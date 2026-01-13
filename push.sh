#!/bin/bash

# ==========================================
# Web App Manager - GitHub Push Utility
# ==========================================

# Default commit message if none provided
MESSAGE="${1:-Update webapp-manager assets and code}"

echo "Preparing to push updates to GitHub..."

# Ensure we are in a git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository. Please run this from the project root."
    exit 1
fi

# Stage all changes
echo "Staging all changes..."
git add .

# Check if there are changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    echo "Committing with message: '$MESSAGE'..."
    git commit -m "$MESSAGE"
fi

# Push to the current branch
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "Successfully pushed to GitHub!"
else
    echo "Error: Push failed. Check your internet connection or git configuration."
    exit 1
fi
