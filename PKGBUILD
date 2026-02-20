# Maintainer: Alexandra
pkgname=detect-repo-language
pkgver=1.0.0
pkgrel=1
pkgdesc="Detect the primary programming language of a repository by analyzing file extensions and lines of code"
arch=('any')
url="https://github.com/alexankitty/repo-language-detect"
license=('MIT')
depends=('python>=3.7')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/alexankitty/repo-language-detect/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')  # Replace with actual sha256sum after first build

build() {
    cd "${srcdir}/lang-detect-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/lang-detect-${pkgver}"
    python -m installer --destdir="${pkgdir}" dist/*.whl
}
