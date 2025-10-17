#!/bin/bash

# Dashcam Manager - Build All Script
# Builds Linux and Android release versions

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Dashcam Manager - Build All (Release)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}Error: Flutter not found in PATH${NC}"
    echo "Please install Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

# Show Flutter version
echo -e "${BLUE}Flutter version:${NC}"
flutter --version | head -n 1
echo ""

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
flutter clean
echo -e "${GREEN}✓ Clean complete${NC}"
echo ""

# Get dependencies
echo -e "${YELLOW}Getting Flutter dependencies...${NC}"
flutter pub get
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies fetched${NC}"
else
    echo -e "${RED}✗ Failed to get dependencies${NC}"
    exit 1
fi
echo ""

# Build Linux
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Linux Release${NC}"
echo -e "${BLUE}========================================${NC}"
if flutter build linux --release; then
    echo -e "${GREEN}✓ Linux build successful${NC}"
    LINUX_BUILD_DIR="$SCRIPT_DIR/build/linux/x64/release/bundle"
    if [ -d "$LINUX_BUILD_DIR" ]; then
        echo -e "${GREEN}Linux executable: $LINUX_BUILD_DIR/dashcam_flutter${NC}"
        LINUX_SIZE=$(du -sh "$LINUX_BUILD_DIR" | cut -f1)
        echo -e "${GREEN}Build size: $LINUX_SIZE${NC}"
    fi
else
    echo -e "${RED}✗ Linux build failed${NC}"
    exit 1
fi
echo ""

# Build Android APK
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Android APK (Release)${NC}"
echo -e "${BLUE}========================================${NC}"
if flutter build apk --release; then
    echo -e "${GREEN}✓ Android APK build successful${NC}"
    APK_PATH="$SCRIPT_DIR/build/app/outputs/flutter-apk/app-release.apk"
    if [ -f "$APK_PATH" ]; then
        echo -e "${GREEN}APK location: $APK_PATH${NC}"
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        echo -e "${GREEN}APK size: $APK_SIZE${NC}"
    fi
else
    echo -e "${RED}✗ Android APK build failed${NC}"
    exit 1
fi
echo ""

# Build Android Split APKs (optional, faster and smaller)
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Android Split APKs (Release)${NC}"
echo -e "${BLUE}========================================${NC}"
if flutter build apk --release --split-per-abi; then
    echo -e "${GREEN}✓ Android split APKs build successful${NC}"
    SPLIT_APK_DIR="$SCRIPT_DIR/build/app/outputs/flutter-apk"
    echo -e "${GREEN}Split APKs location: $SPLIT_APK_DIR${NC}"

    # List all split APKs
    for apk in "$SPLIT_APK_DIR"/app-*-release.apk; do
        if [ -f "$apk" ]; then
            FILENAME=$(basename "$apk")
            SIZE=$(du -h "$apk" | cut -f1)
            echo -e "${GREEN}  - $FILENAME ($SIZE)${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠ Android split APKs build failed (optional)${NC}"
fi
echo ""

# Build summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Build Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}✓ All builds completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Build artifacts:${NC}"
echo ""

# Linux
echo -e "${BLUE}Linux (Desktop):${NC}"
if [ -d "$LINUX_BUILD_DIR" ]; then
    echo "  Location: $LINUX_BUILD_DIR/"
    echo "  Run: $LINUX_BUILD_DIR/dashcam_flutter"
else
    echo -e "${RED}  Not found${NC}"
fi
echo ""

# Android Universal APK
echo -e "${BLUE}Android (Universal APK):${NC}"
if [ -f "$APK_PATH" ]; then
    echo "  Location: $APK_PATH"
    echo "  Size: $(du -h "$APK_PATH" | cut -f1)"
    echo "  Install: adb install $APK_PATH"
else
    echo -e "${RED}  Not found${NC}"
fi
echo ""

# Android Split APKs
echo -e "${BLUE}Android (Split APKs - Optimized):${NC}"
SPLIT_COUNT=$(ls -1 "$SPLIT_APK_DIR"/app-*-release.apk 2>/dev/null | wc -l)
if [ "$SPLIT_COUNT" -gt 1 ]; then
    echo "  Location: $SPLIT_APK_DIR/"
    echo "  APKs:"
    for apk in "$SPLIT_APK_DIR"/app-*-release.apk; do
        if [ -f "$apk" ]; then
            FILENAME=$(basename "$apk")
            SIZE=$(du -h "$apk" | cut -f1)

            # Determine architecture
            if [[ "$FILENAME" == *"armeabi-v7a"* ]]; then
                ARCH="32-bit ARM (older devices)"
            elif [[ "$FILENAME" == *"arm64-v8a"* ]]; then
                ARCH="64-bit ARM (most modern devices)"
            elif [[ "$FILENAME" == *"x86_64"* ]]; then
                ARCH="64-bit Intel/AMD (emulators)"
            else
                ARCH="Universal"
            fi

            echo "    - $FILENAME ($SIZE) - $ARCH"
        fi
    done
else
    echo -e "${YELLOW}  Split APKs not available${NC}"
fi
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Build process complete!${NC}"
echo -e "${BLUE}========================================${NC}"
