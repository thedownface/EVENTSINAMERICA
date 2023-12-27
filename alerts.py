import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

recipient_email=''
sender_email='alerts@infonauticsdatasolutions.com'
sender_password=''



def alert_email(show_name):

    subject=f'ALERT FOR {show_name}'
    body=f'Emails Succesfully Sent for {show_name}'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))

    # Connect to SMTP server (in this case, Gmail's SMTP server)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to Gmail
    server.login(sender_email, sender_password)

    # Send the email
    server.sendmail(sender_email, recipient_email, message.as_string())

    # Close the connection
    server.quit()