import csv
import datetime
import statistics
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
CSV_FILE = "output.csv"    # CSV file from rtl_power
THRESHOLD_DBM = -70          # Signal detected if stronger than this
OUTPUT_FILE = "detected_events.txt"
STRONG_OUTPUT_FILE = "strong_cluster_freqs.csv"
WEAK_OUTPUT_FILE = "weak_cluster_freqs.csv"

# --- HELPER FUNCTION ---
def parse_rtl_power_line(row):
    timestamp = datetime.datetime.strptime(row[0] + ' ' + row[1], "%Y-%m-%d %H:%M:%S")
    freq_start = float(row[2]) / 1e6  # Convert to MHz
    freq_end = float(row[3]) / 1e6
    freq_step = float(row[4]) / 1e6
    powers = []
    for val in row[6:]:
        try:
            powers.append(float(val))
        except ValueError:
            powers.append(float('nan'))
    return timestamp, freq_start, freq_step, powers

# --- MAIN SCRIPT ---
print(f"Processing {CSV_FILE}...")

active_events = []

with open(CSV_FILE, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 7:
            continue  # skip invalid rows

        timestamp, freq_start, freq_step, powers = parse_rtl_power_line(row)

        for idx, power in enumerate(powers):
            if not (power != power):  # Ignore NaN
                if power > THRESHOLD_DBM:
                    #  WAS:  freq = freq_start + (idx * freq_step)
                    #  THEN WAS:  freq = (freq_start + idx * freq_step) / 1e6  # Hz ? MHz
                    freq = freq_start + idx * freq_step



                    active_events.append((timestamp, freq, power))

print(f"Detected {len(active_events)} events.")

# Save all detected events
with open(OUTPUT_FILE, "w") as out:
    out.write("Timestamp,Freq_MHz,Power_dBm\n")
    for event in active_events:
        out.write(f"{event[0]},{event[1]:.6f},{event[2]:.1f}\n")

# --- ANALYZE CLUSTERS ---
strong_cluster_freqs = []
weak_cluster_freqs = []
all_powers = []

for event in active_events:
    timestamp, freq, power = event
    all_powers.append(power)
    if power > -42:
        strong_cluster_freqs.append(freq)
    elif -49 <= power <= -44:
        weak_cluster_freqs.append(freq)

# --- STATISTICS ---
if all_powers:
    mean_power = statistics.mean(all_powers)
    stdev_power = statistics.stdev(all_powers)
    min_power = min(all_powers)
    max_power = max(all_powers)
    mean_plus_3stdev = mean_power + 3 * stdev_power
    mean_minus_3stdev = mean_power - 3 * stdev_power

    print("\nDescriptive Statistics:")
    print(f"Mean: {mean_power:.2f} dBm")
    print(f"Standard Deviation: {stdev_power:.2f} dB")
    print(f"Mean + 3*StdDev: {mean_plus_3stdev:.2f} dBm")
    print(f"Mean - 3*StdDev: {mean_minus_3stdev:.2f} dBm")
    print(f"Min: {min_power:.2f} dBm")
    print(f"Max: {max_power:.2f} dBm")

# --- SAVE FREQUENCIES TO FILES ---
with open(STRONG_OUTPUT_FILE, "w") as f:
    f.write("Freq_MHz\n")
    for freq in strong_cluster_freqs:
        f.write(f"{freq:.6f}\n")

with open(WEAK_OUTPUT_FILE, "w") as f:
    f.write("Freq_MHz\n")
    for freq in weak_cluster_freqs:
        f.write(f"{freq:.6f}\n")

print(f"\nSaved {len(strong_cluster_freqs)} strong cluster freqs to {STRONG_OUTPUT_FILE}")
print(f"Saved {len(weak_cluster_freqs)} weak cluster freqs to {WEAK_OUTPUT_FILE}")

# --- PLOT HISTOGRAMS ---
plt.figure(figsize=(12, 6))
plt.hist(strong_cluster_freqs, bins=100, alpha=0.7, label="Strong signals (-42 dBm and above)")
plt.hist(weak_cluster_freqs, bins=100, alpha=0.7, label="Weaker signals (-49 to -44 dBm)")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Count")
plt.title("Frequencies of Detected Signal Clusters")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("frequency_clusters_histogram.png")
plt.show()

print("\nDone! Histogram saved as 'frequency_clusters_histogram.png'.")