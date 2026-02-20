# Arch Linux PKGBUILD Guide

This directory contains PKGBUILD files for installing `detect-repo-language` on Arch Linux.

## Two Installation Methods

### Method 1: From GitHub Source (PKGBUILD)
Use the standard `PKGBUILD` file to build from the GitHub repository.

**Advantages:**
- Builds from verified source code
- Standard Arch packaging approach
- Full control over build process

**Setup:**
1. Ensure you have GitHub release tags set up (e.g., `v1.0.0`)
2. Update the `sha256sum` in PKGBUILD after first build
3. Build: `makepkg -si`

**To get the correct sha256sum:**
```bash
makepkg --printsrcinfo | grep sha256sum
```

### Method 2: From PyPI (PKGBUILD.pypi)
Use `PKGBUILD.pypi` to build from the PyPI repository (recommended for published packages).

**Advantages:**
- Simplest approach
- Works once package is published to PyPI
- No need to manage GitHub releases

**Setup:**
1. Publish package to PyPI: `python -m twine upload dist/*`
2. Build: `cp PKGBUILD.pypi PKGBUILD && makepkg -si`

## Developer Workflow

### Preparing for Arch Linux Distribution

1. **Create a GitHub Release:**
   ```bash
   git tag v1.0.0
   git push --tags
   ```

2. **Validate PKGBUILD:**
   ```bash
   makepkg --verifysource
   ```

3. **Build and Test:**
   ```bash
   makepkg -s  # Build with dependencies
   ```

4. **Install Locally:**
   ```bash
   makepkg -si  # Build and install
   ```

5. **Submit to AUR (Optional):**
   - Create an AUR account at https://aur.archlinux.org
   - Clone your package repo
   - Push to AUR with git

## Testing the Package

After installation:
```bash
# Verify command is available
which detect-repo-language

# Test functionality
detect-repo-language --primary-only /home/user/some/git/repo
detect-repo-language --with-glyph /home/user/some/git/repo
```

## Updating the Package

When releasing a new version:

1. Update version in PKGBUILD: `pkgver=X.Y.Z`
2. Create git tag: `git tag vX.Y.Z && git push --tags`
3. Get new sha256sum: `makepkg --verifysource` (will fail with old sum, then tell you new one)
4. Update sha256sums in PKGBUILD
5. Build and test: `makepkg -si`

## Troubleshooting

**"failed to verify source file integrity"**
- Update sha256sums: Run `makepkg --printsrcinfo | grep sha256sum`

**"Could not resolve host"**
- Check internet connection
- Verify GitHub URL is correct
- Ensure GitHub release tag exists

**ModuleNotFoundError on build**
- Ensure `python-build`, `python-installer`, `python-wheel` are installed
- `sudo pacman -S python-build python-installer python-wheel`
