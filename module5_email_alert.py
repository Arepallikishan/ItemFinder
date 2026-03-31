import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔐 YOUR GMAIL CREDENTIALS (use App Password, not normal password)
SENDER_EMAIL = "lostfounder22@gmail.com"
APP_PASSWORD = "mllm xgog pbhq wagv"


def send_match_email(receiver_email, item_name, similarity):
    try:
        subject = "🎯 Lost Item Match Found!"
        body = f"""
Hello,

Good news! A matching item for your lost item "{item_name}" has been found.

Match Similarity: {similarity:.2f}%

Please login to the Lost & Found system to verify and claim your item.

Thank you,
Lost & Found AI System
"""

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"📧 Match email sent to: {receiver_email}")

    except Exception as e:
        print("Email sending failed:", e)


def send_thank_you_email(finder_email):
    try:
        subject = "🙏 Thank You for Your Genuine Support!"
        body = """
Hello,

Thank you for submitting a found item to our Lost & Found system.

Your honesty and genuine character are highly appreciated.
You helped someone recover their valuable item.

Best Regards,
Lost & Found AI Team
"""

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = finder_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"💌 Thank you email sent to finder: {finder_email}")

    except Exception as e:
        print("Thank you email failed:", e)