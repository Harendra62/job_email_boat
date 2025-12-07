import os
import sys
import csv
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


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


def send_mail(to, subject, message, email_user, email_pass, attachment_path=None):
    # Create multipart message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = email_user
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

    print(f"\n{'='*60}")
    print("EMAIL DETAILS:")
    print(f"{'='*60}")
    print(f"From: {email_user}")
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    if attachment_path:
        print(f"Attachment: {attachment_path if os.path.exists(attachment_path) else 'Not found'}")
    print(f"{'='*60}\n")

    try:
        # Using Gmail SMTP – you can change host/port as needed
        print("Connecting to SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("Starting TLS...")
            server.starttls()
            print("Logging in...")
            server.login(email_user, email_pass)
            print("Sending email...")
            server.sendmail(email_user, to, msg.as_string())
        
        print(f"✅ SUCCESS: Email sent to {to} with subject '{subject}'")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ ERROR: Authentication failed. Please check your email and password.")
        print(f"   For Gmail, make sure you're using an App Password, not your regular password.")
        print(f"   Error details: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ ERROR: SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return False


def main():
    print("="*60)
    print("DAILY JOB EMAIL BOT - TEST MODE")
    print("="*60)
    
    # Check if environment variables are set
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    
    # If not set, prompt for credentials
    if not email_user:
        email_user = input("\nEnter your email (Gmail): ").strip()
        if not email_user:
            print("❌ Email is required. Exiting.")
            sys.exit(1)
    
    if not email_pass:
        email_pass = input("Enter your email password (Gmail App Password): ").strip()
        if not email_pass:
            print("❌ Password is required. Exiting.")
            sys.exit(1)
    
    # Set environment variables for config.py compatibility
    os.environ["EMAIL_USER"] = email_user
    os.environ["EMAIL_PASS"] = email_pass
    
    try:
        print("\nLoading companies from CSV...")
        companies = load_companies()
        print(f"✅ Loaded {len(companies)} company(ies)")
        
        # Display all available emails from CSV
        print("\n" + "="*60)
        print("AVAILABLE EMAILS FROM CSV:")
        print("="*60)
        for i, company in enumerate(companies, 1):
            print(f"{i}. {company.get('email', 'N/A')} - {company.get('subject', 'N/A')}")
        
        # Let user select which email to test
        print("\n" + "="*60)
        print("SELECT EMAIL TO TEST")
        print("="*60)
        while True:
            try:
                choice = input(f"\nEnter the number (1-{len(companies)}) to select email, or press Enter for today's default: ").strip()
                if not choice:
                    # Use default (today's company)
                    print("\nUsing today's default company...")
                    company = pick_company_for_today(companies)
                    break
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(companies):
                        company = companies[choice_num - 1]
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(companies)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        print(f"✅ Selected company: {company.get('email', 'N/A')}")
        
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
        
        # If still no resume found, ask user
        if not resume_path or not os.path.exists(resume_path):
            print(f"\n⚠️  No resume file found automatically.")
            resume_input = input(f"Enter resume file path (or press Enter to skip attachment): ").strip()
            if resume_input:
                if os.path.exists(resume_input):
                    resume_path = os.path.abspath(resume_input)
                else:
                    print(f"⚠️  Warning: File '{resume_input}' not found. Continuing without attachment.")
                    resume_path = None
            else:
                resume_path = None
        else:
            resume_path = os.path.abspath(resume_path)
            print(f"✅ Using resume: {resume_path}")
        
        print("\n" + "="*60)
        print("READY TO SEND EMAIL")
        print("="*60)
        confirm = input(f"\nSend email to {email}? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            success = send_mail(email, subject, message, email_user, email_pass, resume_path)
            if success:
                print("\n✅ Test completed successfully!")
            else:
                print("\n❌ Test failed. Please check the error messages above.")
        else:
            print("\n❌ Email sending cancelled.")
            
    except FileNotFoundError:
        print(f"❌ ERROR: companies.csv file not found in data/ directory")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

