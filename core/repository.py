from pathlib import Path

from core.builder import run_command
from core.exceptions import BuildError


VIEWER_REPO_URL = "https://github.com/secondlife/viewer.git"
AUTOBUILD_REPO_URL = "https://github.com/secondlife/autobuild.git"
BUILD_VARIABLES_REPO_URL = "https://github.com/secondlife/build-variables.git"
SUPPORTED_VIEWER_REPOS = {
    "Second Life Viewer": "https://github.com/secondlife/viewer.git",
    "Firestorm Viewer": "https://github.com/FirestormViewer/phoenix-firestorm.git",
    "Alchemy Viewer": "https://github.com/AlchemyViewer/Alchemy.git",
    "Kokua Viewer": "https://github.com/kokua/kokua.git",
    "Singularity Viewer": "https://github.com/singularity-viewer/SingularityViewer.git",
    "Cool VL Viewer": "https://github.com/kjansmasl/coolvlviewer.git",
    "Black Dragon Viewer": "https://github.com/NiranV/Black-Dragon-Viewer.git",
    "Catznip Viewer": "https://github.com/catznip/viewer.git",
}
VIEWER_DEFAULT_DIR_NAMES = {
    "Second Life Viewer": "secondlife-viewer",
    "Firestorm Viewer": "firestorm-viewer",
    "Alchemy Viewer": "alchemy-viewer",
    "Kokua Viewer": "kokua-viewer",
    "Singularity Viewer": "singularity-viewer",
    "Cool VL Viewer": "coolvl-viewer",
    "Black Dragon Viewer": "black-dragon-viewer",
    "Catznip Viewer": "catznip-viewer",
}


def get_viewer_repo_url(viewer_name: str) -> str:
    try:
        return SUPPORTED_VIEWER_REPOS[viewer_name]
    except KeyError as error:
        raise BuildError(f"Nicht unterstuetzter Viewer: {viewer_name}") from error


def get_default_viewer_target_dir(viewer_name: str, base_dir: Path) -> Path:
    try:
        folder_name = VIEWER_DEFAULT_DIR_NAMES[viewer_name]
    except KeyError as error:
        raise BuildError(f"Nicht unterstuetzter Viewer: {viewer_name}") from error

    return base_dir.expanduser().resolve() / "repos" / folder_name


def get_default_autobuild_target_dir(base_dir: Path) -> Path:
    return base_dir.expanduser().resolve() / "repos" / "autobuild"


def get_default_build_variables_target_dir(base_dir: Path) -> Path:
    return base_dir.expanduser().resolve() / "repos" / "build-variables"


def clone_or_update_repository(
    repo_url: str,
    target_dir: Path,
    callback,
) -> None:
    resolved_target = target_dir.expanduser().resolve()

    if resolved_target.exists():
        git_dir = resolved_target / ".git"

        if git_dir.exists() and git_dir.is_dir():
            callback(f"Aktualisiere Repo: {resolved_target}")
            run_command(
                ["git", "pull", "--ff-only"],
                resolved_target,
                callback,
            )
            return

        if any(resolved_target.iterdir()):
            raise BuildError(
                f"Zielverzeichnis ist nicht leer und kein Git-Repo: {resolved_target}"
            )
    else:
        resolved_target.parent.mkdir(parents=True, exist_ok=True)

    callback(f"Klone Repo nach: {resolved_target}")
    run_command(
        ["git", "clone", repo_url, str(resolved_target)],
        resolved_target.parent,
        callback,
    )
