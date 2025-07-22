#!/bin/bash
# bump_version.sh
# Script để tăng phiên bản theo format vMAJOR.MINOR.PATCH

VERSION_FILE="version.txt"

# Nếu version.txt chưa tồn tại, tạo mới
if [ ! -f "$VERSION_FILE" ]; then
    echo "v1.0.0" > "$VERSION_FILE"
    echo "Tạo mới version.txt với phiên bản v1.0.0"
fi

# Đọc version hiện tại
CURRENT_VERSION=$(cat "$VERSION_FILE")
echo "Phiên bản hiện tại: $CURRENT_VERSION"

# Loại bỏ 'v' và tách MAJOR, MINOR, PATCH
VERSION_NUM=${CURRENT_VERSION#v}
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION_NUM"

# Kiểm tra tham số (major/minor/patch)
case "$1" in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch|"")
    PATCH=$((PATCH + 1))
    ;;
  *)
    echo "Tham số không hợp lệ! Dùng: major | minor | patch"
    exit 1
    ;;
esac

# Tạo version mới
NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"

# Ghi version mới vào file
echo "$NEW_VERSION" > "$VERSION_FILE"
echo "Phiên bản mới: $NEW_VERSION"

# Ghi commit message gần nhất vào changelog.txt
git log -1 --pretty=%B > changelog.txt
echo "Cập nhật changelog.txt với commit message mới nhất."
