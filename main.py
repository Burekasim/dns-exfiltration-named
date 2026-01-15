import re
import boto3
import time
import os
from twilio.rest import Client
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
LOG_FILE = "/var/log/named_queries.log"  # Change this path to your DNS log file
AWS_REGION = "us-east-1"  # Change if needed
CACHE_DIR = "/tmp/dns_sms_cache"
CACHE_TTL_SECONDS = 30

# Initialize SNS client
sns = boto3.client("sns", region_name=AWS_REGION)

def call_with_message(to_number: str, _message: str):
    if was_recently_sent(_message):
        #print(f"⏱ Skipping duplicate message: {message}")
        return
    """
    Make an outbound call and have Twilio say 'I want to tell you a secret' in Hebrew.
    """
    account_sid = '##twilio_account_sid##'
    auth_token = '##twilio_auth_token##'
    twilio_client = Client(account_sid, auth_token)
    msg_parsed = _message.replace('-', ' ')
    call = twilio_client.calls.create(
        to=to_number,
        from_='+97233820315',
        twiml=f'<Response><Pause /><Say voice="Google.he-IL-Wavenet-C" language="he-IL">היי, רציתי לספר לך סוד: </Say><Say>{msg_parsed}</Say><Pause /></Response>'
    )

    print("Call SID:", call.sid)
    return True


def extract_query(line):
    match = re.search(r"\(([^)]+)\): query:", line)
    return match.group(1).lower() if match else None


def normalize_israeli_number(number):
    """
    Converts Israeli local mobile number (e.g., 0501234567) to international format (+972501234567).
    """
    # Remove non-digits
    digits = re.sub(r'\D', '', number)

    # Handle numbers starting with 0
    if digits.startswith('0') and len(digits) == 10:
        # Replace leading 0 with +972
        return '+972' + digits[1:]

    # Already formatted as +972 or invalid
    return number

def get_cache_file_path(key):
    safe_key = re.sub(r'\W+', '_', key)
    return os.path.join(CACHE_DIR, safe_key + ".txt")

def was_recently_sent(key):
    cache_file = get_cache_file_path(key)
    if os.path.exists(cache_file):
        modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - modified_time < timedelta(seconds=CACHE_TTL_SECONDS):
            return True
    return False

def mark_as_sent(key):
    cache_file = get_cache_file_path(key)
    with open(cache_file, "w") as f:
        f.write(str(datetime.now()))

def extract_octet(subdomain, oc):
    parts = subdomain.split(".")
    if parts:
        try:
            return parts[oc]
        except Exception as e:
            return None
    return None

def send_sms(message, phone):
    if was_recently_sent(message):
        #print(f"Skipping duplicate message: {message}")
        return
    try:
        response = sns.publish(
            PhoneNumber=phone,
            Message=message
        )
        print(f"SMS sent: {message} (MessageId: {response['MessageId']})")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

def process_line(line):
    if 'avi.co.il' not in line.lower():
        print(f'query is not for avi.co.il, ignoring')
        return ''
    query = extract_query(line)
    if query:
        first_octet = extract_octet(query, 0)
        phone_number = normalize_israeli_number(extract_octet(query, 1))
        action = extract_octet(query, 2)
        if not phone_number.replace('+972', '').isdigit():
            print(phone_number)
            print('dns query is not in format, second octact is not phone number')
            return ''
        print(f'query: {query}')
        print(f'query: {first_octet}')
        if first_octet:
            if action == 'a':
                msg = f"Message: {first_octet}"
                send_sms(msg, phone_number)
            if action == 'b':
                call_with_message(phone_number, first_octet)
            mark_as_sent(first_octet)
        else:
            print("No numeric octet found.")
    else:
        print("No query found.")

def tail_log_file(path):
    print(f"Monitoring: {path}")
    with open(path, "r") as file:
        file.seek(0, os.SEEK_END)  # Go to the end of file
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.5)
                continue
            process_line(line.strip())

if __name__ == "__main__":
    tail_log_file(LOG_FILE)
