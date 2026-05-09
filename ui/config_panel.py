from pathlib import Path
import os
from tkinter import BooleanVar
from tkinter import StringVar
from tkinter import filedialog

from ttkbootstrap import Button
from ttkbootstrap import Checkbutton
from ttkbootstrap import Combobox
from ttkbootstrap import Entry
from ttkbootstrap import Frame
from ttkbootstrap import Label

from core.repository import get_default_autobuild_target_dir
from core.repository import get_default_build_variables_target_dir
from core.repository import get_default_viewer_target_dir
from core.repository import SUPPORTED_VIEWER_REPOS


class ConfigPanel(Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)

        self.viewer_path = StringVar()
        self.autobuild_path = StringVar()
        self.build_variables_path = StringVar()
        self.viewer_name = StringVar(value="Second Life Viewer")
        self.viewer_repo_url = StringVar()
        self.build_type = StringVar(value="Release")
        self.jobs = StringVar(value="4")
        self.architecture = StringVar(value="64")
        self.clean_build = BooleanVar(value=False)
        self.avx2_optimize = BooleanVar(value=False)
        self.use_openal = BooleanVar(value=True)
        self.use_fmod = BooleanVar(value=False)
        self.use_webrtc = BooleanVar(value=False)
        self.verbose = BooleanVar(value=False)
        self.package = BooleanVar(value=False)
        self.github_token = StringVar(value=os.environ.get("AUTOBUILD_GITHUB_TOKEN", ""))
        self._project_root = Path(__file__).resolve().parents[1]
        self._last_suggested_viewer_path = ""

        Label(self, text="Viewer").grid(row=0, column=0, sticky="w")
        Combobox(
            self,
            textvariable=self.viewer_name,
            values=list(SUPPORTED_VIEWER_REPOS.keys()),
            width=30,
            state="readonly",
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        Label(self, text="Repo URL").grid(row=1, column=0, sticky="w")
        Entry(
            self,
            textvariable=self.viewer_repo_url,
            width=60,
            state="readonly",
        ).grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        Label(self, text="Viewer Pfad").grid(row=2, column=0, sticky="w")
        Entry(self, textvariable=self.viewer_path, width=60).grid(
            row=2,
            column=1,
            padx=5,
            pady=5,
        )
        Button(self, text="Browse", command=self.browse_viewer_path).grid(
            row=2,
            column=2,
            padx=5,
            pady=5,
            sticky="w",
        )

        Label(self, text="Autobuild Pfad").grid(row=3, column=0, sticky="w")
        Entry(self, textvariable=self.autobuild_path, width=60).grid(
            row=3,
            column=1,
            padx=5,
            pady=5,
        )
        Button(self, text="Browse", command=self.browse_autobuild_path).grid(
            row=3,
            column=2,
            padx=5,
            pady=5,
            sticky="w",
        )

        Label(self, text="Build Variables Pfad").grid(row=4, column=0, sticky="w")
        Entry(self, textvariable=self.build_variables_path, width=60).grid(
            row=4,
            column=1,
            padx=5,
            pady=5,
        )
        Button(self, text="Browse", command=self.browse_build_variables_path).grid(
            row=4,
            column=2,
            padx=5,
            pady=5,
            sticky="w",
        )

        Label(self, text="Build Typ").grid(row=5, column=0, sticky="w")
        Combobox(
            self,
            textvariable=self.build_type,
            values=[
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
            ],
            width=20,
            state="readonly",
        ).grid(row=5, column=1, sticky="w")

        Label(self, text="Architektur").grid(row=6, column=0, sticky="w")
        Combobox(
            self,
            textvariable=self.architecture,
            values=["32", "64"],
            width=5,
            state="readonly",
        ).grid(row=6, column=1, sticky="w")

        Label(self, text="Jobs").grid(row=7, column=0, sticky="w")
        Entry(self, textvariable=self.jobs, width=10).grid(
            row=7,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="Clean Build", variable=self.clean_build).grid(
            row=8,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="AVX2 Optimierung", variable=self.avx2_optimize).grid(
            row=9,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="OpenAL verwenden", variable=self.use_openal).grid(
            row=10,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="FMOD verwenden", variable=self.use_fmod).grid(
            row=11,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="WebRTC verwenden", variable=self.use_webrtc).grid(
            row=12,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="Paketieren", variable=self.package).grid(
            row=13,
            column=1,
            sticky="w",
        )

        Checkbutton(self, text="Verbose Output", variable=self.verbose).grid(
            row=14,
            column=1,
            sticky="w",
        )

        Label(self, text="GitHub Token").grid(row=15, column=0, sticky="w")
        Entry(self, textvariable=self.github_token, width=60, show="*").grid(
            row=15,
            column=1,
            padx=5,
            pady=5,
        )

        self._apply_initial_path_suggestions()
        self.viewer_name.trace_add("write", self._on_viewer_changed)

    def _apply_initial_path_suggestions(self) -> None:
        self.viewer_repo_url.set(SUPPORTED_VIEWER_REPOS[self.viewer_name.get()])

        viewer_suggestion = str(
            get_default_viewer_target_dir(self.viewer_name.get(), self._project_root)
        )

        if not self.viewer_path.get().strip():
            self.viewer_path.set(viewer_suggestion)

        self._last_suggested_viewer_path = viewer_suggestion

        if not self.autobuild_path.get().strip():
            self.autobuild_path.set(
                str(get_default_autobuild_target_dir(self._project_root))
            )

        if not self.build_variables_path.get().strip():
            self.build_variables_path.set(
                str(get_default_build_variables_target_dir(self._project_root))
            )

    def _on_viewer_changed(self, *_: object) -> None:
        self.viewer_repo_url.set(SUPPORTED_VIEWER_REPOS[self.viewer_name.get()])

        current_value = self.viewer_path.get().strip()
        next_suggestion = str(
            get_default_viewer_target_dir(self.viewer_name.get(), self._project_root)
        )

        if not current_value or current_value == self._last_suggested_viewer_path:
            self.viewer_path.set(next_suggestion)

        self._last_suggested_viewer_path = next_suggestion

    def browse_viewer_path(self) -> None:
        selected = filedialog.askdirectory(title="Viewer-Verzeichnis auswaehlen")

        if selected:
            self.viewer_path.set(selected)

    def browse_autobuild_path(self) -> None:
        selected = filedialog.askdirectory(title="Autobuild-Verzeichnis auswaehlen")

        if selected:
            self.autobuild_path.set(selected)

    def browse_build_variables_path(self) -> None:
        selected = filedialog.askdirectory(title="Build Variables-Verzeichnis auswaehlen")

        if selected:
            self.build_variables_path.set(selected)
