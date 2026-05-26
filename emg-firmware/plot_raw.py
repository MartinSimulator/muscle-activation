import pandas as pd
import matplotlib.pyplot as plt

file = input("CSV file to plot (e.g. data/mvc_attempt1.csv): ")
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