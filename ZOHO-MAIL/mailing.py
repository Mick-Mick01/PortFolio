import smtplib
from email.mime.text import MIMEText

smtp_host = 'smtp.zoho.in'
smtp_port = 465  # Use 465 for SSL

sender = 'devcrishkha@zohomail.in'
recipient = 'devkha8721@gmail.com'
app_password = '0ijUjTq3X5Mw' # no space after U and 3


msg = MIMEText("Hi", 'plain', 'utf-8')
msg['Subject'] = "Test email from Python"
msg['From'] = sender
msg['To'] = recipient

with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
    server.login(sender, app_password)
    server.send_message(msg)

print("Email sent successfully!")
