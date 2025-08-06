from pathlib import Path
import shutil
from mcmicroprep.microscopes.base import MicroscopeHandler


class CorePipeline:
    def __init__(self, handler: MicroscopeHandler, image_root: Path):
        self.handler = handler
        self.image_root = Path(image_root)
        self.templates = Path(__file__).parent / "templates"

    def run(self):
        # 1️⃣ Organize raw imagery in-place
        self.handler.restructure_raw(self.image_root)
        # 2️⃣ Enforce dataset structure (expect image_root to be the dataset root)
        # No additional moving of slide folders; image_root should contain slide dirs directly.
        # 3️⃣ Generate boilerplate
        self._generate_boilerplate()

    def _generate_boilerplate(self):
        # Copy common boilerplate templates
        common = self.templates / "common"
        for fname in [
            "batch_submission.sh",
            "mcmicro_template.sh",
            "base.config",
            "markers.csv",
        ]:
            src = common / fname
            dst = self.image_root / fname
            if not dst.exists():
                shutil.copy(src, dst)
                if dst.suffix == ".sh":
                    dst.chmod(dst.stat().st_mode | 0o111)

        # Copy microscope-specific params YAML
        params_src = self.templates / "params" / f"{self.handler.name}.yml"
        params_dst = self.image_root / "params.yml"
        if params_src.exists() and not params_dst.exists():
            shutil.copy(params_src, params_dst)
