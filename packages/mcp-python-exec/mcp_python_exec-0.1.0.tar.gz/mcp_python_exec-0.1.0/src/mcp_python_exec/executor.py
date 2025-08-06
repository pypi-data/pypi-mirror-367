import os
import uuid
import subprocess
from dataclasses import dataclass
from typing import Any, IO, Callable
from functools import cached_property

from PIL import Image

from pychroot import Chroot


return_types = None | str | Image.Image


@dataclass(frozen=True)
class ChrootExecutor:
    name: str | None = None

    uid: int = 65534
    gid: int = 65534
    data_dir: str = "data"
    chroot_data: str = "/mcp"
    home: str = "/tmp/mcp_python_exec"

    output_img_path: str = "img"
    default_img_name: str = "show.png"

    @property
    def mountpoints(self) -> dict[str, dict[str, Any]]:
        return {
            '/bin': {"readonly": True},
            '/lib': {"readonly": True},
            '/lib64': {"readonly": True, "optional": True, "create": True},
            #'/usr/libexec': {"readonly": True, "optional": True, "create": True},
            'tmpfs:/tmp': {},

            self.home: {},
            '/usr/local/bin/uv': {"readonly": True, "optional": True, "create": True},
            '/usr/local/bin/uvx': {"readonly": True, "optional": True, "create": True},
        }

    @cached_property
    def chroot_path(self) -> str:
        name = self.name or str(uuid.uuid4())
        return os.path.join(self.data_dir, name)

    @property
    def chroot_data_path(self) -> str:
        return os.path.join(self.chroot_path, self.chroot_data.lstrip("/"))

    @property
    def chroot_output_img_path(self) -> str:
        return os.path.join(self.chroot_data_path, self.output_img_path)

    def __post_init__(self):
        # Create chroot directory & data directory inside chroot
        os.makedirs(self.chroot_data_path, exist_ok=True)
        os.chown(self.chroot_data_path, self.uid, -1)
        os.makedirs(self.chroot_output_img_path, exist_ok=True)
        os.chown(self.chroot_output_img_path, self.uid, -1)

        # Ensure uv cache directory exists
        if not os.path.exists(self.home):
            os.makedirs(self.home)
            os.chown(self.home, self.uid, self.gid)
            os.chmod(self.home, 0o7750)

    def _exec_raw(self, function: Callable[[], None | list[return_types]]) -> list[return_types]:
        with Chroot(self.chroot_path, mountpoints=self.mountpoints) as child:
            # Environment setup
            os.chdir(self.chroot_data)
            os.environ["HOME"] = self.home

            # Drop privileges
            if self.gid >= 0:
                os.setgid(self.gid)
            os.setuid(self.uid)

            # Execute & capture output
            fn_return = function()

        # NB: Local variables are not propagated back from the chroot context
        fn_return = child.locals.get("fn_return", None)       
        values = [*(fn_return or [])]

        # Check if an image was created
        for file in os.listdir(self.chroot_output_img_path):
            image_path = os.path.join(self.chroot_output_img_path, file)
            
            Image.WARN_POSSIBLE_FORMATS = True
            img = Image.open(image_path)
            #img.load()
            values.append(img)
            
            os.remove(image_path)

        return values
    
    def exec_shell(self, shell_code: str) -> list[return_types]:
        def function():
            proc = subprocess.run(shell_code, shell=True, capture_output=True)
            return [
                "STDERR: " + proc.stderr.decode(errors="replace"),
                "STDOUT: " + proc.stdout.decode(errors="replace")]
        
        return self._exec_raw(function)

    def open(self, path: str, mode: str = "r") -> IO:
        root = self.chroot_path if path.startswith("/") else self.chroot_data_path
        return open(os.path.join(root, path.lstrip("/")), mode)

    def exec_venv(self, python_code: str, requirements: list[str] | None = None) -> list[return_types]:
        with self.open("scratchpad.py", "w") as f:
            f.write(python_code)

        if requirements is None:
            requirements = ["matplotlib"]
        
        cmd = (
            "uv venv"
            " && source .venv/bin/activate"
            + (
                f" && uv pip install --link-mode symlink {' '.join(requirements)}"
                # Patch matplotlib FigureManagerBase.show to save figure to file
                rf""" && sed -i -e '/    def show(self):/!b' -e 'n;/        import matplotlib.pyplot as plt/b' -e 'i\        import matplotlib.pyplot as plt\n        return plt.savefig("{self.output_img_path}/{self.default_img_name}")' .venv/lib/*/site-packages/matplotlib/backend_bases.py"""
                if requirements else ""
            ) +
            " && python scratchpad.py"
        )
        return self.exec_shell(cmd)
