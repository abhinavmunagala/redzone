import subprocess
import shutil
from abc import ABC, abstractmethod
from typing import List


def get_go_bin_path(tool_name: str) -> str:
    """
    Get absolute path to a Go binary.
    Checks Go bin directory first, then PATH.
    """
    try:
        result = subprocess.run(
            ["go", "env", "GOPATH"],
            capture_output=True, text=True
        )
        gopath = result.stdout.strip()
        go_bin = f"{gopath}/bin/{tool_name}"
        # check if exists at Go path
        result2 = subprocess.run(
            ["test", "-f", go_bin],
            capture_output=True
        )
        if result2.returncode == 0:
            return go_bin
    except:
        pass
    # fallback to PATH
    return shutil.which(tool_name) or tool_name


class ReconTool(ABC):

    binary_name: str = ""

    def is_available(self) -> bool:
        path = get_go_bin_path(self.binary_name)
        return shutil.which(path) is not None or \
               path != self.binary_name

    @abstractmethod
    def execute(self, target: str) -> List[dict]:
        pass