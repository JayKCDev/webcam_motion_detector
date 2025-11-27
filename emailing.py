import smtplib, ssl
from PIL import Image
from io import BytesIO
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from main import remove_images
from threading import Thread
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_email(file_path, receiver_email, motion_detected_time):
    email_message = EmailMessage()
    email_message["Subject"] = "CamWatch AI | Motion Detected Alert!"
    email_message.set_content(f"A motion activity has been tracked at {motion_detected_time}. Please review the attached image.")

    with open(file_path, "rb") as file:
        content = file.read()

    image_data = BytesIO(content)
    img = Image.open(image_data)
    image_format = img.format

    email_message.add_attachment(content, maintype="image", subtype=image_format)

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER_EMAIL, SENDER_PASSWORD)
    gmail.sendmail(SENDER_EMAIL, receiver_email, email_message.as_string())
    gmail.quit()
    Thread(target=remove_images, args=(receiver_email,), daemon=True).start()


# if __name__ == "__main__":
#     send_email("images/54.png", "test@example.com")