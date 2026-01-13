#!/bin/bash

# ==========================================
# Web App Manager - RPM Build Script
# ==========================================

# Set version
VERSION="1.0.0"
PACKAGE_NAME="webapp-manager"

echo "Building RPM for $PACKAGE_NAME version $VERSION..."

# 1. CLEANUP PREVIOUS BUILDS
rm -rf rpmbuild
mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# 2. PREPARE SOURCE TARBALL
echo "Creating source tarball..."
TEMP_DIR="$(mktemp -d)"
mkdir -p "$TEMP_DIR/$PACKAGE_NAME-$VERSION"

# Copy essential files
cp app.py "$TEMP_DIR/$PACKAGE_NAME-$VERSION/"
cp manager.py "$TEMP_DIR/$PACKAGE_NAME-$VERSION/"
cp com.wheelhouser.webapp-manager.desktop "$TEMP_DIR/$PACKAGE_NAME-$VERSION/"
mkdir -p "$TEMP_DIR/$PACKAGE_NAME-$VERSION/assets/icons"
cp assets/icons/com.wheelhouser.webapp-manager.svg "$TEMP_DIR/$PACKAGE_NAME-$VERSION/assets/icons/"

# Create tarball
tar -czf "rpmbuild/SOURCES/$PACKAGE_NAME-$VERSION.tar.gz" -C "$TEMP_DIR" "$PACKAGE_NAME-$VERSION"

# Cleanup temp dir
rm -rf "$TEMP_DIR"

# 3. RUN RPMBUILD
echo "Executing rpmbuild..."
cp webapp-manager.spec rpmbuild/SPECS/

rpmbuild --define "_topdir $(pwd)/rpmbuild" -ba rpmbuild/SPECS/webapp-manager.spec

if [ $? -eq 0 ]; then
    echo "================================================="
    echo "SUCCESS: RPM built successfully!"
    echo "Find your package in: $(pwd)/rpmbuild/RPMS/noarch/"
    echo "Install it with: sudo dnf install $(pwd)/rpmbuild/RPMS/noarch/$PACKAGE_NAME-$VERSION-1*.rpm"
    echo "================================================="
else
    echo "ERROR: RPM build failed. Ensure 'rpm-build' is installed."
    exit 1
fi
