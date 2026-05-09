from pathlib import Path
from unittest.mock import patch

from core.builder import (
    _build_env,
    build_viewer,
    clean_build_artifacts,
    ensure_autobuild_available,
    install_dependencies,
    package_viewer,
    run_command,
)
from core.config import BuildConfig


def test_run_command() -> None:
    with patch("core.builder.subprocess.Popen") as mock_popen:
        process = mock_popen.return_value
        process.stdout = ["test"]
        process.wait.return_value = 0

        run_command(
            ["echo", "test"],
            Path("."),
            print,
        )


def test_build_env_sets_autobuild_and_ll_build() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("./repos/autobuild"),
        build_variables_path=Path("./repos/build-variables"),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    env = _build_env(config)
    assert env["AUTOBUILD"] == "autobuild"
    assert env["LL_BUILD"] == str(config.build_variables_path)
    assert env["AUTOBUILD_VARIABLES_FILE"] == str(
        config.build_variables_path / "variables"
    )
    assert env["AUTOBUILD_CONFIG_FILE"] == str(config.viewer_path / "autobuild.xml")


def test_build_env_sets_optional_github_token() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("./repos/autobuild"),
        build_variables_path=Path("./repos/build-variables"),
        build_type="Release",
        jobs=4,
        clean_build=False,
        github_token="token-value",
    )

    env = _build_env(config)
    assert env["AUTOBUILD_GITHUB_TOKEN"] == "token-value"


def test_ensure_autobuild_available_skips_when_present() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    with patch("core.builder.shutil.which", return_value="autobuild"):
        with patch("core.builder.run_command") as mock_run_command:
            ensure_autobuild_available(config, print)

    mock_run_command.assert_not_called()


def test_ensure_autobuild_available_installs_when_missing() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("./repos/autobuild"),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    with patch("core.builder.shutil.which", return_value=None):
        with patch("core.builder.run_command") as mock_run_command:
            ensure_autobuild_available(config, print)

    command = mock_run_command.call_args.args[0]
    assert command[1:3] == ["-m", "pip"]
    assert command[-1] == str(config.autobuild_path)


def test_install_dependencies_runs_autobuild_install() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    with patch("core.builder.run_command") as mock_run_command:
        install_dependencies(config, print)

    command = mock_run_command.call_args.args[0]
    assert command == ["autobuild", "install"]


def test_package_viewer_runs_autobuild_package() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
        architecture="64",
    )

    with patch("core.builder.run_command") as mock_run_command:
        package_viewer(config, print)

    command = mock_run_command.call_args.args[0]
    assert command == ["autobuild", "package", "-A", "64", "-c", "Release"]


def test_clean_build_artifacts_removes_build_directories(tmp_path: Path) -> None:
    build_dir = tmp_path / "build-vc170-64"
    build_dir.mkdir()
    (build_dir / "dummy.txt").write_text("x", encoding="utf-8")

    config = BuildConfig(
        viewer_path=tmp_path,
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=True,
    )

    clean_build_artifacts(config, print)
    assert not build_dir.exists()


def test_clean_build_artifacts_removes_packages_directory(tmp_path: Path) -> None:
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()
    (packages_dir / "marker.txt").write_text("x", encoding="utf-8")

    config = BuildConfig(
        viewer_path=tmp_path,
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="ReleaseOS",
        jobs=4,
        clean_build=True,
    )

    clean_build_artifacts(config, print)
    assert not packages_dir.exists()


def test_build_viewer_windows_without_jobs_flag() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    with patch("core.builder.platform.system", return_value="Windows"):
        with patch("core.builder.run_command") as mock_run_command:
            with patch("core.builder._resolve_build_directory", return_value=Path(".")):
                build_viewer(config, print)

    command = mock_run_command.call_args.args[0]
    assert "-j4" not in command
    assert "--" not in command
    assert "--no-configure" in command


def test_build_viewer_non_windows_with_jobs_flag() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    with patch("core.builder.platform.system", return_value="Linux"):
        with patch("core.builder.run_command") as mock_run_command:
            with patch("core.builder._resolve_build_directory", return_value=Path(".")):
                build_viewer(config, print)

    command = mock_run_command.call_args.args[0]
    assert "--" in command
    assert "-j4" in command
    assert "--no-configure" in command


def test_build_viewer_uses_resolved_build_directory() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    expected_cwd = Path("build-vc170-64")

    with patch("core.builder.platform.system", return_value="Windows"):
        with patch("core.builder._resolve_build_directory", return_value=expected_cwd):
            with patch("core.builder.run_command") as mock_run_command:
                build_viewer(config, print)

    cwd = mock_run_command.call_args.args[1]
    assert cwd == expected_cwd
