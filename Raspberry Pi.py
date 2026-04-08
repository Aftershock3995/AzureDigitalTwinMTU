import asyncio
import urllib.request
import json
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

URL = "http://192.168.10.1:8000/coords.txt"

CONNECTION_STRING = "HostName=yourhostname;DeviceId=yourdeviceid;SharedAccessKey=youraccesskey"

SEND_INTERVAL = 1

def get_coords():
    try:
        with urllib.request.urlopen(URL, timeout=1) as response:
            data = response.read().decode().strip()

            if data:
                parts = data.split(",")

                if len(parts) == 3:
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        z = float(parts[2])
                        return x, y, z
                    except ValueError:
                        print("Invalid numeric values from Mach3:", data)
                        return None
                else:
                    print("Unexpected format:", data)
                    return None
    except Exception as e:
        print(f"HTTP read error: {e}")
        return None

async def send_recurring_telemetry(device_client):
    await device_client.connect()
    print("Connected to Azure IoT Hub")

    while True:
        coords = get_coords()

        if coords:
            x, y, z = coords

            payload = {
                "x": x,
                "y": y,
                "z": z
            }

            try:
                msg = Message(json.dumps(payload))
                msg.content_encoding = "utf-8"
                msg.content_type = "application/json"

                print(f"Sending → X:{x:.3f} Y:{y:.3f} Z:{z:.3f}")

                await device_client.send_message(msg)

            except Exception as e:
                print(f"Send failed: {e}")

        else:
            print("Waiting for valid Mach3 data...")

        await asyncio.sleep(SEND_INTERVAL)

def main():
    print("Mach3 → Azure IoT Telemetry Starting...")
    print("Press Ctrl+C to exit\n")

    device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(send_recurring_telemetry(device_client))

    except KeyboardInterrupt:
        print("\nUser exited")

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

    finally:
        print("Shutting down client...")
        loop.run_until_complete(device_client.shutdown())
        loop.close()

if __name__ == "__main__":
    main()
