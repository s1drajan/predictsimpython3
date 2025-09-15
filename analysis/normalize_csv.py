import pandas as pd
import re
import sys

def parse_input(text: str):
    """
    Parse the input text into a nested dictionary.
    Example:
    {
        "baseline": {"QueueCT": 0.305, "AVEbsld": 1.002, ...},
        "clairvoyant": {...},
        "100th": {...}
    }
    """
    data = {}
    current_block = None

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Check for block name (no colon inside, just ends with :)
        if re.match(r"^[A-Za-z0-9_]+$", line.replace(":", "")) and line.endswith(":"):
            current_block = line[:-1]
            data[current_block] = {}
        else:
            # Metric line: key: value
            if current_block is None:
                raise ValueError("Metric found outside of a block")
            key, value = line.split(":")
            data[current_block][key.strip()] = float(value.strip())
    return data


def normalize_to_baseline(data: dict):
    """
    Normalize all values to baseline, except for R2.
    """
    df = pd.DataFrame(data)
    baseline = df["baseline"]

    normalized = df.div(baseline, axis=0)
    normalized.loc["R2"] = df.loc["R2"]  # keep R2 raw
    return normalized


def main(input_file: str, output_file: str):
    # Read input text
    with open(input_file, "r") as f:
        text = f.read()

    # Parse and normalize
    data = parse_input(text)
    normalized = normalize_to_baseline(data)

    # Save to CSV
    normalized.to_csv(output_file)
    print(f"✅ Normalized CSV saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python normalize_metrics.py input.txt output.csv")
    else:
        main(sys.argv[1], sys.argv[2])
