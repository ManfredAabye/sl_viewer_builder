from pathlib import Path

import pytest

from core.exceptions import ValidationError
from ui.build_panel import BuildPanel


class _FakeVar:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


class _FakeConfigPanel:
    def __init__(self, build_type: str, github_token: str):
        self.viewer_path = _FakeVar(str(Path(".").resolve()))
        self.autobuild_path = _FakeVar(str(Path(".").resolve()))
        self.build_variables_path = _FakeVar(str(Path(".").resolve()))
        self.build_type = _FakeVar(build_type)
        self.jobs = _FakeVar("4")
        self.clean_build = _FakeVar(False)
        self.architecture = _FakeVar("64")
        self.avx2_optimize = _FakeVar(False)
        self.use_openal = _FakeVar(True)
        self.use_fmod = _FakeVar(False)
        self.use_webrtc = _FakeVar(False)
        self.verbose = _FakeVar(False)
        self.package = _FakeVar(False)
        self.github_token = _FakeVar(github_token)


class _FakeStatusPanel:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def append(self, _message: str) -> None:
        self.messages.append(_message)


def _make_panel(build_type: str, github_token: str) -> BuildPanel:
    panel = BuildPanel.__new__(BuildPanel)
    panel.config_panel = _FakeConfigPanel(build_type, github_token)
    panel.status_panel = _FakeStatusPanel()
    return panel


def test_create_config_requires_token_for_non_os_build() -> None:
    panel = _make_panel("Release", "")

    with pytest.raises(ValidationError):
        panel.create_config()


def test_create_config_allows_os_build_without_token() -> None:
    panel = _make_panel("ReleaseOS", "")

    config = panel.create_config()
    assert config.build_type == "ReleaseOS"


def test_create_config_allows_non_os_build_with_token() -> None:
    panel = _make_panel("Release", "ghp_token")

    config = panel.create_config()
    assert config.build_type == "Release"
    assert config.github_token == "ghp_token"


def test_install_thread_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    panel = _make_panel("ReleaseOS", "")

    captured: dict[str, str] = {}

    def _fake_showerror(_title: str, message: str) -> None:
        captured["message"] = message

    monkeypatch.setattr("ui.build_panel.messagebox.showerror", _fake_showerror)
    panel._install_thread()

    assert "GitHub Token" in captured["message"]


def test_build_thread_skips_install_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    panel = _make_panel("ReleaseOS", "")

    monkeypatch.setattr("ui.build_panel.install_dependencies", lambda *_args: (_ for _ in ()).throw(AssertionError("install should not be called")))
    monkeypatch.setattr("ui.build_panel.configure_build", lambda *_args: None)
    monkeypatch.setattr("ui.build_panel.build_viewer", lambda *_args: None)
    monkeypatch.setattr("ui.build_panel.messagebox.showerror", lambda *_args: None)

    panel._build_thread()

    assert any("ueberspringe 'autobuild install'" in msg for msg in panel.status_panel.messages)
