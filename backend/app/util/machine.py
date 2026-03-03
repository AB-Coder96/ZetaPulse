import json
import os
import platform
import subprocess


def _cmd(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def get_machine_profile_json() -> str:
    profile = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu": _cmd(["bash", "-lc", "lscpu | sed -n '1,20p'"]) or "",
        "kernel": platform.release(),
        "env": {"ENV": os.getenv("ENV", "dev")},
    }
    return json.dumps(profile, ensure_ascii=False)
