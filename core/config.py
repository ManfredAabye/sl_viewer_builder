from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BuildConfig:
    viewer_path: Path
    autobuild_path: Path
    build_variables_path: Path
    build_type: str
    jobs: int
    clean_build: bool
    architecture: str = "64"
    avx2_optimize: bool = False
    use_openal: bool = True
    use_fmod: bool = False
    use_webrtc: bool = False
    verbose: bool = False
    package: bool = False
    github_token: str = ""
