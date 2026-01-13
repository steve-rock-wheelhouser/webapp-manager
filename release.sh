#!/bin/bash

# ==========================================
# Web App Manager - GitHub Release Utility
# ==========================================

VERSION="1.0.0"
PACKAGE_NAME="webapp-manager"
RPM_PATH=$(ls rpmbuild/RPMS/noarch/${PACKAGE_NAME}-${VERSION}-*.rpm 2>/dev/null)

echo "Preparing to create GitHub Release for version $VERSION..."

# 1. Check for RPM
if [ -z "$RPM_PATH" ]; then
    echo "Error: RPM package not found in rpmbuild/RPMS/noarch/."
    echo "Please run ./install.sh first to build the package."
    exit 1
fi

# 2. Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it with: sudo dnf install gh"
    echo "Then login with: gh auth login"
    exit 1
fi

# 3. Check login status
if ! gh auth status &> /dev/null; then
    echo "Error: You are not logged into GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

# 4. Create release and upload asset
echo "Creating release v$VERSION and uploading $(basename "$RPM_PATH")..."

gh release create "v$VERSION" "$RPM_PATH" \
    --title "Release v$VERSION" \
    --notes "Initial RPM release of the Web App Manager (GTK4/Libadwaita)." \
    --latest

if [ $? -eq 0 ]; then
    echo "================================================="
    echo "SUCCESS: Release v$VERSION created on GitHub!"
    echo "================================================="
else
    echo "Error: Failed to create GitHub release."
    exit 1
fi
