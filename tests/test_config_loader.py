"""Unit tests for independent ConfigLoader instances."""

from pathlib import Path

import yaml

from utils.ConfigLoader import ConfigLoader


def _write_project_config(root: Path, env_name: str):
    root.mkdir(parents=True, exist_ok=True)
    (root / "TestBed.yml").write_text(
        yaml.safe_dump({"env": env_name}, allow_unicode=True),
        encoding="utf-8",
    )
    (root / "TestSet.yml").write_text(
        yaml.safe_dump({"test_cases": []}, allow_unicode=True),
        encoding="utf-8",
    )
    main_config = {
        "TestBedPath": "TestBed.yml",
        "TestSetPath": "TestSet.yml",
        "base_dir": ".",
    }
    main_path = root / "main.yml"
    main_path.write_text(
        yaml.safe_dump(main_config, allow_unicode=True),
        encoding="utf-8",
    )
    return main_path


def test_config_loaders_with_distinct_paths_do_not_share_state(tmp_path):
    first_path = _write_project_config(tmp_path / "first", "first-env")
    second_path = _write_project_config(tmp_path / "second", "second-env")

    first_loader = ConfigLoader(path=first_path)
    second_loader = ConfigLoader(path=second_path)

    assert first_loader is not second_loader
    assert first_loader.get("TestBed.env") == "first-env"
    assert second_loader.get("TestBed.env") == "second-env"
    assert first_loader.config_path == first_path.resolve()
    assert second_loader.config_path == second_path.resolve()


def test_config_save_is_scoped_to_one_loader(tmp_path):
    first_path = _write_project_config(tmp_path / "first", "first-env")
    second_path = _write_project_config(tmp_path / "second", "second-env")
    first_loader = ConfigLoader(path=first_path)
    second_loader = ConfigLoader(path=second_path)

    first_loader.save_test_bed({"env": "saved-env"})

    assert first_loader.get("TestBed.env") == "saved-env"
    assert second_loader.get("TestBed.env") == "second-env"
