import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def create_email( expo_name, your_name, your_company, your_position,your_website):
    email_subject = f"Access Detailed Attendees List from {expo_name}"

    email_body = f"""\
    <html>
      <head>
        <style>
          /* Add CSS styles for improved layout */
          body {{
            font-family: 'Arial', sans-serif;
            background-color: #f7f7f7;
            margin: 0;
            padding: 0;
          }}
          .container {{
            width: 80%;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
          }}
          .header {{
            text-align: center;
            font-family: 'Verdana', sans-serif;
            font-size: 28px;
            font-weight: bold;
            color: #333333;
            padding: 20px 0;
          }}
          .content {{
            color: #444444;
            font-size: 16px;
            padding-bottom: 20px;
          }}
          .content ul {{
            list-style-type: disc;
            margin-left: 20px;
          }}
          .signature {{
            font-size: 14px;
            color: #666666;
            margin-top: 20px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            Access Detailed Attendees List
          </div>
          <div class="content">
            <p>Hello,</p>
            <p>I hope this message finds you well. My name is {your_name} from {your_company}, and I wanted to introduce you to an opportunity that could significantly benefit your's Company.</p>
            <p><strong>We specialize in curating comprehensive attendee lists from prominent Expos and Tradeshows like {expo_name}.</strong> Our meticulously compiled lists cover a diverse array of industry professionals, influencers, and decision-makers who attended the event.</p>
            <p>By leveraging our Attendees List, your team can:</p>
            <ul style="list-style-type: disc; margin-left: 20px;">
              <li>Gain insights into key players present at the event</li>
              <li>Identify potential leads and valuable connections</li>
              <li>Develop targeted marketing and outreach strategies</li>
              <li>Enhance your business development efforts</li>
              <li>And more...</li>
            </ul>
            <p>We understand the importance of having access to quality leads and contacts to drive growth and expand your network. Our goal is to provide you with the resources that empower your team to excel.</p>
            <p>Would you be available for a brief call this week to discuss how our Attendees List from {expo_name} can align with your objectives and support your initiatives at yours's Company?</p>
            <p>Looking forward to the opportunity to connect and explore potential synergies between our offerings and your needs.</p>
            <p>Thank you for your time, and I eagerly await your response.</p>
          </div>
          <div class="signature">
            <p><strong>Best Regards,</strong><br>{your_name}<br>{your_position}<br>{your_company}<br>{your_website}</p>
          </div>
        </div>
      </body>
    </html>
    """

    return email_subject, email_body


def send_email(sender_email, sender_password, recipient_email, subject, body):
    # Email content setup
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