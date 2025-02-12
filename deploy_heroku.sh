#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display a message
function echo_message() {
  echo "=====> $1"
}

# Variables
APP_NAME="progress-rpg-dev"  # Replace with your Heroku app name
BRANCH_NAME="main"          # Replace with your Git branch name (e.g., main/master)

# Step 1: Enable maintenance mode
echo_message "Enabling maintenance mode"
heroku maintenance:on --app $APP_NAME

# Step 2: Check for changes and commit if any
echo_message "Checking for changes to commit"
if git diff-index --quiet HEAD --; then
    echo_message "No changes to commit, skipping commit step."
else
  echo_message "Staging and committing changes"
  git add .
  read -p "Enter commit message: " commit_message
  git commit -m "$commit_message"
fi

# Step 3: Push to Heroku
echo_message "Pushing to Heroku"
git push heroku $BRANCH_NAME

# Step 4: Run database migrations
echo_message "Running database migrations"
heroku run python manage.py migrate --app $APP_NAME

# Step 5: Collect static files (for Django projects)
echo_message "Collecting static files"
heroku run python manage.py collectstatic --app $APP_NAME

# Step 6: Disable maintenance mode
echo_message "Disabling maintenance mode"
heroku maintenance:off --app $APP_NAME

# Step 7: Check logs
echo_message "Deployment complete. Checking logs..."
heroku logs --tail --app $APP_NAME
