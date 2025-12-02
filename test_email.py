import os
import sys
import csv
from datetime import date
import smtplib
from email.mime.text import MIMEText


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


def send_mail(to, subject, message, email_user, email_pass):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = to

    print(f"\n{'='*60}")
    print("EMAIL DETAILS:")
    print(f"{'='*60}")
    print(f"From: {email_user}")
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
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
        
        print("\nSelecting company for today...")
        company = pick_company_for_today(companies)
        print(f"✅ Selected company: {company.get('email', 'N/A')}")
        
        email = company["email"]
        subject = company["subject"]
        message = company["message"]
        
        print("\n" + "="*60)
        print("READY TO SEND EMAIL")
        print("="*60)
        confirm = input(f"\nSend email to {email}? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            success = send_mail(email, subject, message, email_user, email_pass)
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

