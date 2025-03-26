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

# Use the first command-line argument as the commit and email subject, if provided
CUSTOM_SUBJECT=${1:-"updated deed reports"}

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
subject = "${CUSTOM_SUBJECT}"

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

git pull
activate

echo "Running dawson_deeds.py"
python3 dawson_deeds.py

echo "Running cypress_deeds.py"
python3 cypress_deeds.py

CHANGES_DETECTED=false
EMAIL_MESSAGE=""
DAWSON_DIFF=$(git diff -U0 reports/dawson.csv)

if [ -n "$DAWSON_DIFF" ]; then
    EMAIL_MESSAGE+="Dawson deeds report has been updated.\n"
    EMAIL_MESSAGE+="------------\n$DAWSON_DIFF\n------------\n"
    CHANGES_DETECTED=true
fi

CYPRESS_DIFF=$(git diff -U0 reports/cypress/cypress.csv)
if [ -n "$CYPRESS_DIFF" ]; then
    EMAIL_MESSAGE+="Cypress deeds report has been updated.\n"
    EMAIL_MESSAGE+="------------\n$CYPRESS_DIFF\n------------\n"
    CHANGES_DETECTED=true
fi

if [ "$CHANGES_DETECTED" = true ]; then
    echo "Changes detected, sending email..."
    send_email "$EMAIL_MESSAGE"
    
    echo "Committing changes..."
    git add reports
    git commit -m "$CUSTOM_SUBJECT" 
    git push
else
    echo "No changes detected"
fi

echo "Done"

# Clean up environment variables
for var in "${required_vars[@]}"; do
    unset "$var"
done