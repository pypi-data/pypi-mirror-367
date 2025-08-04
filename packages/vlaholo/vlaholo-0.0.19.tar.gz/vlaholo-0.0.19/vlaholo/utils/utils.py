import datetime
from pathlib import Path
import subprocess
import sys
import numpy as np
import torch
from loguru import logger as logging
from datetime import datetime, timezone
import select
from os import path as osp
import copy
import os
from pathlib import Path


def get_safe_dtype(dtype: torch.dtype, device: str | torch.device):
    """
    mps is currently not compatible with float64
    """
    if isinstance(device, torch.device):
        device = device.type
    if device == "mps" and dtype == torch.float64:
        return torch.float32
    else:
        return dtype


def auto_select_torch_device() -> torch.device:
    """Tries to select automatically a torch device."""
    if torch.cuda.is_available():
        logging.info("Cuda backend detected, using cuda.")
        return torch.device("cuda")
    # elif torch.backends.mps.is_available():
    #     logging.info("Metal backend detected, using cuda.")
    #     return torch.device("mps")
    else:
        logging.warning(
            "No accelerated backend detected. Using default cpu, this will be slow."
        )
        return torch.device("cpu")


def is_torch_device_available(try_device: str) -> bool:
    try_device = str(try_device)  # Ensure try_device is a string
    if try_device == "cuda":
        return torch.cuda.is_available()
    elif try_device == "mps":
        return torch.backends.mps.is_available()
    elif try_device == "cpu":
        return True
    else:
        raise ValueError(
            f"Unknown device {try_device}. Supported devices are: cuda, mps or cpu."
        )


def is_amp_available(device: str):
    if device in ["cuda", "cpu"]:
        return True
    elif device == "mps":
        return False
    else:
        raise ValueError(f"Unknown device '{device}.")


def format_big_number(num, precision=0):
    suffixes = ["", "K", "M", "B", "T", "Q"]
    divisor = 1000.0

    for suffix in suffixes:
        if abs(num) < divisor:
            return f"{num:.{precision}f}{suffix}"
        num /= divisor

    return num


def _relative_path_between(path1: Path, path2: Path) -> Path:
    """Returns path1 relative to path2."""
    path1 = path1.absolute()
    path2 = path2.absolute()
    try:
        return path1.relative_to(path2)
    except ValueError:  # most likely because path1 is not a subpath of path2
        common_parts = Path(osp.commonpath([path1, path2])).parts
        return Path(
            "/".join(
                [".."] * (len(path2.parts) - len(common_parts))
                + list(path1.parts[len(common_parts) :])
            )
        )


def print_cuda_memory_usage():
    """Use this function to locate and debug memory leak."""
    import gc

    gc.collect()
    # Also clear the cache if you want to fully release the memory
    torch.cuda.empty_cache()
    print(
        "Current GPU Memory Allocated: {:.2f} MB".format(
            torch.cuda.memory_allocated(0) / 1024**2
        )
    )
    print(
        "Maximum GPU Memory Allocated: {:.2f} MB".format(
            torch.cuda.max_memory_allocated(0) / 1024**2
        )
    )
    print(
        "Current GPU Memory Reserved: {:.2f} MB".format(
            torch.cuda.memory_reserved(0) / 1024**2
        )
    )
    print(
        "Maximum GPU Memory Reserved: {:.2f} MB".format(
            torch.cuda.max_memory_reserved(0) / 1024**2
        )
    )


def capture_timestamp_utc():
    return datetime.now(timezone.utc)


def say(text, blocking=False):
    system = sys.platform.system()

    if system == "Darwin":
        cmd = ["say", text]

    elif system == "Linux":
        cmd = ["spd-say", text]
        if blocking:
            cmd.append("--wait")

    elif system == "Windows":
        cmd = [
            "PowerShell",
            "-Command",
            "Add-Type -AssemblyName System.Speech; "
            f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')",
        ]

    else:
        raise RuntimeError("Unsupported operating system for text-to-speech.")

    if blocking:
        subprocess.run(cmd, check=True)
    else:
        subprocess.Popen(
            cmd, creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0
        )


def log_say(text, play_sounds, blocking=False):
    logging.info(text)

    if play_sounds:
        say(text, blocking)


def get_channel_first_image_shape(image_shape: tuple) -> tuple:
    shape = copy(image_shape)
    if shape[2] < shape[0] and shape[2] < shape[1]:  # (h, w, c) -> (c, h, w)
        shape = (shape[2], shape[0], shape[1])
    elif not (shape[0] < shape[1] and shape[0] < shape[2]):
        raise ValueError(image_shape)

    return shape


def has_method(cls: object, method_name: str) -> bool:
    return hasattr(cls, method_name) and callable(getattr(cls, method_name))


def is_valid_numpy_dtype_string(dtype_str: str) -> bool:
    """
    Return True if a given string can be converted to a numpy dtype.
    """
    try:
        # Attempt to convert the string to a numpy dtype
        np.dtype(dtype_str)
        return True
    except TypeError:
        # If a TypeError is raised, the string is not a valid dtype
        return False


def enter_pressed() -> bool:
    return (
        select.select([sys.stdin], [], [], 0)[0] and sys.stdin.readline().strip() == ""
    )


def move_cursor_up(lines):
    """Move the cursor up by a specified number of lines."""
    print(f"\033[{lines}A", end="")


def get_safe_torch_device(try_device: str, log: bool = False) -> torch.device:
    """Given a string, return a torch.device with checks on whether the device is available."""
    try_device = str(try_device)
    match try_device:
        case "cuda":
            assert torch.cuda.is_available()
            device = torch.device("cuda")
        case "mps":
            assert torch.backends.mps.is_available()
            device = torch.device("mps")
        case "cpu":
            device = torch.device("cpu")
            if log:
                logging.warning("Using CPU, this will be slow.")
        case _:
            device = torch.device(try_device)
            if log:
                logging.warning(f"Using custom {try_device} device.")

    return device


def find_latest_checkpoint(output_dir):
    '''
    output_dir / checkpoints / last /pretrained_model
    find the last path 
    '''
    return Path(os.path.join(output_dir, 'checkpoints/last/pretrained_model'))