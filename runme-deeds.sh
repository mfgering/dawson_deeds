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
    echo "$message" | mail \
        -s "$EMAIL_SUBJECT" \
        -r "$EMAIL_FROM" \
        -S smtp="smtp://$SMTP_SERVER:$SMTP_PORT" \
        -S smtp-use-starttls \
        -S smtp-auth=login \
        -S smtp-auth-user="$EMAIL_FROM" \
        -S smtp-auth-password="$EMAIL_PASSWORD" \
        "$EMAIL_TO"
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
    CHANGES_DETECTED=true
fi

if [ "$CYPRESS_INITIAL" != "$CYPRESS_AFTER" ]; then
    EMAIL_MESSAGE+="Cypress deeds report has been updated.\n"
    CHANGES_DETECTED=true
fi

if [ "$CHANGES_DETECTED" = true ]; then
    echo "Changes detected, sending email..."
    send_email "$EMAIL_MESSAGE"
    
    echo "Commiting changes..."
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