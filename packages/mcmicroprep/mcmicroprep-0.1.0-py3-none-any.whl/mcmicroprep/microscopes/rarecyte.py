#!/usr/bin/env python3
from pathlib import Path
from mcmicroprep.microscopes.base import MicroscopeHandler


class RareCyteHandler(MicroscopeHandler):
    name = "rarecyte"

    def restructure_raw(self, image_root: Path):
        for slide in image_root.iterdir():
            if not slide.is_dir() or slide.name in ["templates", "microscopes"]:
                continue
            raw = slide / "raw"
            misc = slide / "misc_files"
            raw.mkdir(exist_ok=True)
            misc.mkdir(exist_ok=True)

            # Flatten: move all .rcpnl files directly into raw/
            for path in slide.rglob("*.rcpnl"):
                if raw in path.parents or misc in path.parents:
                    continue
                dest = raw / path.name
                path.rename(dest)

            # Move all other top-level items to misc_files/
            for item in list(slide.iterdir()):
                if item.name not in ["raw", "misc_files"]:
                    item.rename(misc / item.name)

    def params_template(self) -> dict:
        return {}
