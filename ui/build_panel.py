import threading
from pathlib import Path
from tkinter import messagebox

from ttkbootstrap import Button
from ttkbootstrap import Frame

from core.builder import build_viewer
from core.builder import clean_build_artifacts
from core.builder import configure_build
from core.builder import install_dependencies
from core.builder import package_viewer
from core.config import BuildConfig
from core.exceptions import ValidationError
from core.repository import AUTOBUILD_REPO_URL
from core.repository import BUILD_VARIABLES_REPO_URL
from core.repository import clone_or_update_repository
from core.repository import get_viewer_repo_url
from core.validator import validate_build_type
from core.validator import validate_directory
from core.validator import validate_jobs


class BuildPanel(Frame):
    def __init__(self, master, config_panel, status_panel):
        super().__init__(master, padding=10)

        self.config_panel = config_panel
        self.status_panel = status_panel

        download_viewer_button = Button(
            self,
            text="Download Viewer",
            style="secondary.TButton",
            command=self.start_download_viewer,
        )
        download_viewer_button.pack(side="left", padx=5)

        download_autobuild_button = Button(
            self,
            text="Download Autobuild",
            style="secondary.TButton",
            command=self.start_download_autobuild,
        )
        download_autobuild_button.pack(side="left", padx=5)

        download_variables_button = Button(
            self,
            text="Download Build Variables",
            style="secondary.TButton",
            command=self.start_download_build_variables,
        )
        download_variables_button.pack(side="left", padx=5)

        configure_button = Button(
            self,
            text="Configure",
            style="info.TButton",
            command=self.start_configure,
        )
        configure_button.pack(side="left", padx=5)

        install_button = Button(
            self,
            text="Install",
            style="info.TButton",
            command=self.start_install,
        )
        install_button.pack(side="left", padx=5)

        build_button = Button(
            self,
            text="Build",
            style="success.TButton",
            command=self.start_build,
        )
        build_button.pack(side="left", padx=5)

    def create_config(self) -> BuildConfig:
        build_type = validate_build_type(self.config_panel.build_type.get())
        github_token = self.config_panel.github_token.get().strip()

        if not github_token and not build_type.endswith("OS"):
            raise ValidationError(
                "Dieser Build-Typ nutzt proprietaere Pakete. "
                "Bitte GitHub Token setzen oder Build-Typ 'ReleaseOS'/'RelWithDebInfoOS' verwenden."
            )

        return BuildConfig(
            viewer_path=validate_directory(
                self.config_panel.viewer_path.get(),
                "Viewer Pfad",
            ),
            autobuild_path=validate_directory(
                self.config_panel.autobuild_path.get(),
                "Autobuild Pfad",
            ),
            build_variables_path=validate_directory(
                self.config_panel.build_variables_path.get(),
                "Build Variables Pfad",
            ),
            build_type=build_type,
            jobs=validate_jobs(self.config_panel.jobs.get()),
            clean_build=self.config_panel.clean_build.get(),
            architecture=self.config_panel.architecture.get(),
            avx2_optimize=self.config_panel.avx2_optimize.get(),
            use_openal=self.config_panel.use_openal.get(),
            use_fmod=self.config_panel.use_fmod.get(),
            use_webrtc=self.config_panel.use_webrtc.get(),
            verbose=self.config_panel.verbose.get(),
            package=self.config_panel.package.get(),
            github_token=github_token,
        )

    def append_status(self, message: str) -> None:
        self.status_panel.append(message)

    def _resolve_target_path(self, value: str, name: str) -> Path:
        if not value.strip():
            raise ValidationError(f"{name} darf nicht leer sein")
        return Path(value)

    def start_download_viewer(self) -> None:
        threading.Thread(target=self._download_viewer_thread, daemon=True).start()

    def start_download_autobuild(self) -> None:
        threading.Thread(target=self._download_autobuild_thread, daemon=True).start()

    def start_download_build_variables(self) -> None:
        threading.Thread(target=self._download_build_variables_thread, daemon=True).start()

    def start_configure(self) -> None:
        threading.Thread(target=self._configure_thread, daemon=True).start()

    def start_install(self) -> None:
        threading.Thread(target=self._install_thread, daemon=True).start()

    def start_build(self) -> None:
        threading.Thread(target=self._build_thread, daemon=True).start()

    def _configure_thread(self) -> None:
        try:
            config = self.create_config()
            if config.clean_build:
                clean_build_artifacts(config, self.append_status)
            configure_build(config, self.append_status)
            self.append_status("Konfiguration abgeschlossen")
        except Exception as error:
            messagebox.showerror("Fehler", str(error))

    def _install_thread(self) -> None:
        try:
            config = self.create_config()
            if not config.github_token:
                raise ValidationError(
                    "Install ohne GitHub Token ist nicht verfuegbar. "
                    "Nutze fuer OSS-Build den Build-Button mit ReleaseOS/RelWithDebInfoOS."
                )
            install_dependencies(config, self.append_status)
            self.append_status("Install abgeschlossen")
        except Exception as error:
            messagebox.showerror("Fehler", str(error))

    def _build_thread(self) -> None:
        try:
            config = self.create_config()
            if config.clean_build:
                clean_build_artifacts(config, self.append_status)
            if config.github_token:
                install_dependencies(config, self.append_status)
                self.append_status("Install abgeschlossen")
            else:
                self.append_status(
                    "Kein GitHub Token gesetzt: ueberspringe 'autobuild install' und baue OSS-Konfiguration."
                )
            configure_build(config, self.append_status)
            self.append_status("Konfiguration abgeschlossen")
            build_viewer(config, self.append_status)
            if config.package:
                package_viewer(config, self.append_status)
                self.append_status("Paketierung abgeschlossen")
            self.append_status("Build abgeschlossen")
        except Exception as error:
            messagebox.showerror("Fehler", str(error))

    def _download_viewer_thread(self) -> None:
        try:
            viewer_name = self.config_panel.viewer_name.get()
            repo_url = get_viewer_repo_url(viewer_name)
            target = self._resolve_target_path(
                self.config_panel.viewer_path.get(),
                "Viewer Pfad",
            )
            clone_or_update_repository(
                repo_url,
                target,
                self.append_status,
            )
            self.append_status(f"{viewer_name} Download abgeschlossen")
        except Exception as error:
            messagebox.showerror("Fehler", str(error))

    def _download_autobuild_thread(self) -> None:
        try:
            target = self._resolve_target_path(
                self.config_panel.autobuild_path.get(),
                "Autobuild Pfad",
            )
            clone_or_update_repository(
                AUTOBUILD_REPO_URL,
                target,
                self.append_status,
            )
            self.append_status("Autobuild Download abgeschlossen")
        except Exception as error:
            messagebox.showerror("Fehler", str(error))

    def _download_build_variables_thread(self) -> None:
        try:
            target = self._resolve_target_path(
                self.config_panel.build_variables_path.get(),
                "Build Variables Pfad",
            )
            clone_or_update_repository(
                BUILD_VARIABLES_REPO_URL,
                target,
                self.append_status,
            )
            self.append_status("Build Variables Download abgeschlossen")
        except Exception as error:
            messagebox.showerror("Fehler", str(error))
