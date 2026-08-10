import sys
from pathlib import Path
from unittest import mock

import muffin.utils


def test_import_submodules_uses_prefix():
    """import_submodules passes prefix to iter_modules for namespaced imports."""
    pkg = mock.MagicMock()
    pkg.__path__ = ["/fake/path"]

    with mock.patch.object(sys, "modules", {"mypkg": pkg}):
        with mock.patch("muffin.utils.pkgutil.iter_modules") as mock_iter:
            mock_iter.return_value = [("finder", "mypkg.mymod", False)]
            with mock.patch("muffin.utils.importlib.import_module") as mock_import:
                mock_import.return_value = mock.MagicMock()
                result = muffin.utils.import_submodules("mypkg")

    mock_iter.assert_called_once_with(["/fake/path"], "mypkg.")
    mock_import.assert_called_once_with("mypkg.mymod")
    assert "mymod" in result


def test_import_submodules_prefix_prevents_shadow_import(tmp_path):
    """With prefix, a submodule named 'tests' is imported from the
    correct package even when a top-level 'tests' shadows it on sys.path.

    Regression: caio 0.12.2 installs a top-level ``tests`` package
    into site-packages.  ``walk_packages`` without a prefix performs a
    bare ``__import__('tests')`` which resolves to the wrong package.
    With the prefix the lookup is correctly scoped.
    """
    # -- Build a package with a 'tests' submodule -------------------------
    pkg_dir = tmp_path / "_testpkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("")

    tests_sub = pkg_dir / "tests"
    tests_sub.mkdir()
    (tests_sub / "__init__.py").write_text('SENTINEL = "correct"')

    # -- Build a shadow top-level 'tests' earlier on sys.path -------------
    shadow = tmp_path / "_shadow"
    shadow.mkdir()
    (shadow / "tests").mkdir()
    (shadow / "tests" / "__init__.py").write_text('SENTINEL = "wrong"')

    # Shadow must come *before* the real package so that a bare
    # ``__import__('tests')`` would find the wrong one.
    sys.path.insert(0, str(shadow))
    sys.path.insert(0, str(tmp_path))

    # Also import the package itself so it lands in sys.modules.
    import _testpkg  # noqa: PLC0415

    try:
        result = muffin.utils.import_submodules("_testpkg", "tests")
        assert result["tests"].SENTINEL == "correct"
    finally:
        sys.path.remove(str(tmp_path))
        sys.path.remove(str(shadow))
        sys.modules.pop("_testpkg", None)
        sys.modules.pop("_testpkg.tests", None)
        # Don't remove 'tests' from sys.modules — it may belong to the
        # test suite itself and removing it breaks downstream imports.
        if "tests" in sys.modules and sys.modules["tests"].__name__ == "tests":
            if getattr(sys.modules["tests"], "SENTINEL", None) == "wrong":
                sys.modules.pop("tests", None)
