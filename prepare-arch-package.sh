#!/bin/bash
# Helper script to prepare detect-repo-language for Arch Linux packaging

set -e

VERSION="${1:-1.0.0}"
REPO_NAME="lang-detect"
GITHUB_USER="${2:-yourusername}"

echo "🏗️  Preparing Arch Linux package for detect-repo-language v${VERSION}"
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ git is required but not installed"
    exit 1
fi

# Create GitHub release
echo "📌 Step 1: Creating GitHub release tag..."
if git rev-parse "v${VERSION}" 2>/dev/null; then
    echo "   ⚠️  Tag v${VERSION} already exists"
else
    git tag -a "v${VERSION}" -m "Release version ${VERSION} for Arch Linux packaging"
    git push --tags
    echo "   ✓ Tag v${VERSION} created and pushed"
fi

echo ""
echo "📦 Step 2: Building wheel..."
python3 -m build --wheel 2>/dev/null || {
    echo "   Installing build tools..."
    python3 -m pip install build wheel setuptools --quiet
    python3 -m build --wheel
}
echo "   ✓ Wheel built: $(ls -1 dist/*.whl 2>/dev/null | tail -1)"

echo ""
echo "🔐 Step 3: Calculating sha256sum for PKGBUILD..."
TARBALL_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}/archive/refs/tags/v${VERSION}.tar.gz"
echo "   Downloading: ${TARBALL_URL}"

# Create temporary directory
TMPDIR=$(mktemp -d)
trap "rm -rf ${TMPDIR}" EXIT

pushd "${TMPDIR}" > /dev/null
if curl -sL -o "detect-repo-language-${VERSION}.tar.gz" "${TARBALL_URL}"; then
    SHA256=$(sha256sum "detect-repo-language-${VERSION}.tar.gz" | cut -d' ' -f1)
    echo "   ✓ SHA256: ${SHA256}"
    echo ""
    echo "📝 Update PKGBUILD with:"
    echo "   sha256sums=('${SHA256}')"
else
    echo "   ⚠️  Could not download tarball. Ensure GitHub release/tag exists."
    echo "      Update sha256sums manually after testing"
fi
popd > /dev/null

echo ""
echo "✅ Preparation complete!"
echo ""
echo "Next steps:"
echo "1. Update sha256sums in PKGBUILD if needed"
echo "2. Test the package build:"
echo "   cd /tmp && cp -r /home/alexandra/git/lang-detect test-pkgbuild && cd test-pkgbuild"
echo "   makepkg --verifysource"
echo "   makepkg -si"
echo ""
echo "3. (Optional) Submit to AUR:"
echo "   https://aur.archlinux.org/submit/"
