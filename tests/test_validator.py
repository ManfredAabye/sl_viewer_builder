import pytest

from core.exceptions import ValidationError
from core.validator import validate_build_type
from core.validator import validate_jobs


def test_validate_build_type_success() -> None:
    assert validate_build_type("ReleaseFS_AVX") == "ReleaseFS_AVX"


def test_validate_build_type_failure() -> None:
    with pytest.raises(ValidationError):
        validate_build_type("Invalid")


def test_validate_jobs_success() -> None:
    assert validate_jobs("4") == 4


def test_validate_jobs_failure() -> None:
    with pytest.raises(ValidationError):
        validate_jobs("abc")
