#!/bin/bash
# bump_version.sh
# Script tăng phiên bản dựa trên commit message:
#   [major] -> tăng MAJOR
#   [minor] -> tăng MINOR
#   mặc định -> tăng PATCH
# Đồng thời cập nhật changelog.txt

VERSION_FILE="version.txt"
CHANGELOG_FILE="changelog.txt"

# Nếu version.txt chưa tồn tại, tạo mới
if [ ! -f "$VERSION_FILE" ]; then
    echo "v1.0.0" > "$VERSION_FILE"
    echo "Tạo mới version.txt với phiên bản v1.0.0"
fi

# Đọc version hiện tại
CURRENT_VERSION=$(cat "$VERSION_FILE")
VERSION_NUM=${CURRENT_VERSION#v}
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION_NUM"

# Lấy commit message gần nhất
COMMIT_MSG=$(git log -1 --pretty=%B)

# Xác định loại bump
if echo "$COMMIT_MSG" | grep -qi "\[major\]"; then
    BUMP_TYPE="major"
elif echo "$COMMIT_MSG" | grep -qi "\[minor\]"; then
    BUMP_TYPE="minor"
else
    BUMP_TYPE="patch"
fi

# Tăng version
case "$BUMP_TYPE" in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
esac

# Ghi version mới
NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"
echo "$NEW_VERSION" > "$VERSION_FILE"
echo "Phiên bản mới: $NEW_VERSION"

# Cập nhật changelog.txt với commit message
NOW=$(date +"%d-%m-%Y %H:%M")
echo "$NOW — 🚀 ${COMMIT_MSG}" > "$CHANGELOG_FILE"
echo "Cập nhật $CHANGELOG_FILE với commit message mới nhất."