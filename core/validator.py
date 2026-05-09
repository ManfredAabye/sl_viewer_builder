from pathlib import Path

from core.exceptions import ValidationError


VALID_BUILD_TYPES = {
    "Release",
    "Debug",
    "RelWithDebInfo",
    "ReleaseFS",
    "ReleaseFS_AVX",
    "ReleaseFS_AVX2",
    "ReleaseFS_open",
    "ReleaseOS",
    "RelWithDebInfoFS",
    "RelWithDebInfoFS_open",
    "RelWithDebInfoOS",
}


def validate_directory(path: str, name: str) -> Path:
    directory = Path(path).expanduser().resolve()

    if not directory.exists():
        raise ValidationError(f"{name} existiert nicht: {path}")

    if not directory.is_dir():
        raise ValidationError(f"{name} ist kein Verzeichnis: {path}")

    return directory


def validate_build_type(build_type: str) -> str:
    if build_type not in VALID_BUILD_TYPES:
        raise ValidationError(f"Ungueltiger Build-Typ: {build_type}")

    return build_type


def validate_jobs(value: str) -> int:
    try:
        jobs = int(value)
    except ValueError as error:
        raise ValidationError("Jobs muss eine Zahl sein") from error

    if jobs <= 0:
        raise ValidationError("Jobs muss groesser als 0 sein")

    return jobs
