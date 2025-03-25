#!/usr/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | sed 's/#.*//g' | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Validate required environment variables
required_vars=("EMAIL_FROM" "EMAIL_TO" "EMAIL_SUBJECT" "SMTP_SERVER" "SMTP_PORT" "EMAIL_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in .env file"
        exit 1
    fi
done

activate() {
  . .venv/bin/activate
  python3 -V
}

send_email() {
    local message="$1"
    python3 - <<END
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

sender = os.environ['EMAIL_FROM']
receiver = os.environ['EMAIL_TO']
password = os.environ['EMAIL_PASSWORD']
smtp_server = os.environ['SMTP_SERVER']
smtp_port = int(os.environ['SMTP_PORT'])
subject = os.environ['EMAIL_SUBJECT']

message = MIMEMultipart()
message["From"] = sender
message["To"] = receiver
message["Subject"] = subject

body = """$message"""
message.attach(MIMEText(body, "plain"))

try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender, password)
        server.send_message(message)
        print("Email sent successfully")
except Exception as e:
    print(f"Failed to send email: {str(e)}")
    exit(1)
END
}

test() {
    echo "Starting test..."
    send_email "Test email"
    echo "End test"
    exit 0
}

# Store initial modification times
DAWSON_INITIAL=$(stat -c %Y reports/dawson_deeds.csv 2>/dev/null || echo 0)
CYPRESS_INITIAL=$(stat -c %Y reports/cypress/cypress.csv 2>/dev/null || echo 0)

git pull
activate

echo "Running dawson_deeds.py"
python3 dawson_deeds.py

echo "Running cypress_deeds.py"
python3 cypress_deeds.py

# Check for modifications
DAWSON_AFTER=$(stat -c %Y reports/dawson_deeds.csv 2>/dev/null || echo 0)
CYPRESS_AFTER=$(stat -c %Y reports/cypress/cypress.csv 2>/dev/null || echo 0)

CHANGES_DETECTED=false
EMAIL_MESSAGE=""

if [ "$DAWSON_INITIAL" != "$DAWSON_AFTER" ]; then
    EMAIL_MESSAGE+="Dawson deeds report has been updated.\n"
    DAWSON_DIFF=$(git diff reports/dawson.csv)
    EMAIL_MESSAGE+="$DAWSON_DIFF\n"
    CHANGES_DETECTED=true
fi

if [ "$CYPRESS_INITIAL" != "$CYPRESS_AFTER" ]; then
    EMAIL_MESSAGE+="Cypress deeds report has been updated.\n"
    CYPRESS_DIFF=$(git diff reports/cypress/cypress.csv)
    EMAIL_MESSAGE+="$CYPRESS_DIFF\n"
    CHANGES_DETECTED=true
fi

if [ "$CHANGES_DETECTED" = true ]; then
    echo "Changes detected, sending email..."
    send_email "$EMAIL_MESSAGE"
    
    echo "Committing changes..."
    git add reports
    git commit -m 'cron: updated deed reports' 
    git push
else
    echo "No changes detected"
fi

echo "Done"

# Clean up environment variables
for var in "${required_vars[@]}"; do
    unset "$var"
done