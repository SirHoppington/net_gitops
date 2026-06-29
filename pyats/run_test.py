import os
import sys
import time

import pyeapi
from pyats.topology import loader

TESTBED = os.path.join(os.path.dirname(__file__), "inventory", "testbed.yaml")

# cEOS eAPI is not up immediately after the topology syncs - poll for it.
BOOT_TIMEOUT = int(os.environ.get("PYATS_BOOT_TIMEOUT", "600"))
BOOT_INTERVAL = int(os.environ.get("PYATS_BOOT_INTERVAL", "15"))
PING_COUNT = int(os.environ.get("PYATS_PING_COUNT", "5"))


def _plain(value):
    """Return the plaintext of a pyATS Secret, or the value if already plain."""
    return getattr(value, "plaintext", value)


def _connect(device):
    eapi = device.connections["eapi"]
    creds = device.credentials["default"]
    return pyeapi.connect(
        transport="https",
        host=str(eapi["ip"]),
        port=int(eapi.get("port", 443)),
        username=str(_plain(creds["username"])),
        password=str(_plain(creds["password"])),
    )


def connect_when_ready(device):
    """Connect + confirm eAPI answers, retrying while cEOS boots."""
    deadline = time.time() + BOOT_TIMEOUT
    last_error = None
    while time.time() < deadline:
        try:
            node = _connect(device)
            version = node.execute(["show version"])["result"][0]
            print(f"{device.name}: eAPI up - {version['modelName']} "
                  f"{version['version']}")
            return node
        except Exception as exc:
            last_error = exc
            print(f"{device.name}: not ready yet ({exc}); retrying...")
            time.sleep(BOOT_INTERVAL)
    raise TimeoutError(f"eAPI never came up within {BOOT_TIMEOUT}s: {last_error}")


def assert_interface_up(device, node, intf):
    """Fail unless the link interface is UP/UP (Arista: connected + line up)."""
    status = node.execute([f"show interfaces {intf}"])
    iface = status["result"][0]["interfaces"][intf]
    admin = iface["interfaceStatus"]      # "connected" == admin-up + link-up
    line = iface["lineProtocolStatus"]    # "up"
    if admin != "connected" or line != "up":
        raise RuntimeError(
            f"{intf} not UP/UP: interfaceStatus={admin} lineProtocol={line}")
    print(f"{device.name}: {intf} UP/UP")


def check_reachability(device, node):
    """Per neighbour: assert link UP/UP, then ping the peer ip via eAPI."""
    neighbors = device.custom.get("neighbors", {}) if device.custom else {}
    for name, info in neighbors.items():
        assert_interface_up(device, node, info["interface"])
        ip = info["ip"]
        # ping needs privileged mode; prepend enable, read the ping result (last).
        output = node.execute(
            ["enable", f"ping {ip} repeat {PING_COUNT}"], encoding="text")
        text = output["result"][-1]["output"]
        if "0% packet loss" not in text:
            raise RuntimeError(f"ping {name} ({ip}) failed:\n{text}")
        print(f"{device.name}: reachability to {name} ({ip}) OK")


def check_device(device):
    node = connect_when_ready(device)
    check_reachability(device, node)


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
        sys.exit(f"checks failed for: {', '.join(failures)}")
    print("All devices passed eAPI + reachability checks.")


if __name__ == "__main__":
    main()
