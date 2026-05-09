from pathlib import Path

from core.config import BuildConfig


def test_config_creation() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="Release",
        jobs=4,
        clean_build=False,
    )

    assert config.build_type == "Release"
    assert config.architecture == "64"
    assert config.use_openal is True
    assert config.use_fmod is False


def test_config_creation_with_flags() -> None:
    config = BuildConfig(
        viewer_path=Path("."),
        autobuild_path=Path("."),
        build_variables_path=Path("."),
        build_type="ReleaseFS_AVX2",
        jobs=8,
        clean_build=True,
        architecture="64",
        avx2_optimize=True,
        use_openal=True,
        use_fmod=False,
        verbose=True,
        package=True,
    )

    assert config.avx2_optimize is True
    assert config.verbose is True
    assert config.package is True
