import serial
import csv
import time

PORT = '/dev/tty.usbserial-0001'
BAUD = 115200

exercise = input("Exercise name: ")
set_num  = input("Set number: ")
filename = f"{exercise}_set{set_num}.csv"

print(f"Recording to {filename} — press Enter to start, Ctrl+C to stop")
input()

with serial.Serial(PORT, BAUD) as ser, open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp_us', 'adc_raw'])
    print("Recording... Ctrl+C to stop")
    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if ',' in line:
                parts = line.split(',')
                writer.writerow(parts)
    except KeyboardInterrupt:
        print(f"\nSaved to {filename}")