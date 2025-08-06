#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from mcmicroprep.microscopes.base import MicroscopeHandler


class OlympusHandler(MicroscopeHandler):
    name = "olympus"

    def restructure_raw(self, image_root: Path):
        for slide in image_root.iterdir():
            if not slide.is_dir() or slide.name in [
                "dataset",
                "templates",
                "microscopes",
            ]:
                continue
            raw = slide / "raw"
            misc = slide / "misc_files"
            raw.mkdir(exist_ok=True)
            misc.mkdir(exist_ok=True)

            for item in list(slide.iterdir()):
                if item.is_dir() and item.name.endswith("_frames"):
                    item.rename(raw / item.name)
                elif item.name not in ["raw", "misc_files"]:
                    item.rename(misc / item.name)

            # Only run companion script if missing the OME file
            for frame in raw.iterdir():
                ome = frame / "image.companion.ome"
                if not ome.exists():
                    # Invoke installed module, not script in cwd
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "mcmicroprep.companion_script",
                            str(frame),
                        ],
                        check=True,
                    )

    def params_template(self) -> dict:
        # Not used when file-based params selection is preferred
        return {}
