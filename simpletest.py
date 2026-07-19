"""
🔥 STRONG Ransomware Simulation Test (FINAL STABLE VERSION)
This WILL trigger high risk scores (80–100)
"""

import os
import time

def test_ransomware_detection():
    print("="*70)
    print("🔥 RANSOMWARE ATTACK SIMULATION (FINAL STABLE TEST)")
    print("="*70)
    print()

    test_dir = "./test_ransomware"

    # 🔥 SAFE CLEANUP (DO NOT DELETE FOLDER)
    if os.path.exists(test_dir):
        for file in os.listdir(test_dir):
            file_path = os.path.join(test_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception:
                pass
    else:
        os.makedirs(test_dir)

    # -----------------------------
    # STEP 1: NORMAL FILE
    # -----------------------------
    print("Step 1: Creating NORMAL file...")
    normal_file = os.path.join(test_dir, "normal.txt")

    with open(normal_file, "w") as f:
        f.write("This is a normal file.\n" * 100)

    print("✓ Normal file created")
    print()

    time.sleep(1)

    # -----------------------------
    # STEP 2: HIGH ENTROPY FILE
    # -----------------------------
    print("Step 2: Creating HIGH entropy file...")

    encrypted_file = os.path.join(test_dir, "encrypted_sample.dat")
    with open(encrypted_file, "wb") as f:
        f.write(os.urandom(10000))

    print("✓ High entropy file created")
    print()

    time.sleep(1)

    # -----------------------------
    # STEP 3: REAL RANSOMWARE BEHAVIOR
    # -----------------------------
    print("Step 3: 🚨 Simulating REAL ransomware attack...")

    for i in range(120):
        file_path = os.path.join(test_dir, f"attack_{i}.txt")

        # 1. Create file
        with open(file_path, "w") as f:
            f.write("safe content")

        # 2. Modify file (simulate encryption)
        with open(file_path, "wb") as f:
            f.write(os.urandom(5000))

        # 3. Rename file (simulate ransomware)
        encrypted_path = file_path.replace(".txt", ".encrypted")

        # 🔥 SAFE RENAME (NO CRASH)
        os.replace(file_path, encrypted_path)

        # 🔥 Small delay (important for event detection)
        time.sleep(0.01)

    print("🔥 120 files modified and renamed!")
    print()

    print("="*70)
    print("✅ ATTACK SIMULATION COMPLETE")
    print("="*70)
    print()
    print("👉 EXPECTED IN DETECTOR:")
    print("   🚨 High Entropy")
    print("   🚨 Modification Burst")
    print("   🚨 Rename Pattern")
    print("   🚨 Risk Score: 80–100")
    print()


if __name__ == "__main__":
    test_ransomware_detection()