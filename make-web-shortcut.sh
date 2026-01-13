#!/bin/bash

# ==========================================
# Fedora Web App Installer (Auto-Icon Version)
# ==========================================
clear

# 1. GATHER INPUTS
read -p "Enter App Name (e.g. Marquee Magic): " APP_NAME
#APP_NAME="My WebApp"
read -p "Enter URL (e.g. https://example.com): " APP_URL
#APP_URL="https://wheelhouser.com"
read -p "Enter path to Icon (press Enter for ./icon.svg): " ICON_SOURCE
#ICON_SOURCE=./icon.svg

# 2. LOGIC: SET DEFAULT ICON
# If user hit Enter, assume current directory icon.svg
if [[ -z "$ICON_SOURCE" ]]; then
    ICON_SOURCE="$(pwd)/icon.svg"
    echo "No icon specified. Checking for default: $ICON_SOURCE"
fi

# Clean up input for filenames (removes spaces/symbols for the file system)
SAFE_NAME=$(echo "$APP_NAME" | tr -dc '[:alnum:]\n\r' | tr '[:upper:]' '[:lower:]')
DESKTOP_FILENAME="${SAFE_NAME}.desktop"

# Define System Paths
# Using 'hicolor/scalable/apps' is the most reliable way for Fedora/GNOME to index icons
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
APP_DIR="$HOME/.local/share/applications"

# Create directories if missing
mkdir -p "$ICON_DIR"
mkdir -p "$APP_DIR"

# 3. HANDLE ICON INSTALLATION
if [[ -f "$ICON_SOURCE" ]]; then
    EXT="${ICON_SOURCE##*.}"
    ICON_DEST="${ICON_DIR}/${SAFE_NAME}.${EXT}"
    
    # Copy file to system icon folder
    cp "$ICON_SOURCE" "$ICON_DEST"
    echo "Icon found and installed to: $ICON_DEST"
    
    # Use the absolute path in the desktop file to be safe
    ICON_SETTING="$ICON_DEST"
else
    echo "WARNING: Could not find icon at '$ICON_SOURCE'."
    echo "Falling back to generic web browser icon."
    ICON_SETTING="web-browser"
fi

# 4. GENERATE & INSTALL DESKTOP FILE
TARGET_FILE="$APP_DIR/$DESKTOP_FILENAME"

echo "Creating launcher at $TARGET_FILE..."

# Use this command to make a general web open
#Exec=xdg-open $APP_URL

cat <<EOF > "$TARGET_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Launch $APP_NAME
Exec=firefox --kiosk $APP_URL
Icon=$ICON_SETTING
Terminal=false
StartupNotify=true
Categories=Network;WebBrowser;
EOF

# Make executable
chmod +x "$TARGET_FILE"

# Copy a backup to current directory for your reference
cp "$TARGET_FILE" "./$DESKTOP_FILENAME"

# 5. FORCE CACHE UPDATES
# This is critical for the icon to appear immediately in the Dock
echo "Refreshing GNOME databases..."
update-desktop-database "$APP_DIR"
touch "$APP_DIR"
gtk-update-icon-cache --ignore-theme-index "$HOME/.local/share/icons" 2>/dev/null

echo "Done. If the icon doesn't appear immediately, press Alt+F2, type 'r', and hit Enter."
