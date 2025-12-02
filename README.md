# Daily Job Email Bot

An automated email bot that sends daily job application emails to companies from a rotating list. The bot uses a date-based algorithm to select which company to email each day, ensuring a fair rotation through your list.

## Features

- 📧 Automated daily email sending
- 🔄 Fair rotation through company list using date-based selection
- ⏰ Scheduled execution via GitHub Actions
- 🧪 Test mode for verifying email functionality
- 📝 CSV-based company management

## How It Works

The bot selects which company to email based on the current date. It uses a modulo operation on the day number to cycle through your company list, ensuring each company gets contacted in rotation.

## Setup

### Prerequisites

- Python 3.10 or higher
- A Gmail account with App Password enabled
- GitHub account (for automated scheduling)

### Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd daily-job-email-bot
   ```

2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Set up your company list:**
   
   Edit `data/companies.csv` with your companies. The CSV should have the following format:
   ```csv
   email,subject,message
   company1@example.com,Job Application - Your Name,Your application message here.
   company2@example.com,Job Application - Your Name,Your application message here.
   ```

2. **Configure email credentials:**
   
   The bot uses environment variables for email credentials:
   - `EMAIL_USER`: Your Gmail address
   - `EMAIL_PASS`: Your Gmail App Password (not your regular password)

   **Getting a Gmail App Password:**
   1. Go to [Google Account Settings](https://myaccount.google.com/)
   2. Enable 2-Step Verification if not already enabled
   3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
   4. Generate a new app password for "Mail"
   5. Use this 16-character password as `EMAIL_PASS`

## Usage

### Local Testing

Use the test script to verify email sending:

```bash
# Option 1: Set environment variables first
$env:EMAIL_USER = "your-email@gmail.com"
$env:EMAIL_PASS = "your-app-password"
python test_email.py

# Option 2: Run directly (will prompt for credentials)
python test_email.py
```

The test script will:
- Load companies from CSV
- Show which company will be selected for today
- Display email details before sending
- Ask for confirmation before sending
- Provide detailed success/error messages

### Running Manually

```bash
# Set environment variables
$env:EMAIL_USER = "your-email@gmail.com"
$env:EMAIL_PASS = "your-app-password"

# Run the main script
python main.py
```

### Automated Scheduling (GitHub Actions)

The bot is configured to run automatically via GitHub Actions.

1. **Set up GitHub Secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `EMAIL_USER`: Your Gmail address
     - `EMAIL_PASS`: Your Gmail App Password

2. **Schedule:**
   - The workflow is configured to run daily at 10:00 AM IST (4:30 AM UTC)
   - You can also trigger it manually via GitHub Actions → "Daily Job Email" → "Run workflow"

3. **Workflow File:**
   - Located at `.github/workflows/daily_email.yml`
   - You can modify the cron schedule if needed

## Project Structure

```
daily-job-email-bot/
├── .github/
│   └── workflows/
│       └── daily_email.yml      # GitHub Actions workflow
├── data/
│   └── companies.csv            # Company list (email, subject, message)
├── config.py                    # Configuration (reads env variables)
├── main.py                      # Main script
├── test_email.py                # Test script for email verification
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## How Company Selection Works

The bot uses a date-based rotation algorithm:

1. Gets the current date
2. Converts it to an ordinal number (unique for each date)
3. Uses modulo operation to select an index: `index = day_number % number_of_companies`
4. Selects the company at that index

This ensures:
- Each company gets contacted in rotation
- The same company won't be selected on consecutive days (unless you have very few companies)
- Fair distribution over time

## Troubleshooting

### Email Not Sending

1. **Check credentials:**
   - Verify `EMAIL_USER` and `EMAIL_PASS` are set correctly
   - Ensure you're using an App Password, not your regular Gmail password

2. **Test connection:**
   - Run `python test_email.py` to see detailed error messages
   - Check if Gmail SMTP is accessible from your network

3. **Check CSV format:**
   - Ensure `data/companies.csv` exists and has correct format
   - Verify all required columns: `email`, `subject`, `message`

### GitHub Actions Not Running

1. **Check secrets:**
   - Verify `EMAIL_USER` and `EMAIL_PASS` are set in repository secrets
   - Ensure secrets are spelled correctly

2. **Check workflow file:**
   - Verify `.github/workflows/daily_email.yml` exists
   - Check the cron schedule syntax

3. **Check workflow runs:**
   - Go to Actions tab to see workflow execution history
   - Check logs for error messages

## Security Notes

- ⚠️ Never commit your email credentials to the repository
- ✅ Always use environment variables or GitHub Secrets
- ✅ Use Gmail App Passwords instead of your main password
- ✅ Keep your `companies.csv` private if it contains sensitive information

## License

This project is open source and available for personal use.

## Contributing

Feel free to fork this project and customize it for your needs!

