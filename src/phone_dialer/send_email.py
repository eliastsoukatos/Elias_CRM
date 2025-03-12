import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_project_email(recipient_email, company, recipient_name):
    # Outlook SMTP Settings (GDS account)
    SMTP_SERVER = "smtp-mail.outlook.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "elias.tsoukatos@gdsgroup.com"
    SENDER_PASSWORD = "Gds2024!"  # Replace with your actual app password if required
    SENDER_NAME = "Elias Tsoukatos"  # Display name for the sender

    subject = "AI Project Opportunity with Bank of America | Gen AI Automation"
    
    # Use only the first name from recipient_name
    first_name = recipient_name.split()[0] if recipient_name else recipient_name

    # HTML body for a professional look and feel
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Hi {first_name},</p>
        <p>
          I wanted to reach out regarding a new initiative we're working on with Bank of America.
          Their Director of Global Markets and Risk Technology is currently seeking vendors to help automate 
          the creation of financial pitchbooks through generative AI, and our role is to identify suitable partners.
        </p>
        <p>The project involves leveraging advanced technologies such as:</p>
        <ul>
          <li>Custom-trained large language models (LLMs)</li>
          <li>Integration with financial platforms (Bloomberg, FactSet)</li>
          <li>API-driven data aggregation and automated valuation modeling</li>
          <li>Microservices architecture deployed on private cloud platforms</li>
        </ul>
        <p>
          I was checking out <strong>{company}</strong> and I really liked your website.
          If this aligns with your capabilities, I’d love to schedule a brief call to discuss potential collaboration.
          You can easily schedule a meeting using the following link:
        </p>
        <p>
          https://calendly.com/elias-tsoukatos-gdsgroup/30min
        </p>
        <p>
          For context, GDS (gdsgroup.com) is a strategic vendor evaluation firm.
          We help Fortune 2000 C-suite executives identify, assess, and engage the right vendors and technology partners for their key initiatives.
        </p>
        <p>
          Additionally, we offer pipeline acceleration services and are currently sourcing vendors for over 16,000 active projects,
          directly engaging with more than 5,000 C-suite executives from Fortune 2000 companies.
        </p>
        <p>
          If this aligns with your expertise, I'd be happy to discuss this project in more detail or explore other relevant initiatives
          we're currently sourcing vendors for.
        </p>
        <p>Looking forward to our conversation!</p>
        <br>
        <p>Best regards,</p>
        <p>
          <strong>{SENDER_NAME}</strong><br>
          Vendor Acquisition Manager<br>
          GDS Group<br>
          225 Liberty St<br>
          New York, USA<br>
          <a href="mailto:elias.tsoukatos@gdsgroup.com" style="color: #1a73e8; text-decoration: none;">
            elias.tsoukatos@gdsgroup.com</a><br>
          +1 910-421-9278<br>
          <a href="http://gdsgroup.com" style="color: #1a73e8; text-decoration: none;">
            gdsgroup.com</a>
        </p>
      </body>
    </html>
    """

    # Create a MIME message with HTML content
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = recipient_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        # Connect to the SMTP server, start TLS, and login
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {first_name} ({recipient_email})")
    except Exception as e:
        print(f"❌ Failed to send email to {first_name} ({recipient_email}): {e}")

# Example usage:
if __name__ == "__main__":
    # Replace these with the actual recipient details
    recipient = "etsoukatos@aimonkey.io"
    company = "aiMonkey"
    recipient_name = "Elias Semeney"
    send_project_email(recipient, company, recipient_name)
