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
        I'm working directly with Bank of America’s Director of Global Markets and Risk Technology, who needs a vendor to automate financial pitchbook creation using generative AI.
        </p>

        <p>The project focuses on:</p>
        <ul>
          <li>Custom-trained large language models</li>
          <li>Integration with platforms like Bloomberg and FactSet</li>
          <li>API-driven data aggregation and automated valuation</li>
          <li>Microservices on a private cloud</li>
        </ul>

        <p>
          I was impressed by {company}’s website and believe you could be a great fit.
          If you’re interested, please schedule a brief call via my Calendly:
        </p>
        <p>
          <a
            href="https://calendly.com/elias-tsoukatos-gdsgroup/30min"
            style="color: #1a73e8; text-decoration: none;"
          >
            Schedule a Meeting
          </a>
        </p>

        <p>
          For context, GDS Group is a strategic vendor evaluation firm that helps
          Fortune 2000 executives find the right technology partners.
        </p>

        <p>Looking forward to connecting!</p>

        <br>

        <p>Best regards,</p>

        <!-- Signature Table -->
        <table style="border: none; padding: 0; margin: 0;">
          <tr>
            <!-- GDS Logo -->
            <td style="vertical-align: top;">
              <img
                src="https://ci3.googleusercontent.com/mail-img-att/AGAZnRogHKO9SWtr_3VvrXKyQ6sLpvX4DBUvJP-BaF8G4K4RURD-5rPyYAkFPytCGp9Z93QTrNDJU5t-ujBvpr8986qX4rWEbw1bk5Dv5b0ilbr9z--xFfT1kpmBSuyREBgOmR7jdOgsPTz-Z14YFhmNlz7tkKMH12NvFmu4b5hf8-zcVENzXckjBjYt8uuJrzTf0W29pLOgBMT551W4d1so1RV7s5ifUn1hvleIw_hUgIfZSagck4MN1YWhenoeS9HR1yEQKqiqvSKPfM9_2WhUAjXdylZaOmvsr_MSe1FCR0XumKSxBDm9xxqRRaBSclO1BzOpa07aqzEpZwckcURip5XYZt04yqEk50Db37b0ZUJC3YQPNqRd3GS3mzgCAGzwjAW3STcROwsNSqKptXyZMYuMWWk3cO_u-X0lxFa8FKUg2mzl0tVW-ewaXWzUoBtxqRfL60AwJ8u6CQ4vS6uUedYVX48jGBJrSt4y8dU5-nXVBIM0CRR1zhsHvVRlphBDGKrHI-fc9aesvVM_Tpj_anMXARHtmTbD9etnPCkeYecQVRbrvRMv3OwR2Q_SvA3Xu1vfUEjWVQjl1--oldvyKuhyd6gAiPJ1t1pt31xi2qEa_W2qA_-QzYKH3-rMeTvEShgzXKyHOeE63epJeavEuXnMwLnZ6lBiom743ZlaHAIpDq-ZoPr9nVZBjXeRVQcsqgwr78dqIIuzHhpYQvNrX7x1Ig3fOag61OSpd7dE3O7pp2grAOixPgsH-Gh7RY1QTzIywSHc_VrBmzcP64xBzyq3tx85OZm4r3o0D-MXWuhhHjA8_4Q1pJ4ZWagsidW8dIFE9fCNs4pFTT87wnSUTo2Clhk5sAGfpjhYhkF1FDjG0te2fSVem129I5p8LISig9ddoa2tfNH57Oj0ZrnPx15loN9QPvEkwlJ3dSMCyKHg8AMWL_8P0aNTkGSv3_WvkGz8tvGlw2VJfaM8iP2jyeqR8FUc8l-7wDRzyIaCJmKFF73lvqdcwLCTT6eIDlnIDDI_892g6Nh7_HNt6kGMeZVObatZ=s0-l75-ft"
                alt="GDS Logo"
                style="width: 80px; height: auto;"
              />
            </td>

            <!-- Contact Info & LinkedIn Icon -->
            <td style="vertical-align: top; padding-left: 10px;">
              <p style="margin: 0;">
                <strong>{SENDER_NAME}</strong><br>
                Vendor Acquisition Manager<br>
                GDS Group<br>
                225 Liberty St<br>
                New York, USA<br>
                <a
                  href="mailto:elias.tsoukatos@gdsgroup.com"
                  style="color: #1a73e8; text-decoration: none;"
                >
                  elias.tsoukatos@gdsgroup.com
                </a><br>
                +1 910-421-9278<br>
                <a
                  href="http://gdsgroup.com"
                  style="color: #1a73e8; text-decoration: none;"
                >
                  gdsgroup.com
                </a>
              </p>
              <p style="margin: 5px 0 0 0;">
                <a href="https://www.linkedin.com/in/eliastsoukatos/" target="_blank">
                  <img
                    src="https://ci3.googleusercontent.com/mail-img-att/AGAZnRoS833SpzdPkKO4KVS6gawT5-FgWfOLwVN_P9h-7BSShlGutKJ-puJJACDVLrDdAXYrxR5NY04IU7OG2r8bw0ihT9kHxKqwjdgmOBOWmGUQ3R6zgUuRsSqQTAk8HHOvQzz_g117mvWVl5r_g_pLOarYRWT5UzX8DOlH7yEwKGJ4Vw1N3KHykg_cMtdT2rCZfR0Uuy9neEO3vIlby6K6lC70nrIBUE_mysSqay1SSaKDYI_LFgmuBjIeJMxi3ICDBxBwYSHaYqdetHkGv1Ftm209G3jtyyBX8_Y2SFvzezBdMRvXAqzHBoxlL4NrBbdmTDFcPxX2ZGdNYyZ3HuSBT7IzxomqS_muAEWcGYeXJhBZWHZQ3O4YKaXiJHonPKvmLuSDarjvfY4ZuYBHm1AYCW5aAlXCsPWzdNvsFQ5CGFZLC8upoDlHdpgDb7lS0DxM7Ikkp2BmrCVkiuOSrDAJ_Pturg302mqBa2-VMvTrBhCxN2gdAVMAKbxoJTnaWFgAVlIWUg5D5tT9UaA7TvBki3EfXltb59oZLvCrcqEQWF6eiRkQu-pOjFCw4AK7-tQT9j3jKVqd6pubc7XDPy5QU1lOSqvL7m_lF8r03JDtRYls_0yJg9JRp32xhpSG7Dr11RESkKlp-zzESJYjBfzopyND0z5bg-AD46nt4pGHhBJcVeTz_DkdGIBrGvouLUK1uQnwcUm-3UQmtNMbBbJZzRDQy77kd1YgdyyCXXNl5oq2qrII8D8yTFXwodNsqG5PjXBZfL12BkVz-O-l3CXieahgt-s_YG5Zti--nu2ZrgwTIyPtJ4Pj-DF2re1lprAatjQghRywPwe94ffLfxWU7knVRd70BPXAOgUv1wMChelfgTktcwH0WhpZbniOYaa9qWAfQXUecdy_ZaEUmcp1Okc2pWyF7dhA731NxLLLoaP6sPyvc2TrlUNOp1-E41WCAH4kgGQ6ZKE150Ifcbp6h4RP7oONMUaXT9Xy68zFinawJOMeGKzYe3XoTjllX-7UvD3uBZvLjzINRRDPWLxwheUfWocdQA=s0-l75-ft"
                    alt="LinkedIn"
                    style="width: 24px; height: auto;"
                  />
                </a>
              </p>
            </td>
          </tr>
        </table>
        <!-- End Signature -->

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
    recipient = "elias.tsoukatos@gdsgroup.com"
    company = "GDS"
    recipient_name = "Elias"
    send_project_email(recipient, company, recipient_name)
