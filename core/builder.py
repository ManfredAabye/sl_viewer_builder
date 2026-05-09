import logging
import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from core.config import BuildConfig
from core.exceptions import BuildError


logger = logging.getLogger(__name__)
StatusCallback = Callable[[str], None]


def _resolve_vs2022_instance() -> str | None:
    candidates = [
        Path("C:/Program Files/Microsoft Visual Studio/2022/Community"),
        Path("C:/Program Files/Microsoft Visual Studio/2022/Professional"),
        Path("C:/Program Files/Microsoft Visual Studio/2022/Enterprise"),
        Path("C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return None


def _build_env(config: BuildConfig) -> dict[str, str]:
    env = os.environ.copy()
    env["AUTOBUILD"] = "autobuild"
    env["LL_BUILD"] = str(config.build_variables_path)
    env["AUTOBUILD_VARIABLES_FILE"] = str(config.build_variables_path / "variables")
    env["AUTOBUILD_CONFIG_FILE"] = str(config.viewer_path / "autobuild.xml")
    if platform.system() == "Windows":
        vs_instance = _resolve_vs2022_instance()
        if vs_instance:
            env["CMAKE_GENERATOR_INSTANCE"] = vs_instance
    if config.github_token.strip():
        env["AUTOBUILD_GITHUB_TOKEN"] = config.github_token.strip()
    return env


def ensure_autobuild_available(config: BuildConfig, callback: StatusCallback) -> None:
    if shutil.which("autobuild"):
        return

    callback("autobuild nicht gefunden, installiere Tool im aktuellen venv...")
    run_command(
        [sys.executable, "-m", "pip", "install", str(config.autobuild_path)],
        config.viewer_path,
        callback,
        env=os.environ.copy(),
    )


def clean_build_artifacts(config: BuildConfig, callback: StatusCallback) -> None:
    for build_dir in config.viewer_path.glob("build-*"):
        if build_dir.is_dir():
            callback(f"Entferne altes Build-Verzeichnis: {build_dir}")
            shutil.rmtree(build_dir, ignore_errors=True)

    packages_dir = config.viewer_path / "packages"
    if packages_dir.exists() and packages_dir.is_dir():
        callback(f"Entferne altes Package-Verzeichnis: {packages_dir}")
        shutil.rmtree(packages_dir, ignore_errors=True)


def _resolve_build_directory(config: BuildConfig) -> Path:
    pattern = f"build-vc*-{config.architecture}"
    candidates = [p for p in config.viewer_path.glob(pattern) if p.is_dir()]

    if not candidates:
        return config.viewer_path

    # Use the most recently modified build directory.
    return max(candidates, key=lambda path: path.stat().st_mtime)


def run_command(
    command: list[str],
    cwd: Path,
    callback: StatusCallback,
    env: dict[str, str] | None = None,
) -> None:
    logger.info("Starte Kommando: %s", " ".join(command))

    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError as error:
        raise BuildError(f"Kommando nicht gefunden: {command[0]}") from error

    if process.stdout is None:
        raise BuildError("Keine Ausgabe verfuegbar")

    for line in process.stdout:
        line = line.strip()

        if line:
            callback(line)
            logger.info(line)

    return_code = process.wait()

    if return_code != 0:
        raise BuildError(f"Kommando fehlgeschlagen: {' '.join(command)}")


def configure_build(config: BuildConfig, callback: StatusCallback) -> None:
    ensure_autobuild_available(config, callback)
    command = [
        "autobuild",
        "configure",
        "-A",
        config.architecture,
        "-c",
        config.build_type,
    ]

    run_command(command, config.viewer_path, callback, env=_build_env(config))


def install_dependencies(config: BuildConfig, callback: StatusCallback) -> None:
    ensure_autobuild_available(config, callback)
    command = ["autobuild", "install"]
    run_command(command, config.viewer_path, callback, env=_build_env(config))


def build_viewer(config: BuildConfig, callback: StatusCallback) -> None:
    ensure_autobuild_available(config, callback)
    command = [
        "autobuild",
        "build",
        "-A",
        config.architecture,
        "-c",
        config.build_type,
        "--no-configure",
    ]

    if config.clean_build:
        command.append("--clean")

    if config.verbose:
        command.append("--verbose")

    # Visual Studio (Windows) doesn't accept -j via autobuild forwarding.
    if platform.system() != "Windows":
        command.append("--")
        command.append(f"-j{config.jobs}")

    run_command(command, _resolve_build_directory(config), callback, env=_build_env(config))


def package_viewer(config: BuildConfig, callback: StatusCallback) -> None:
    ensure_autobuild_available(config, callback)
    command = [
        "autobuild",
        "package",
        "-A",
        config.architecture,
        "-c",
        config.build_type,
    ]
    run_command(command, config.viewer_path, callback, env=_build_env(config))
