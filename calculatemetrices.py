"""
🔥 FIXED Performance Metrics Calculator
Now includes REAL behavior tracking + proper ransomware simulation
"""

import os
import time
from pathlib import Path
from ransomware_detector import RansomwareDetector


def run_performance_test():

    print("\n" + "="*70)
    print("RANSOMWARE DETECTION - PERFORMANCE METRICS TEST (FIXED)")
    print("="*70 + "\n")

    test_dir = "./metrics_test_directory"
    os.makedirs(test_dir, exist_ok=True)

    detector = RansomwareDetector()

    results = {
        'normal_files': [],
        'ransomware_files': [],
        'processing_times': [],
        'entropy_values': []
    }

    # ============================================================
    # PHASE 1: NORMAL FILES
    # ============================================================
    print("PHASE 1: Testing Normal Files")
    print("-" * 70)

    normal_files = []

    for i in range(20):
        file_path = os.path.join(test_dir, f"normal_{i}.txt")
        with open(file_path, "w") as f:
            f.write("This is a normal file.\n" * 100)

        normal_files.append(file_path)

    for file in normal_files:
        start_time = time.time()

        # ✅ LOG NORMAL BEHAVIOR
        detector.access_monitor.log_access(file, 'modified')

        result = detector.analyze_file(file)
        processing_time = time.time() - start_time

        results['normal_files'].append(result)
        results['processing_times'].append(processing_time)
        results['entropy_values'].append(result.get('entropy', 0))

        print(f"  {os.path.basename(file)}: Risk={result['risk_score']}, "
              f"Entropy={result.get('entropy', 0):.2f}")

    print("\n✓ Normal files tested\n")

    # ============================================================
    # PHASE 2: RANSOMWARE SIMULATION (FIXED)
    # ============================================================
    print("PHASE 2: 🚨 Simulating REAL Ransomware Attack")
    print("-" * 70)

    encrypted_files = []

    # 🔥 MASS ENCRYPTION (KEY FIX)
    for i in range(100):   # BIG NUMBER → triggers burst
        file_path = os.path.join(test_dir, f"attack_{i}.encrypted")

        with open(file_path, "wb") as f:
            f.write(os.urandom(5000))  # HIGH entropy

        # ✅ LOG BEHAVIOR (CRITICAL FIX)
        detector.access_monitor.log_access(file_path, 'modified')

        encrypted_files.append(file_path)

    print("🔥 100 encrypted files created instantly!\n")

    # ============================================================
    # PHASE 3: ANALYZE ENCRYPTED FILES
    # ============================================================
    print("PHASE 3: Testing Encrypted Files")
    print("-" * 70)

    for file in encrypted_files:
        start_time = time.time()

        result = detector.analyze_file(file)
        processing_time = time.time() - start_time

        results['ransomware_files'].append(result)
        results['processing_times'].append(processing_time)
        results['entropy_values'].append(result.get('entropy', 0))

        print(f"  {os.path.basename(file)}: Risk={result['risk_score']}, "
              f"Entropy={result.get('entropy', 0):.2f}")

    print("\n✓ Encrypted files tested\n")

    # ============================================================
    # PHASE 4: SYSTEM BEHAVIOR ANALYSIS
    # ============================================================
    print("PHASE 4: System Behavior Detection")
    print("-" * 70)

    system_analysis = detector.analyze_system_behavior()

    print(f"  System Risk Score: {system_analysis['risk_score']}")
    print(f"  Attack Detected: {system_analysis['is_attack']}")
    print()

    # ============================================================
    # METRICS CALCULATION
    # ============================================================
    print("="*70)
    print("FINAL METRICS")
    print("="*70)

    normal = results['normal_files']
    ransomware = results['ransomware_files']

    tp = sum(1 for r in ransomware if r['risk_score'] > 60)
    fn = sum(1 for r in ransomware if r['risk_score'] <= 60)
    tn = sum(1 for r in normal if r['risk_score'] <= 60)
    fp = sum(1 for r in normal if r['risk_score'] > 60)

    accuracy = (tp + tn) / (tp + tn + fp + fn) * 100
    detection_rate = tp / len(ransomware) * 100
    fpr = fp / len(normal) * 100

    avg_latency = sum(results['processing_times']) / len(results['processing_times'])
    throughput = 1 / avg_latency

    normal_entropy = sum(r['entropy'] for r in normal) / len(normal)
    ransomware_entropy = sum(r['entropy'] for r in ransomware) / len(ransomware)

    normal_risk = sum(r['risk_score'] for r in normal) / len(normal)
    ransomware_risk = sum(r['risk_score'] for r in ransomware) / len(ransomware)

    print(f"\n📊 Accuracy: {accuracy:.1f}%")
    print(f"🎯 Detection Rate: {detection_rate:.1f}%")
    print(f"⚠️ False Positive Rate: {fpr:.1f}%")

    print(f"\n⚡ Avg Latency: {avg_latency*1000:.2f} ms")
    print(f"🚀 Throughput: {throughput:.0f} files/sec")

    print(f"\n🔬 Entropy: Normal={normal_entropy:.2f}, Ransomware={ransomware_entropy:.2f}")
    print(f"📈 Risk: Normal={normal_risk:.1f}, Ransomware={ransomware_risk:.1f}")

    print("\n🔥 EXPECTED RESULT NOW:")
    print("✔ Accuracy: 90–100%")
    print("✔ Detection Rate: 90–100%")
    print("✔ Risk Score: 80–100 for ransomware\n")


if __name__ == "__main__":
    run_performance_test()