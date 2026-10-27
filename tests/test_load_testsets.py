"""Filesystem-isolated tests for business test-case discovery."""

from pathlib import Path

from app.services.load_testsets import (
    _parse_variable_from_file,
    get_case_name,
    get_module_name,
    traverse_test_cases,
)


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_static_name_parsing_and_filename_fallbacks(tmp_path):
    module_dir = tmp_path / "assessment"
    _write(module_dir / "__init__.py", 'module_name = "Assessment Module"\n')
    case_file = _write(
        module_dir / "check_user.py",
        'case_name = "Check User"\n',
    )

    assert get_module_name(module_dir) == "Assessment Module"
    assert get_case_name(case_file) == "Check User"
    assert get_module_name(tmp_path / "missing_module") == "missing_module"
    assert get_case_name(tmp_path / "unnamed_case.py") == "unnamed_case"


def test_static_parser_returns_fallback_for_invalid_or_unsupported_files(tmp_path):
    invalid_python = _write(tmp_path / "broken.py", "module_name = \n")
    text_file = _write(tmp_path / "notes.txt", "module_name = 'not a python file'")
    missing_variable = _write(tmp_path / "plain.py", "other_name = 'value'\n")

    assert _parse_variable_from_file(invalid_python, "module_name", "fallback") == "fallback"
    assert _parse_variable_from_file(text_file, "module_name", "fallback") == "fallback"
    assert _parse_variable_from_file(tmp_path / "absent.py", "module_name", "fallback") == "fallback"
    assert _parse_variable_from_file(missing_variable, "module_name", "fallback") == "fallback"


def test_static_parser_does_not_execute_discovered_source(tmp_path):
    marker = tmp_path / "should-not-exist.txt"
    source = _write(
        tmp_path / "case.py",
        f'case_name = "Safe Case"\nopen({str(marker)!r}, "w").write("executed")\n',
    )

    assert get_case_name(source) == "Safe Case"
    assert not marker.exists()


def test_traverse_test_cases_builds_sorted_recursive_tree_and_filters_files(tmp_path):
    business = tmp_path / "Business"
    alpha = business / "alpha_module"
    beta = business / "beta_module"
    _write(alpha / "__init__.py", "module_name = 'Alpha'\n")
    _write(beta / "__init__.py", "module_name = 'Beta'\n")
    _write(alpha / "TestCases" / "alpha_case.py", "case_name = 'Alpha Case'\n")
    _write(alpha / "TestCases" / "notes.txt", "ignored = True\n")
    _write(alpha / "TestCases" / "__init__.py", "")
    _write(alpha / "TestCases" / "__pycache__" / "ignored.py", "case_name = 'Ignored'\n")
    _write(
        beta / "TestCases" / "nested" / "__init__.py",
        "module_name = 'Nested Group'\n",
    )
    _write(
        beta / "TestCases" / "nested" / "beta_case.py",
        "case_name = 'Beta Case'\n",
    )
    _write(beta / "TestCases" / "empty_dir" / "__init__.py", "")
    (business / "without_test_cases").mkdir(parents=True)
    _write(business / "without_test_cases" / "__init__.py", "module_name = 'No Cases'\n")

    tree = traverse_test_cases(str(business))

    assert [module["label"] for module in tree] == ["Alpha", "Beta"]
    assert tree[0]["type"] == "module"
    assert tree[0]["children"][0]["label"] == "Alpha Case"
    assert tree[0]["children"][0]["type"] == "file"
    assert tree[0]["children"][0]["isLeaf"] is True
    assert [item["label"] for item in tree[1]["children"]] == ["Nested Group"]
    nested = tree[1]["children"][0]
    assert nested["type"] == "folder"
    assert nested["children"][0]["label"] == "Beta Case"
    all_paths = str(tree)
    assert "notes.txt" not in all_paths
    assert "__init__.py" not in all_paths
    assert "__pycache__" not in all_paths
    assert "Ignored" not in all_paths


def test_traverse_test_cases_returns_empty_for_missing_or_irrelevant_roots(tmp_path):
    assert traverse_test_cases(str(tmp_path / "missing-business")) == []

    not_a_directory = _write(tmp_path / "business.txt", "not a directory")
    assert traverse_test_cases(str(not_a_directory)) == []

    empty_business = tmp_path / "empty-business"
    empty_business.mkdir()
    _write(empty_business / "no_test_cases" / "__init__.py", "module_name = 'Empty'\n")
    assert traverse_test_cases(str(empty_business)) == []
