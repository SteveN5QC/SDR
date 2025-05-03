import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Load frequencies from CSVs manually
def load_freqs(filename):
    with open(filename) as f:
        next(f)  # skip the header

        return [float(line.strip()) for line in f]

strong_freqs = load_freqs('strong_cluster_freqs.csv')
weak_freqs = load_freqs('weak_cluster_freqs.csv')

plt.figure(figsize=(12, 6))

# Plot histograms
plt.hist(strong_freqs, bins=100, color='steelblue', alpha=0.7, label='Strong signals (-42 dBm and above)')
plt.hist(weak_freqs, bins=100, color='orange', alpha=0.5, label='Weaker signals (-49 to -44 dBm)')

plt.xlabel('Frequency (MHz)')
plt.ylabel('Count')
plt.title('Frequencies of Detected Signal Clusters')

# ? Disable scientific notation & offset
plt.ticklabel_format(style='plain', axis='x')
plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))

plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('frequency_clusters_histogram_cleaned.png')
plt.show()
