import os
import sys
import shutil
import unittest
import pytest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

from src.coverage_test import build_test_suite

def test_build_test_suite_with_real_files(tmp_path):
    test_dir = tmp_path / "real_test_pkg"
    test_dir.mkdir()
    (test_dir / "__init__.py").write_text("")
    
    test_file = test_dir / "test_demo.py"
    test_file_content = """
import unittest
class TestRealCase(unittest.TestCase):
    def test_pass(self):
        pass
"""
    test_file.write_text(test_file_content)
    sys.path.append(str(tmp_path))

    try:
        module_rel_path = os.path.join("real_test_pkg", "test_demo.py")
        test_paths = [module_rel_path]

        wrong_module_name = ''.join(module_rel_path.split(".")[:-1]).replace("\\", ".")
        
        if os.name != 'nt':
            with pytest.raises(ImportError):
                import importlib
                importlib.import_module(wrong_module_name)

        suite = build_test_suite(test_paths)

        assert isinstance(suite, unittest.TestSuite)
        assert suite.countTestCases() > 0

        tests = list(suite)

        found = False
        for t in tests:
            for sub_t in t:
                if "TestRealCase" in str(sub_t):
                    found = True
        assert found

    finally:
        if str(tmp_path) in sys.path:
            sys.path.remove(str(tmp_path))

        if "real_test_pkg.test_demo" in sys.modules:
            del sys.modules["real_test_pkg.test_demo"]

def test_os_sep_logic_directly():
    linux_fake_path = "dir/subdir/file.py"
    
    bad_logic = ''.join(linux_fake_path.split(".")[:-1]).replace("\\", ".")
    good_logic = ''.join(linux_fake_path.split(".")[:-1]).replace(os.sep, ".")

    if os.sep == '/':
        assert "/" in bad_logic
        assert "/" not in good_logic
        assert good_logic == "dir.subdir.file"