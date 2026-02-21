# Maintainer: Alexandra
pkgname=detect-repo-language
pkgver=1.3.0
pkgrel=1
pkgdesc="Detect the primary programming language of a repository by analyzing file extensions and lines of code"
arch=('any')
url="https://github.com/alexankitty/detect-repo-language"
license=('MIT')
depends=('python>=3.7')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/alexankitty/detect-repo-language/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')  # Replace with actual sha256sum after first build

build() {
    cd "${srcdir}/detect-repo-language-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/detect-repo-language-${pkgver}"
    python -m installer --destdir="${pkgdir}" dist/*.whl
    
    # Install languages data files to system data directory
    mkdir -p "${pkgdir}/usr/share/detect-repo-language/languages"
    cp -r src/detect_repo_language/languages/*.json "${pkgdir}/usr/share/detect-repo-language/languages/"
}
