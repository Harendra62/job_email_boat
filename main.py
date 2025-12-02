import csv
from datetime import date
import smtplib
from email.mime.text import MIMEText
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


def send_mail(to, subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to

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

    send_mail(email, subject, message)


if __name__ == "__main__":
    main()
