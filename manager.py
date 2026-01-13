#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This script generates icon files for various platforms (Linux, Windows, macOS, etc.)
# from a source image. It supports PNG, JPG, SVG, and other formats.
# It uses the Pillow library for image processing and PySide6 for the GUI.
#
#
# Copyright (C) 2026 steve.rock@wheelhouser.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# --- Setup Instructions ---
# Active the venv on linux/macOS:
# python -m venv .venv
# source .venv/bin/activate
# pip install --upgrade pip
#
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# pip install -r requirements.txt
# pip install --force-reinstall -r requirements.txt
#
#===========================================================================================

import os
import subprocess
import re

ICON_DIR = os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps")
APP_DIR = os.path.expanduser("~/.local/share/applications")
PROFILE_BASE_DIR = os.path.expanduser("~/.local/share/webapp-launcher/profiles")

def get_installed_apps():
    """Returns a list of web apps created by this tool."""
    apps = []
    if not os.path.exists(APP_DIR):
        return apps

    for filename in os.listdir(APP_DIR):
        if filename.endswith(".desktop"):
            filepath = os.path.join(APP_DIR, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                # Check if it's one of our apps (using firefox --kiosk)
                if "firefox" in content and "--kiosk" in content:
                    name_match = re.search(r"^Name=(.*)$", content, re.MULTILINE)
                    # Match URL at the end of Exec line
                    url_match = re.search(r"Exec=.* --kiosk (.*)$", content, re.MULTILINE)
                    icon_match = re.search(r"^Icon=(.*)$", content, re.MULTILINE)
                    
                    apps.append({
                        "id": filename.replace(".desktop", ""),
                        "name": name_match.group(1) if name_match else filename,
                        "url": url_match.group(1) if url_match else "",
                        "icon": icon_match.group(1) if icon_match else "",
                        "filepath": filepath
                    })
    return apps

def install_app(name, url, icon_source):
    """Installs a new web app."""
    os.makedirs(ICON_DIR, exist_ok=True)
    os.makedirs(APP_DIR, exist_ok=True)

    safe_name = "".join(c for c in name if c.isalnum()).lower()
    profile_dir = os.path.join(PROFILE_BASE_DIR, safe_name)
    os.makedirs(profile_dir, exist_ok=True)

    desktop_filename = f"{safe_name}.desktop"
    
    icon_setting = "web-browser"
    if icon_source and os.path.exists(icon_source):
        ext = os.path.splitext(icon_source)[1]
        icon_dest = os.path.join(ICON_DIR, f"{safe_name}{ext}")
        subprocess.run(["cp", icon_source, icon_dest])
        icon_setting = icon_dest

    target_file = os.path.join(APP_DIR, desktop_filename)
    
    # We use --new-instance and --profile to ensure an isolated window even if Firefox is running
    exec_command = f"firefox --new-instance --profile {profile_dir} --kiosk {url}"

    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Launch {name}
Exec={exec_command}
Icon={icon_setting}
Terminal=false
StartupNotify=true
Categories=Network;WebBrowser;
"""
    with open(target_file, "w") as f:
        f.write(content)
    
    os.chmod(target_file, 0o755)
    refresh_caches()
    return True

def uninstall_app(app_id):
    """Uninstalls a web app by its ID."""
    desktop_path = os.path.join(APP_DIR, f"{app_id}.desktop")
    
    if os.path.exists(desktop_path):
        # Try to find and remove the icon too
        with open(desktop_path, 'r') as f:
            content = f.read()
            icon_match = re.search(r"^Icon=(.*)$", content, re.MULTILINE)
            if icon_match:
                icon_path = icon_match.group(1)
                if icon_path.startswith(ICON_DIR) and os.path.exists(icon_path):
                    os.remove(icon_path)
        
        # Remove profile directory
        profile_dir = os.path.join(PROFILE_BASE_DIR, app_id)
        if os.path.exists(profile_dir):
            subprocess.run(["rm", "-rf", profile_dir])

        os.remove(desktop_path)
        refresh_caches()
        return True
    return False

def refresh_caches():
    """Refreshes the desktop and icon caches."""
    try:
        subprocess.run(["update-desktop-database", APP_DIR], check=False)
        subprocess.run(["touch", APP_DIR], check=False)
        subprocess.run(["gtk-update-icon-cache", "--ignore-theme-index", os.path.expanduser("~/.local/share/icons")], check=False)
    except Exception as e:
        print(f"Error refreshing caches: {e}")
