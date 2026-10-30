"""Keep the documentation pages wired together."""

from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"


def test_readme_includes():
    """docs/plugins.rst and docs/index.rst include slices of the README."""
    readme = (ROOT / "README.rst").read_text()
    for marker in (".. _description:", ".. _plugins:", ".. _benchmarks:", ".. _links:"):
        assert marker in readme, f"README lost the include marker {marker!r}"


def test_toctree_pages_exist():
    """Every page listed in the index toctree is a real file."""
    index = (DOCS / "index.rst").read_text()
    toctree = index.split(".. toctree::")[1]
    pages = [line.strip() for line in toctree.splitlines() if line.startswith("    ")]
    pages = [page for page in pages if page and not page.startswith(":")]

    assert pages
    for page in pages:
        assert (DOCS / f"{page}.rst").exists(), f"toctree points to missing {page}.rst"
