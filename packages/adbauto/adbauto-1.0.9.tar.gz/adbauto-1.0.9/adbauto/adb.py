# adbauto/adb.py
import subprocess
import time
import sys, os
import importlib.resources as resources
import adbauto.scrcpy as scrcpy

## UTILS
def get_adb_path():
    """Gets the path to where the adb.exe is installed."""
    if sys.platform == "win32":
        return str(resources.files("adbauto").joinpath("bin/adb.exe"))
    else:
        raise RuntimeError("adbauto currently only bundles adb.exe for Windows")
    
def hidden_run(*args, **kwargs):
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if "startupinfo" not in kwargs:
            kwargs["startupinfo"] = si
    return subprocess.run(*args, **kwargs)

## END OF UTILS

def run_adb_command(args):
    """Run an adb command and return its stdout as string."""
    adb_path = get_adb_path()
    adb_dir = os.path.dirname(adb_path)
    result = hidden_run([adb_path] + args, capture_output=True, text=True, cwd=adb_dir)
    if result.returncode != 0:
        raise RuntimeError(f"ADB command failed: {' '.join(args)}\n{result.stderr.strip()}")
    return result.stdout.strip()

def start_adb_server():
    """Start the ADB server if it's not already running."""
    run_adb_command(["start-server"])
    print("ADB server started (or already running).")

def list_devices():
    """Return a list of connected device IDs."""
    output = run_adb_command(["devices"])
    lines = output.splitlines()
    return [line.split()[0] for line in lines[1:] if "device" in line]

def adb_connect_port(port):
    """Connect to an ADB server on a specific port."""
    try:
        run_adb_command(["connect", f"localhost:{port}"])
    except RuntimeError as e:
        print(f"Failed to connect to ADB server on port {port}: {e}")
        raise

def get_emulator_device(port=5555):
    """Connect to the ADB device on the specified port and return its device ID."""
    try:
        start_adb_server()
        adb_connect_port(port)
        devices = list_devices()

        target_id = f"localhost:{port}"
        if target_id not in devices and len(devices) == 0:
            raise RuntimeError(f"Device {target_id} not found after connection attempt.")
        elif target_id not in devices:
            print(f"Device {target_id} not found in the list of connected devices. Available devices: {devices}")
            return devices[0]

        print(f"Connected to device: {target_id}")
        return target_id
    except Exception as e:
        print(f"Error in get_emulator_device: {e}")
        raise


def shell(device_id, command):
    """Run a shell command on the target device and return its output."""
    return run_adb_command(["-s", device_id, "shell", command])

def pull(device_id, remote_path, local_path=None):
    """Pull a file from the device to the local machine."""
    return run_adb_command(["-s", device_id, "pull", remote_path, local_path])

def start_scrcpy(device_id):
    try:
        scrcpyClient = scrcpy.Client(device=device_id)
        scrcpyClient.max_fps = 5
        scrcpyClient.bitrate = 8000000
        scrcpyClient.start(daemon_threaded=True)
        while scrcpyClient.last_frame is None:
            time.sleep(0.1)
        return scrcpyClient
    except Exception as e:
        print(f"Error starting scrcpy: {e}")
        raise e

def stop_scrcpy(scrcpyClient):
    """Stop the scrcpy client."""
    scrcpyClient.stop()
    print("scrcpy client stopped.")
    return True