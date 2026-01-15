This script was used at the AWS IL Community day during a demo.<br/>

This script listens to named (BIND) server (DNS) queries,<br/>
Make sure you have the following setting in your /etc/bind.conf: <br/>
<img width="574" height="440" alt="CleanShot 2026-01-16 at 01 16 10@2x" src="https://github.com/user-attachments/assets/732f77a3-40cf-4d79-ba19-5b47e91fe95e" />

You will need the following:<br/>
1. Twilio account for Phone calls with a phone number that can call perform outbound calls.
2. AWS account for SMS. (make sure you increase the [$1 SMS limit](https://docs.aws.amazon.com/general/latest/gr/sns.html#:~:text=Account%20spend%20threshold%20for%20SMS)
3. A domain with DNS delegating to the instance IP that runs this script.

How does it work?<br/>
Once everything is configured, the script monitors the BIND query log, if there is a query in the following format: <br/>
1. secret-message.0501234567.a.avi.co.il - An SMS with the text "secret-message" will be sent to 0501234567.
2. secret-message.0501234567.a.avi.co.il - A phone call will be made to 0501234567 with a female voice saying in Hebrew, "Hi, I want to tell you a secret, secret-message".


My setup was:<br/>
avi.co.il hosted on Route53<br/>
b.avi.co.il and a.avi.co.il are delegated DNS yoyo.yeah.co.il. (one of the domains that I own)<br/>
yoyo.yeah.co.il A record leads to an EC2 instance with an Elastic IP.<br/>




