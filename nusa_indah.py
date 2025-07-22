import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label

def detect_tires_enhanced(signal, title="Signal", threshold=5):
    signal = np.array(signal)
    binary = signal > threshold
    labeled, num_features = label(binary)

    tire_data = []

    t = signal

    for i in range(1, num_features + 1):
        idx = np.where(labeled == i)[0]
        if len(idx) > 0:
            width = np.max(signal[idx])  # peak width in cm
            duration = len(idx) * (t[1] - t[0])  # duration in seconds
            start_time = t[idx[0]]
            end_time = t[idx[-1]]
            center_time = np.mean(t[idx])

            tire_data.append({
                'width': width,
                'duration': duration,
                'start_time': start_time,
                'end_time': end_time,
                'center_time': center_time,
                'indices': idx
            })

    # Sort by center time to get front and rear
    tire_data.sort(key=lambda x: x['center_time'])

    return tire_data, num_features

# --- Classification Algorithm ---
def classify_vehicle_type(tire_data, title="Signal"):
    """
    Classify vehicle type based on tire characteristics

    Classification Rules:
    - Type 1: Both tires have similar widths (difference < 10 cm)
    - Type 2: Significant difference in tire widths (rear > front by ≥ 10 cm)

    Additional factors:
    - Duration patterns (fast vs slow/ngantri)
    - Width consistency
    """

    if len(tire_data) < 2:
        return "Unknown", "Insufficient tire data"

    if len(tire_data) > 2:
        return f"Type {len(tire_data)}"
     
    # Extract features
    front_tire = tire_data[0]  # First tire chronologically
    rear_tire = tire_data[1]   # Second tire chronologically

    front_width = front_tire['width']
    rear_width = rear_tire['width']
    front_duration = front_tire['duration']
    rear_duration = rear_tire['duration']

    width_difference = rear_width - front_width
    avg_duration = (front_duration + rear_duration) / 2

    # Classification logic
    vehicle_type = None
    speed_category = None
    confidence = 0

    # Type classification based on width difference
    if abs(width_difference) < 10:  # Similar widths
        vehicle_type = "Type 1"
        confidence += 0.7
    elif width_difference >= 10:   # Rear significantly wider
        vehicle_type = "Type 2"
        confidence += 0.8
    else:
        vehicle_type = "Type 1"  # Default fallback
        confidence += 0.3

    # Speed/behavior classification based on duration
    if avg_duration > 1.0:  # Long duration = slow/queuing
        speed_category = "Ngantri (Slow/Queuing)"
        confidence += 0.2
    else:  # Short duration = fast
        speed_category = "Fast"
        confidence += 0.2

    # Additional validation
    width_ratio = rear_width / front_width if front_width > 0 else 1
    if width_ratio > 1.5:  # Strong indicator of Type 2
        if vehicle_type == "Type 2":
            confidence += 0.1
        else:
            confidence -= 0.2

    confidence = min(confidence, 1.0)  # Cap at 100%

    classification_details = {
        'vehicle_type': vehicle_type,
        'speed_category': speed_category,
        'confidence': confidence,
        'front_width': front_width,
        'rear_width': rear_width,
        'width_difference': width_difference,
        'width_ratio': width_ratio,
        'avg_duration': avg_duration,
        'front_duration': front_duration,
        'rear_duration': rear_duration
    }

    # return vehicle_type, speed_category, classification_details
    return vehicle_type

# --- Enhanced Visualization Function ---
def analyze_and_classify(signal, title="Signal", threshold=5):
    # Detect tires
    tire_data, num_features = detect_tires_enhanced(signal, title, threshold)

    # Classify
    if len(tire_data) >= 2:
        vehicle_type, speed_category, details = classify_vehicle_type(tire_data, title)

        print(f"\n🚗 {title}")
        print(f"Detected {num_features} tires.")
        print(f"Classification: {vehicle_type} - {speed_category}")
        print(f"Confidence: {details['confidence']:.2f}")
        print(f"Front tire width: {details['front_width']:.2f} cm")
        print(f"Rear tire width: {details['rear_width']:.2f} cm")
        print(f"Width difference: {details['width_difference']:.2f} cm")
        print(f"Width ratio: {details['width_ratio']:.2f}")
        print(f"Average duration: {details['avg_duration']:.2f} s")

        # Plot
        plt.figure(figsize=(14, 6))

        # Main signal plot
        plt.subplot(1, 2, 1)
        plt.plot(t, signal, 'b-', label='Signal', alpha=0.7)
        plt.axhline(y=threshold, color='r', linestyle='--', alpha=0.5, label=f'Threshold ({threshold})')

        # Mark detected tires
        colors = ['red', 'green', 'orange', 'purple']
        for i, tire in enumerate(tire_data):
            color = colors[i % len(colors)]
            plt.plot(t[tire['indices']], signal[tire['indices']],
                    color=color, linewidth=3, alpha=0.8,
                    label=f'Tire {i+1} ({tire["width"]:.1f} cm)')

            # Mark peak
            center_idx = int(np.mean(tire['indices']))
            plt.plot(t[center_idx], tire['width'], 'o', color=color, markersize=8)
            plt.text(t[center_idx], tire['width'] + 1,
                    f'{tire["width"]:.1f} cm\n{tire["duration"]:.2f}s',
                    ha='center', va='bottom', color=color, fontweight='bold')

        plt.title(f"Tire Detection - {title}")
        plt.xlabel("Time (s)")
        plt.ylabel("Signal (Tire Width in cm)")
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend()

        # Classification summary plot
        plt.subplot(1, 2, 2)
        categories = ['Front Width', 'Rear Width', 'Duration']
        values = [details['front_width'], details['rear_width'],
                 details['avg_duration']*10]  # Scale for visibility
        colors_bar = ['lightblue', 'lightcoral', 'lightgreen']

        bars = plt.bar(categories, values, color=colors_bar, alpha=0.7)
        plt.title(f"Classification: {vehicle_type}\n{speed_category}")
        plt.ylabel("Values (scaled)")

        # Add value labels on bars
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.1f}', ha='center', va='bottom')

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        return details
    else:
        print(f"\n❌ {title}: Insufficient tire data for classification")
        return None