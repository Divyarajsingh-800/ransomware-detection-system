"""
Test Script for Ransomware Detection System
Simulates both normal and ransomware-like behavior
"""

import os
import time
import random
import string
from pathlib import Path
import threading


class RansomwareSimulator:
    """Simulate ransomware behavior for testing"""
    
    def __init__(self, test_dir):
        self.test_dir = test_dir
        os.makedirs(test_dir, exist_ok=True)
    
    def create_test_files(self, count=20):
        """Create test files with various content"""
        print(f"Creating {count} test files...")
        
        file_types = {
            'text': ['.txt', '.doc', '.log'],
            'data': ['.csv', '.json', '.xml'],
            'image': ['.jpg', '.png', '.gif'],
            'document': ['.pdf', '.docx', '.xlsx']
        }
        
        for i in range(count):
            file_type = random.choice(list(file_types.keys()))
            extension = random.choice(file_types[file_type])
            filename = f"test_file_{i}{extension}"
            filepath = os.path.join(self.test_dir, filename)
            
            # Create file with low entropy content (normal files)
            content = self._generate_normal_content()
            
            with open(filepath, 'w') as f:
                f.write(content)
        
        print(f"✓ Created {count} test files")
    
    def _generate_normal_content(self, size=1024):
        """Generate normal text content (low entropy)"""
        words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog',
                 'hello', 'world', 'test', 'file', 'content', 'data', 'information']
        content = ' '.join(random.choices(words, k=size))
        return content
    
    def _generate_encrypted_content(self, size=1024):
        """Generate random bytes (high entropy - sim1ulates encryption)"""
        # FIXED: Use os.urandom for truly random bytes
        # This generates cryptographically random bytes with entropy ~7.9-8.0
        # Much more realistic than text characters (which only give ~6.1 entropy)
        return os.urandom(size)
    
    def simulate_normal_activity(self, duration=30):
        """Simulate normal file operations"""
        print(f"\n{'='*70}")
        print(f"Simulating NORMAL user activity for {duration} seconds...")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        files = list(Path(self.test_dir).glob('*'))
        
        while time.time() - start_time < duration:
            if files:
                # Randomly modify a file
                file = random.choice(files)
                try:
                    with open(file, 'a') as f:
                        f.write("\nNormal modification at " + str(time.time()))
                    print(f"Normal edit: {file.name}")
                except:
                    pass
            
            time.sleep(random.uniform(2, 5))  # Normal pace
        
        print("\n✓ Normal activity simulation completed\n")
    
    def simulate_ransomware_attack(self, delay=5):
        """Simulate ransomware encryption behavior"""
        print(f"\n{'='*70}")
        print(f"⚠️  Simulating RANSOMWARE ATTACK in {delay} seconds...")
        print(f"{'='*70}\n")
        
        time.sleep(delay)
        
        print("🔴 Starting ransomware simulation...\n")
        
        files = list(Path(self.test_dir).glob('*'))
        
        # Rapid file encryption simulation
        for i, file in enumerate(files):
            try:
                # FIXED: Read as binary
                with open(file, 'rb') as f:
                    original_content = f.read()
                
                # Overwrite with high-entropy content (simulating encryption)
                encrypted_content = self._generate_encrypted_content(len(original_content))
                
                # FIXED: Write as binary
                with open(file, 'wb') as f:
                    f.write(encrypted_content)
                
                # Rename file with ransomware extension
                new_name = str(file) + '.encrypted'
                os.rename(file, new_name)
                
                print(f"Encrypted and renamed: {file.name} -> {Path(new_name).name}")
                
                # Small delay to simulate rapid encryption
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing {file}: {e}")
        
        # Create ransomware note
        ransom_note = os.path.join(self.test_dir, "README_RANSOM.txt")
        with open(ransom_note, 'w') as f:
            f.write("""
YOUR FILES HAVE BEEN ENCRYPTED!

All your important files have been encrypted with military-grade encryption.
To decrypt your files, you need to pay the ransom.

This is a SIMULATION for testing ransomware detection systems.
No actual harm has been done to your files.
""")
        
        print("\n🔴 Ransomware simulation completed!")
        print(f"{'='*70}\n")
    
    def cleanup(self):
        """Clean up test files"""
        print("\nCleaning up test files...")
        for file in Path(self.test_dir).glob('*'):
            try:
                os.remove(file)
            except:
                pass
        print("✓ Cleanup completed")


def run_detection_test():
    """Run comprehensive detection test"""
    from ransomware_detector import RansomwareDetector
    
    test_dir = "./test_directory"
    simulator = RansomwareSimulator(test_dir)
    
    # Initialize detector
    print("Initializing Ransomware Detector...")
    detector = RansomwareDetector()
    print("✓ Detector initialized\n")
    
    # Create test files
    simulator.create_test_files(20)
    
    # Test 1: Normal activity
    print("\n" + "="*70)
    print("TEST 1: Normal Activity Detection")
    print("="*70)
    
    # Analyze files under normal conditions
    for file in Path(test_dir).glob('*'):
        result = detector.analyze_file(str(file))
        print(f"\nFile: {file.name}")
        print(f"  Risk Score: {result['risk_score']}")
        print(f"  Entropy: {result.get('entropy', 0):.2f}")
        print(f"  Suspicious: {result['is_suspicious']}")
    
    # Simulate normal activity
    simulator.simulate_normal_activity(15)
    
    # Check system behavior
    system_analysis = detector.analyze_system_behavior()
    print(f"\nSystem Risk Score: {system_analysis['risk_score']}")
    print(f"Attack Detected: {system_analysis['is_attack']}")
    
    # Test 2: Ransomware simulation
    print("\n" + "="*70)
    print("TEST 2: Ransomware Attack Detection")
    print("="*70)
    
    # Run ransomware simulation in separate thread
    attack_thread = threading.Thread(target=simulator.simulate_ransomware_attack, args=(3,))
    attack_thread.start()
    
    # Monitor for 20 seconds
    print("\nMonitoring for ransomware activity...")
    for i in range(20):
        time.sleep(1)
        
        if i % 2 == 0:  # Check every 2 seconds
            system_analysis = detector.analyze_system_behavior()
            
            if system_analysis['is_attack']:
                print(f"\n🚨 RANSOMWARE DETECTED! Risk Score: {system_analysis['risk_score']}")
                print("Indicators:")
                for indicator in system_analysis['indicators']:
                    print(f"  - {indicator}")
    
    attack_thread.join()
    
    # Analyze encrypted files
    print("\n" + "="*70)
    print("Analyzing encrypted files...")
    print("="*70)
    
    for file in Path(test_dir).glob('*.encrypted'):
        result = detector.analyze_file(str(file))
        print(f"\nFile: {file.name}")
        print(f"  Risk Score: {result['risk_score']}")
        print(f"  Entropy: {result.get('entropy', 0):.2f}")
        print(f"  Suspicious: {result['is_suspicious']}")
        if result['indicators']:
            print(f"  Indicators: {', '.join(result['indicators'])}")
    
    # Cleanup
    input("\n\nPress Enter to cleanup test files...")
    simulator.cleanup()
    
    print("\n✓ Detection test completed!")


def interactive_menu():
    """Interactive testing menu"""
    test_dir = "./test_directory"
    simulator = RansomwareSimulator(test_dir)
    
    from ransomware_detector import RansomwareDetector
    detector = RansomwareDetector()
    
    while True:
        print("\n" + "="*70)
        print("AI-Based Ransomware Detection System - Testing Menu")
        print("="*70)
        print("\n1. Create test files")
        print("2. Simulate normal activity")
        print("3. Simulate ransomware attack")
        print("4. Analyze all files")
        print("5. Check system behavior")
        print("6. Run full automated test")
        print("7. Cleanup test files")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            count = int(input("How many files to create? (default 20): ") or "20")
            simulator.create_test_files(count)
        
        elif choice == '2':
            duration = int(input("Duration in seconds? (default 30): ") or "30")
            simulator.simulate_normal_activity(duration)
        
        elif choice == '3':
            simulator.simulate_ransomware_attack(delay=3)
        
        elif choice == '4':
            print("\nAnalyzing all files...")
            for file in Path(test_dir).glob('*'):
                if file.is_file():
                    result = detector.analyze_file(str(file))
                    print(f"\n{file.name}:")
                    print(f"  Risk: {result['risk_score']}, Entropy: {result.get('entropy', 0):.2f}")
                    if result['indicators']:
                        print(f"  Indicators: {', '.join(result['indicators'])}")
        
        elif choice == '5':
            analysis = detector.analyze_system_behavior()
            print(f"\nSystem Risk Score: {analysis['risk_score']}")
            print(f"Attack Detected: {analysis['is_attack']}")
            if analysis['indicators']:
                print("Indicators:")
                for ind in analysis['indicators']:
                    print(f"  - {ind}")
        
        elif choice == '6':
            run_detection_test()
        
        elif choice == '7':
            simulator.cleanup()
        
        elif choice == '8':
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        run_detection_test()
    else:
        interactive_menu()