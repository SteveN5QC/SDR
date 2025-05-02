import csv
import datetime
import matplotlib.pyplot as plt
import statistics

# --- CONFIGURATION ---
CSV_FILE = "output.csv"    # CSV file from rtl_power
THRESHOLD_DBM = -70         # Signal detected if stronger than this
OUTPUT_FILE = "detected_events.txt"

# --- HELPER FUNCTION ---
def parse_rtl_power_line(row):
    date_str = row[0].strip()
    time_str = row[1].strip()
    timestamp = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    freq_start = float(row[2])
    freq_stop = float(row[3])
    freq_step = float(row[4])
    powers = []
    for val in row[6:]:
        try:
            powers.append(float(val))
        except ValueError:
            powers.append(float('nan'))  # handle 'nan' safely
    return timestamp, freq_start, freq_stop, freq_step, powers

# --- MAIN SCRIPT ---
print(f"Processing {CSV_FILE}...")

active_events = []
power_values = []  # <-- Create it here

with open(CSV_FILE, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 7:
            continue  # skip invalid rows

        timestamp, freq_start, freq_stop, freq_step, powers = parse_rtl_power_line(row)

        for idx, power in enumerate(powers):
            if not (power != power):  # skip NaNs
                if power > THRESHOLD_DBM:
                    freq = freq_start + (idx * freq_step)
                    active_events.append((timestamp, freq, power))
                    power_values.append(power)  # collect powers for stats

print(f"Detected {len(active_events)} events.")

# Save to file
with open(OUTPUT_FILE, "w") as out:
    out.write("Timestamp,Freq_MHz,Power_dBm\n")
    for event in active_events:
        out.write(f"{event[0]},{event[1]:.6f},{event[2]:.1f}\n")

# --- CALCULATE STATISTICS ---
if power_values:
    mean_power = statistics.mean(power_values)
    min_power = min(power_values)
    max_power = max(power_values)

    if len(power_values) > 1:
        stdev_power = statistics.stdev(power_values)
        print("\n=== Signal Statistics ===")
        print(f"Mean Power: {mean_power:.2f} dBm")
        print(f"Standard Deviation: {stdev_power:.2f} dB")
        print(f"Mean + 3?: {mean_power + 3 * stdev_power:.2f} dBm")
        print(f"Mean - 3?: {mean_power - 3 * stdev_power:.2f} dBm")
    else:
        stdev_power = 0
        print("\n=== Signal Statistics ===")
        print(f"Mean Power: {mean_power:.2f} dBm")
        print("Not enough data points for standard deviation.")

    print(f"Minimum Power: {min_power:.2f} dBm")
    print(f"Maximum Power: {max_power:.2f} dBm")

    # --- PLOT HISTOGRAM ---
    plt.figure(figsize=(10,6))
    plt.hist(power_values, bins=50, color='skyblue', edgecolor='black')
    plt.axvline(mean_power, color='red', linestyle='dashed', linewidth=1.5, label=f"Mean ({mean_power:.1f} dBm)")
    
    if len(power_values) > 1:
        plt.axvline(mean_power + 3 * stdev_power, color='green', linestyle='dashed', linewidth=1.5, label=f"Mean + 3?")
        plt.axvline(mean_power - 3 * stdev_power, color='orange', linestyle='dashed', linewidth=1.5, label=f"Mean - 3?")
    
    plt.title('Distribution of Signal Strengths')
    plt.xlabel('Power (dBm)')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

else:
    print("No valid power values found!")
