import csv
import os
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import EMAIL, PASSWORD


def load_companies(csv_path="data/companies.csv"):
    companies = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row)
    return companies


def pick_company_for_today(companies):
    if not companies:
        raise ValueError("No companies found in companies.csv")

    today = date.today()
    day_number = today.toordinal()  # unique number for each date
    index = day_number % len(companies)
    return companies[index]


def send_mail(to, subject, message, attachment_path=None):
    # Create multipart message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to

    # Add message body
    msg.attach(MIMEText(message, "plain"))

    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        try:
            filename = os.path.basename(attachment_path)
            # Determine MIME type based on file extension
            if filename.lower().endswith('.pdf'):
                maintype, subtype = 'application', 'pdf'
            elif filename.lower().endswith(('.doc', '.docx')):
                maintype, subtype = 'application', 'msword'
                if filename.lower().endswith('.docx'):
                    subtype = 'vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                maintype, subtype = 'application', 'octet-stream'
            
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase(maintype, subtype)
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"',
            )
            msg.attach(part)
            print(f"✅ Attachment added: {filename} ({maintype}/{subtype})")
        except Exception as e:
            print(f"⚠️  Warning: Could not attach file {attachment_path}: {e}")
            import traceback
            traceback.print_exc()

    # Using Gmail SMTP – you can change host/port as needed
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to, msg.as_string())

    print(f"Email sent to {to} with subject '{subject}'")


def main():
    companies = load_companies()
    company = pick_company_for_today(companies)

    email = company["email"]
    subject = company["subject"]
    message = company["message"]
    
    # Check for resume attachment path in CSV or use default
    resume_path = company.get("resume_path", "").strip() if company.get("resume_path") else ""
    if resume_path:
        # Convert to absolute path if relative
        if not os.path.isabs(resume_path):
            resume_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), resume_path)
        if not os.path.exists(resume_path):
            print(f"⚠️  Warning: Resume path from CSV not found: {resume_path}")
            resume_path = ""
    
    if not resume_path:
        # Try common resume file names in root and data folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        common_resume_names = [
            "resume.pdf", "Resume.pdf", "resume.docx", "Resume.docx", "CV.pdf", "cv.pdf",
            "data/resume.pdf", "data/Resume.pdf", "data/resume.docx", "data/Resume.docx", 
            "data/CV.pdf", "data/cv.pdf", "data/Harendra_word_resume.pdf"
        ]
        for resume_name in common_resume_names:
            full_path = os.path.join(base_dir, resume_name) if not os.path.isabs(resume_name) else resume_name
            if os.path.exists(full_path):
                resume_path = full_path
                print(f"✅ Found resume: {resume_path}")
                break

    if resume_path and os.path.exists(resume_path):
        resume_path = os.path.abspath(resume_path)
        print(f"✅ Using resume: {resume_path}")
    else:
        resume_path = None
        print("⚠️  No resume file found. Sending email without attachment.")

    send_mail(email, subject, message, resume_path)


if __name__ == "__main__":
    main()
