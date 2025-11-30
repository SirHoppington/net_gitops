from pyats.topology import loader
import pyeapi
import json

try:
    testbed = loader.load('testbed.yaml')
    device = testbed.devices['arista1']

    # Connect via CLI (optional)
    device.connect(alias='cli', via='cli')
    print("Connected to Arista via CLI.")

    # Connect via eAPI using pyeapi
    node = pyeapi.connect(
        transport='https',
        host=device.connections['eapi']['ip'],
        username=device.connections['eapi']['username'],
        password=device.connections['eapi']['password'],
        port=device.connections['eapi'].get('port', 443)
    )

    # Run a command and get structured JSON
    response = node.execute(['show version'])
    print("Arista EOS Version Info:")
    print(json.dumps(response, indent=2))

    # Example: Get interface status
    interfaces = node.execute(['show interfaces status'])
    print("\nInterface Status:")
    print(json.dumps(interfaces, indent=2))

except Exception as e:
    print(f"Error: {e}")