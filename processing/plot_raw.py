import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent.parent / "emg-firmware" / "data"

if len(sys.argv) > 1:
    file_input = sys.argv[1]
else:
    file_input = input("CSV file to plot (e.g. data/mvc_attempt1.csv): ").strip()


file_path = Path(file_input)
if not file_path.is_file():
    file_path = DATA_DIR / file_input
if not file_path.is_file():
    available = ", ".join(p.name for p in sorted(DATA_DIR.glob("*.csv")))
    raise FileNotFoundError(
        f"Could not find {file_input!r}. Tried {file_path}.\n"
        f"Available files in {DATA_DIR}: {available}"
    )
file = str(file_path)

df = pd.read_csv(file)

df['timestamp_us'] = pd.to_numeric(df['timestamp_us'], errors='coerce')
df['adc_raw'] = pd.to_numeric(df['adc_raw'], errors='coerce')
df = df.dropna()

df['timestamp_s'] = (df['timestamp_us'] - df['timestamp_us'].iloc[0]) / 1e6

plt.figure(figsize=(12, 4))
plt.plot(df['timestamp_s'], df['adc_raw'], linewidth=0.5)
plt.xlabel('time (seconds)')
plt.ylabel('adc raw value')
plt.title(file)
plt.tight_layout()
plt.show()