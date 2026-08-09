"""Record sEMG samples from the ESP32 over serial.

Buffers samples in memory during the set, then writes the CSV once at stop.
Avoids per-sample disk I/O, which was causing USB disconnects mid-set.

Important: close PlatformIO Serial Monitor (and any other serial tools)
before running this script. Only one program can own the USB port.
"""

from pathlib import Path

import csv
import serial
from serial.serialutil import SerialException

PORT = "/dev/tty.usbserial-0001"
BAUD = 115200
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def save_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp_us", "adc_raw"])
        writer.writerows(rows)
    print(f"Saved {len(rows)} samples to {path}")


exercise = input("Exercise name: ").strip()
set_num = input("Set number: ").strip()
DATA_DIR.mkdir(parents=True, exist_ok=True)
filename = DATA_DIR / f"{exercise}_set{set_num}.csv"

print(f"Recording to {filename}")
print("Press Enter to start, Ctrl+C to stop")
print(f"Make sure PlatformIO Serial Monitor is closed — it uses {PORT}")
input()

buffer: list[list[str]] = []

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except SerialException as exc:
    raise SystemExit(
        f"Could not open {PORT}.\n"
        "Another program is probably using it (PlatformIO Serial Monitor, "
        "Arduino Serial Monitor, screen, etc.).\n"
        "Close that monitor, then run this script again.\n"
        f"Details: {exc}"
    ) from exc

try:
    ser.reset_input_buffer()
    print("Recording... Ctrl+C to stop")
    try:
        while True:
            line = ser.readline()
            if not line:
                continue
            text = line.decode("utf-8", errors="ignore").strip()
            if "," in text:
                buffer.append(text.split(",", 1))
    except KeyboardInterrupt:
        pass
    except SerialException as exc:
        print(
            f"\nSerial connection lost ({exc}).\n"
            "Usually this means the port was opened by another program "
            "(e.g. PlatformIO Serial Monitor) or the board reset/unplugged."
        )
finally:
    ser.close()

save_csv(filename, buffer)
