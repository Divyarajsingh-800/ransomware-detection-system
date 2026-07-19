"""
DIAGNOSTIC SCRIPT - Find out WHY detection isn't working
Run this to see what's happening
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ransomware_detector import EntropyCalculator, RansomwareDetector

def diagnose():
    print("="*70)
    print("RANSOMWARE DETECTION DIAGNOSTIC TOOL")
    print("="*70)
    print()
    
    # Create test directory
    test_dir = "./diagnostic_test"
    os.makedirs(test_dir, exist_ok=True)
    
    print("Creating test files...")
    print()
    
    # Test 1: Normal text file
    print("TEST 1: Normal Text File")
    print("-" * 70)
    normal_file = os.path.join(test_dir, "normal.txt")
    with open(normal_file, 'w') as f:
        f.write("The quick brown fox jumps over the lazy dog. " * 200)
    
    entropy_calc = EntropyCalculator()
    entropy = entropy_calc.calculate_entropy(normal_file)
    
    print(f"File: {normal_file}")
    print(f"Entropy: {entropy:.2f}")
    print(f"Expected: 4.0-5.5 (LOW)")
    print(f"Status: {'✅ CORRECT' if entropy < 7.0 else '❌ WRONG'}")
    print()
    
    # Test 2: Random binary file (encrypted)
    print("TEST 2: Encrypted File (Random Bytes)")
    print("-" * 70)
    encrypted_file = os.path.join(test_dir, "encrypted.dat")
    with open(encrypted_file, 'wb') as f:
        random_data = os.urandom(10000)
        f.write(random_data)
    
    entropy = entropy_calc.calculate_entropy(encrypted_file)
    
    print(f"File: {encrypted_file}")
    print(f"Entropy: {entropy:.2f}")
    print(f"Expected: 7.0-8.0 (HIGH)")
    print(f"Status: {'✅ CORRECT' if entropy > 7.0 else '❌ PROBLEM FOUND!'}")
    
    if entropy <= 7.0:
        print()
        print("⚠️  ERROR: Encrypted file has LOW entropy!")
        print("   This means binary encryption simulation is not working")
        print("   The file should have entropy > 7.0")
    print()
    
    # Test 3: Full detection system
    print("TEST 3: Full Detection System")
    print("-" * 70)
    
    detector = RansomwareDetector()
    
    # Analyze normal file
    result_normal = detector.analyze_file(normal_file)
    print(f"Normal file analysis:")
    print(f"  Entropy: {result_normal['entropy']:.2f}")
    print(f"  Risk Score: {result_normal['risk_score']}")
    print(f"  Suspicious: {result_normal['is_suspicious']}")
    print(f"  Status: {'✅' if not result_normal['is_suspicious'] else '❌ False Positive!'}")
    print()
    
    # Analyze encrypted file
    result_encrypted = detector.analyze_file(encrypted_file)
    print(f"Encrypted file analysis:")
    print(f"  Entropy: {result_encrypted['entropy']:.2f}")
    print(f"  Risk Score: {result_encrypted['risk_score']}")
    print(f"  Suspicious: {result_encrypted['is_suspicious']}")
    print(f"  Indicators: {result_encrypted['indicators']}")
    
    if result_encrypted['risk_score'] < 60:
        print(f"  Status: ❌ DETECTION FAILED!")
        print()
        print("  PROBLEM: Encrypted file should have risk score 70-100")
        print("  Actual: Risk score only", result_encrypted['risk_score'])
        print()
        print("  Possible causes:")
        print("  1. ML model not detecting properly (needs retraining)")
        print("  2. Entropy not being calculated correctly")
        print("  3. Feature extraction issue")
        print()
        print("  To fix: Run fix_and_retrain.py")
    else:
        print(f"  Status: ✅ DETECTION WORKING!")
    
    print()
    print("="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print()
    
    # Summary
    print("SUMMARY:")
    print(f"  Normal file entropy: {result_normal['entropy']:.2f} (should be < 7.0)")
    print(f"  Encrypted file entropy: {result_encrypted['entropy']:.2f} (should be > 7.0)")
    print(f"  Normal file risk: {result_normal['risk_score']} (should be < 30)")
    print(f"  Encrypted file risk: {result_encrypted['risk_score']} (should be > 60)")
    print()
    
    if result_encrypted['risk_score'] < 60:
        print("❌ DETECTION NOT WORKING PROPERLY")
        print()
        print("FIX:")
        print("1. Delete ransomware_model.pkl")
        print("2. Run: python fix_and_retrain.py")
        print("3. Run this diagnostic again")
    else:
        print("✅ DETECTION SYSTEM WORKING CORRECTLY!")
        print()
        print("You can now test with:")
        print("  python test_ransomware_detection.py")

if __name__ == "__main__":
    diagnose()