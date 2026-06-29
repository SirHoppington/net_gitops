import json
import os
import sys
import time

import pyeapi
from pyats.topology import loader

TESTBED = os.path.join(os.path.dirname(__file__), "inventory", "testbed.yaml")

# cEOS eAPI is not up immediately after the topology syncs - poll for it.
BOOT_TIMEOUT = int(os.environ.get("PYATS_BOOT_TIMEOUT", "600"))
BOOT_INTERVAL = int(os.environ.get("PYATS_BOOT_INTERVAL", "15"))


def _plain(value):
    """Return the plaintext of a pyATS Secret, or the value if already plain."""
    return getattr(value, "plaintext", value)


def _connect(device):
    eapi = device.connections["eapi"]
    creds = device.credentials["default"]
    # pyATS stores ip as an IPv4Address and password as a SecretString; pyeapi
    # needs plain str/int or it throws "expected string or bytes-like object".
    return pyeapi.connect(
        transport="https",
        host=str(eapi["ip"]),
        port=int(eapi.get("port", 443)),
        username=str(_plain(creds["username"])),
        password=str(_plain(creds["password"])),
    )


def check_device(device):
    deadline = time.time() + BOOT_TIMEOUT
    last_error = None
    while time.time() < deadline:
        try:
            node = _connect(device)
            version = node.execute(["show version"])
            print(f"{device.name}: connected via eAPI")
            print(json.dumps(version["result"], indent=2))
            return
        except Exception as exc:  # noqa: BLE001 - retry until boot completes
            last_error = exc
            print(f"{device.name}: not ready yet ({exc}); retrying...")
            time.sleep(BOOT_INTERVAL)
    raise TimeoutError(f"eAPI never came up within {BOOT_TIMEOUT}s: {last_error}")


def main():
    testbed = loader.load(TESTBED)
    failures = []
    for name, device in testbed.devices.items():
        try:
            check_device(device)
        except Exception as exc:  # noqa: BLE001 - report any device, keep going
            failures.append(name)
            print(f"{name}: FAILED - {exc}", file=sys.stderr)
    if failures:
        sys.exit(f"eAPI checks failed for: {', '.join(failures)}")
    print("All devices passed eAPI checks.")


if __name__ == "__main__":
    main()
