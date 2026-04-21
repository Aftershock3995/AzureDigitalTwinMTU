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
        # Note: urllib is blocking; in high-perf apps, consider 'aiohttp'
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

        # We create the payload here. 
        # ArcOK is set to False every loop iteration as requested.
        if coords:
            x, y, z = coords
            payload = {
                "x": x,
                "y": y,
                "z": z,
                "ArcOK": False  # Constant false status
            }
        else:
            # If coordinates fail, we still send the ArcOK status 
            # or you can choose to skip. Here we skip to match your original logic.
            print("Waiting for valid Mach3 data...")
            await asyncio.sleep(SEND_INTERVAL)
            continue

        try:
            msg = Message(json.dumps(payload))
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"

            print(f"Sending → X:{x:.3f} Y:{y:.3f} Z:{z:.3f} | ArcOK: False")

            await device_client.send_message(msg)

        except Exception as e:
            print(f"Send failed: {e}")

        await asyncio.sleep(SEND_INTERVAL)

def main():
    print("Mach3 → Azure IoT Telemetry Starting...")
    print("Press Ctrl+C to exit\n")

    device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    # Updated way to handle the event loop for modern Python compatibility
    try:
        asyncio.run(send_recurring_telemetry(device_client))
    except KeyboardInterrupt:
        print("\nUser exited")
    finally:
        print("Shutting down...")

if __name__ == "__main__":
    main()
