from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from core.exceptions import BuildError
from core.repository import clone_or_update_repository
from core.repository import get_default_autobuild_target_dir
from core.repository import get_default_build_variables_target_dir
from core.repository import get_default_viewer_target_dir
from core.repository import get_viewer_repo_url


def test_clone_or_update_repository_clones_when_missing(tmp_path: Path) -> None:
    target = tmp_path / "viewer"

    with patch("core.repository.run_command") as mock_run:
        clone_or_update_repository("https://example.com/repo.git", target, print)

    mock_run.assert_called_once_with(
        ["git", "clone", "https://example.com/repo.git", str(target.resolve())],
        target.resolve().parent,
        print,
    )


def test_clone_or_update_repository_pulls_when_git_exists(tmp_path: Path) -> None:
    target = tmp_path / "viewer"
    (target / ".git").mkdir(parents=True)
    callback = Mock()

    with patch("core.repository.run_command") as mock_run:
        clone_or_update_repository("https://example.com/repo.git", target, callback)

    mock_run.assert_called_once_with(
        ["git", "pull", "--ff-only"],
        target.resolve(),
        callback,
    )


def test_clone_or_update_repository_fails_on_nonempty_non_git_dir(tmp_path: Path) -> None:
    target = tmp_path / "viewer"
    target.mkdir()
    (target / "file.txt").write_text("x", encoding="utf-8")

    with patch("core.repository.run_command") as mock_run:
        with pytest.raises(BuildError):
            clone_or_update_repository("https://example.com/repo.git", target, print)

    mock_run.assert_not_called()


def test_get_viewer_repo_url_success() -> None:
    url = get_viewer_repo_url("Firestorm Viewer")
    assert url == "https://github.com/FirestormViewer/phoenix-firestorm.git"


def test_get_viewer_repo_url_failure() -> None:
    with pytest.raises(BuildError):
        get_viewer_repo_url("Unknown Viewer")


def test_get_default_viewer_target_dir_success(tmp_path: Path) -> None:
    result = get_default_viewer_target_dir("Kokua Viewer", tmp_path)
    assert result == tmp_path.resolve() / "repos" / "kokua-viewer"


def test_get_default_viewer_target_dir_failure(tmp_path: Path) -> None:
    with pytest.raises(BuildError):
        get_default_viewer_target_dir("Unknown Viewer", tmp_path)


def test_get_default_autobuild_target_dir(tmp_path: Path) -> None:
    result = get_default_autobuild_target_dir(tmp_path)
    assert result == tmp_path.resolve() / "repos" / "autobuild"


def test_get_default_build_variables_target_dir(tmp_path: Path) -> None:
    result = get_default_build_variables_target_dir(tmp_path)
    assert result == tmp_path.resolve() / "repos" / "build-variables"
