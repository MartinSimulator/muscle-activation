import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FS_HZ = 1000
ADC_MAX = 4095
ROW_RE = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*$")


def resolve_csv(file_input: str) -> Path:
    file_path = Path(file_input)
    if file_path.is_file():
        return file_path

    file_path = DATA_DIR / file_input
    if file_path.is_file():
        return file_path

    available = ", ".join(p.name for p in sorted(DATA_DIR.glob("*.csv")))
    raise FileNotFoundError(
        f"Could not find {file_input!r}. Tried {file_path}.\n"
        f"Available files in {DATA_DIR}: {available}"
    )


def load_emg_csv(path: Path) -> pd.DataFrame:
    """Load EMG CSV, skipping serial-corrupted lines."""
    timestamps = []
    adc_values = []
    skipped = 0

    with path.open(newline="") as f:
        header = f.readline()
        if "timestamp" not in header.lower() and "adc" not in header.lower():
            # No header - parse first line as data too.
            f.seek(0)

        for line in f:
            match = ROW_RE.match(line)
            if not match:
                skipped += 1
                continue

            ts = int(match.group(1))
            adc = int(match.group(2))
            if ts < 0 or not (0 <= adc <= ADC_MAX):
                skipped += 1
                continue

            timestamps.append(ts)
            adc_values.append(adc)

    if not adc_values:
        raise ValueError(f"No valid EMG rows found in {path}")

    df = pd.DataFrame({"timestamp_us": timestamps, "adc_raw": adc_values})

    # Drop a bogus leading timestamp (seen in some recordings).
    if len(df) >= 2 and df["timestamp_us"].iloc[0] < df["timestamp_us"].iloc[1] - 1_000_000:
        df = df.iloc[1:].reset_index(drop=True)

    # Serial noise often garbles timestamps. Prefer sample-index time if
    # timestamps are non-monotonic or imply an impossible duration.
    dts = df["timestamp_us"].diff().iloc[1:]
    mono_frac = float((dts >= 0).mean()) if len(dts) else 1.0
    median_dt = float(dts[dts > 0].median()) if (dts > 0).any() else float("nan")
    ts_span_s = float(df["timestamp_us"].iloc[-1] - df["timestamp_us"].iloc[0]) / 1e6
    sample_span_s = len(df) / FS_HZ
    duration_ok = sample_span_s * 0.5 <= ts_span_s <= sample_span_s * 3.0
    timestamps_ok = mono_frac >= 0.98 and 500 <= median_dt <= 2000 and duration_ok

    if timestamps_ok:
        df["timestamp_s"] = (df["timestamp_us"] - df["timestamp_us"].iloc[0]) / 1e6
        time_note = "time from timestamps"
    else:
        df["timestamp_s"] = df.index.to_numpy() / FS_HZ
        time_note = (
            f"time from sample index @ {FS_HZ} Hz "
            f"(timestamps look corrupted: mono={mono_frac:.0%}, "
            f"ts_span={ts_span_s:.1f}s vs ~{sample_span_s:.1f}s)"
        )

    print(f"Loaded {len(df)} valid rows from {path.name} (skipped {skipped})")
    print(time_note)
    return df


if len(sys.argv) > 1:
    file_input = sys.argv[1]
else:
    file_input = input("CSV file to plot (e.g. test_set1.csv): ").strip()

file_path = resolve_csv(file_input)
df = load_emg_csv(file_path)

plt.figure(figsize=(12, 4))
plt.plot(df["timestamp_s"], df["adc_raw"], linewidth=0.5)
plt.xlabel("time (seconds)")
plt.ylabel("adc raw value")
plt.title(str(file_path))
plt.tight_layout()
plt.show()
