"""
AI-Based Real-Time Ransomware Detection System
Using File Entropy & Access Pattern Intelligence
"""

import os
import time
import math
import numpy as np
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pickle
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


class EntropyCalculator:
    """Calculate Shannon entropy of files to detect encryption"""
    
    @staticmethod
    def calculate_entropy(file_path, block_size=1024):
        """
        Calculate Shannon entropy of a file
        High entropy (>7.0) suggests encrypted/compressed data
        """
        try:
            if not os.path.exists(file_path):
                return 0.0
            
            # Skip very large files (>100MB)
            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                return 0.0
            
            entropy = 0.0
            with open(file_path, 'rb') as f:
                # Read file in chunks
                byte_counts = defaultdict(int)
                total_bytes = 0
                
                while True:
                    chunk = f.read(block_size)
                    if not chunk:
                        break
                    
                    for byte in chunk:
                        byte_counts[byte] += 1
                        total_bytes += 1
                
                # Calculate Shannon entropy
                for count in byte_counts.values():
                    if count > 0:
                        probability = count / total_bytes
                        entropy -= probability * math.log2(probability)
            
            return entropy
        
        except (IOError, PermissionError, OSError):
            return 0.0


class FileAccessMonitor:
    """Monitor file access patterns for suspicious behavior"""
    
    def __init__(self, time_window=60):
        self.time_window = time_window  # seconds
        self.access_log = defaultdict(lambda: deque(maxlen=1000))
        self.modification_log = defaultdict(lambda: deque(maxlen=1000))
        self.rename_log = defaultdict(lambda: deque(maxlen=100))
        self.deletion_log = defaultdict(lambda: deque(maxlen=100))
        self.lock = threading.Lock()
    
    def log_access(self, file_path, event_type):
        """Log file access event"""
        with self.lock:
            timestamp = time.time()
            
            if event_type == 'modified':
                self.modification_log[file_path].append(timestamp)
            elif event_type == 'renamed':
                self.rename_log[file_path].append(timestamp)
            elif event_type == 'deleted':
                self.deletion_log[file_path].append(timestamp)
            else:
                self.access_log[file_path].append(timestamp)
    
    def get_access_rate(self, file_path=None):
        """Calculate file access rate (accesses per minute)"""
        with self.lock:
            current_time = time.time()
            
            if file_path:
                recent_accesses = [t for t in self.access_log[file_path] 
                                   if current_time - t <= self.time_window]
                return len(recent_accesses) * (60 / self.time_window)
            else:
                # Global access rate
                total_accesses = 0
                for timestamps in self.access_log.values():
                    recent = [t for t in timestamps if current_time - t <= self.time_window]
                    total_accesses += len(recent)
                return total_accesses * (60 / self.time_window)
    
    def get_modification_burst(self):
        """Detect burst of file modifications (ransomware behavior)"""
        with self.lock:
            current_time = time.time()
            recent_mods = 0
            
            for timestamps in self.modification_log.values():
                recent = [t for t in timestamps if current_time - t <= 10]  # Last 10 seconds
                recent_mods += len(recent)
            
            return recent_mods
    
    def get_rename_pattern(self):
        """Detect mass file renaming (common ransomware behavior)"""
        with self.lock:
            current_time = time.time()
            recent_renames = 0
            
            for timestamps in self.rename_log.values():
                recent = [t for t in timestamps if current_time - t <= 30]  # Last 30 seconds
                recent_renames += len(recent)
            
            return recent_renames
    
    def get_deletion_pattern(self):
        """Detect mass file deletion"""
        with self.lock:
            current_time = time.time()
            recent_deletions = 0
            
            for timestamps in self.deletion_log.values():
                recent = [t for t in timestamps if current_time - t <= 30]
                recent_deletions += len(recent)
            
            return recent_deletions


class FeatureExtractor:
    """Extract features for ML model"""
    
    def __init__(self, entropy_calc, access_monitor):
        self.entropy_calc = entropy_calc
        self.access_monitor = access_monitor
        self.file_extensions = defaultdict(int)
    
    def extract_features(self, file_path=None):
        """Extract feature vector for classification"""
        features = []
        
        # File-specific features
        if file_path and os.path.exists(file_path):
            entropy = self.entropy_calc.calculate_entropy(file_path)
            file_size = os.path.getsize(file_path)
            extension = Path(file_path).suffix.lower()
            
            # Check for suspicious extensions
            suspicious_exts = ['.encrypted', '.locked', '.crypto', '.crypt', 
                              '.locky', '.cerber', '.zepto', '.osiris']
            has_suspicious_ext = 1 if extension in suspicious_exts else 0
            
            features.extend([
                entropy,  # File entropy
                file_size / (1024 * 1024),  # File size in MB
                has_suspicious_ext,  # Suspicious extension flag
                self.access_monitor.get_access_rate(file_path),  # Access rate
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # System-wide behavioral features
        features.extend([
            self.access_monitor.get_modification_burst(),  # Modification burst
            self.access_monitor.get_rename_pattern(),  # Rename pattern
            self.access_monitor.get_deletion_pattern(),  # Deletion pattern
            self.access_monitor.get_access_rate(),  # Global access rate
        ])
        
        return np.array(features).reshape(1, -1)


class RansomwareDetector:
    """Main ransomware detection engine using ML"""
    
    def __init__(self, model_path='ransomware_model.pkl'):
        self.entropy_calc = EntropyCalculator()
        self.access_monitor = FileAccessMonitor()
        self.feature_extractor = FeatureExtractor(self.entropy_calc, self.access_monitor)
        
        # ML models
        self.rf_classifier = None
        self.isolation_forest = None
        self.scaler = StandardScaler()
        
        # Detection thresholds
        self.entropy_threshold = 7.0
        self.modification_threshold = 50  # files modified in 10 seconds
        self.rename_threshold = 20  # files renamed in 30 seconds
        
        # Alert system
        self.alerts = []
        self.alert_callback = None
        
        # Load or train model
        self.model_path = model_path
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load ML models"""
        if os.path.exists(self.model_path):
            self._load_model()
        else:
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train initial model with synthetic data"""
        print("Training initial ransomware detection model...")
        
        # Generate synthetic training data
        # Normal behavior: low entropy, moderate access patterns
        normal_samples = []
        for _ in range(500):
            features = [
                np.random.uniform(3.0, 6.5),  # Normal file entropy
                np.random.uniform(0.01, 10),  # File size
                0,  # No suspicious extension
                np.random.uniform(0, 5),  # Low access rate
                np.random.uniform(0, 10),  # Low modification burst
                np.random.uniform(0, 5),  # Low rename pattern
                np.random.uniform(0, 3),  # Low deletion pattern
                np.random.uniform(0, 20),  # Moderate global access
            ]
            normal_samples.append(features)
        
        # FIX: Ransomware samples now include BOTH
        # single encrypted files (high entropy only)
        # AND active attacks (high entropy + high burst)
        ransomware_samples = []
        for _ in range(500):
            if np.random.random() < 0.5:
                # Single encrypted file - high entropy, low burst
                features = [
                    np.random.uniform(7.0, 8.0),  # High entropy
                    np.random.uniform(0.01, 10),
                    np.random.choice([0, 1], p=[0.3, 0.7]),
                    np.random.uniform(0, 10),   # LOW access rate
                    np.random.uniform(0, 15),   # LOW mod burst
                    np.random.uniform(0, 8),    # LOW rename
                    np.random.uniform(0, 5),
                    np.random.uniform(0, 30),   # LOW global
                ]
            else:
                # Active ransomware attack - high entropy + high burst
                features = [
                    np.random.uniform(7.0, 8.0),  # High entropy
                    np.random.uniform(0.01, 10),
                    np.random.choice([0, 1], p=[0.3, 0.7]),
                    np.random.uniform(10, 100),  # HIGH access rate
                    np.random.uniform(30, 200),  # HIGH mod burst
                    np.random.uniform(10, 100),  # HIGH rename
                    np.random.uniform(5, 50),
                    np.random.uniform(50, 500),  # HIGH global
                ]
            ransomware_samples.append(features)
        
        # Combine and create labels
        X = np.array(normal_samples + ransomware_samples)
        y = np.array([0] * len(normal_samples) + [1] * len(ransomware_samples))
        
        # Train models
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.rf_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.rf_classifier.fit(X_scaled, y)
        
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.isolation_forest.fit(X_scaled)
        
        self._save_model()
        print("Model training completed!")
    
    def _save_model(self):
        """Save trained model"""
        model_data = {
            'rf_classifier': self.rf_classifier,
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def _load_model(self):
        """Load trained model"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.rf_classifier = model_data['rf_classifier']
            self.isolation_forest = model_data['isolation_forest']
            self.scaler = model_data['scaler']
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self._train_initial_model()
    
    def analyze_file(self, file_path):
        """Analyze a single file for ransomware indicators"""
        try:
            # Extract features
            features = self.feature_extractor.extract_features(file_path)
            features_scaled = self.scaler.transform(features)
            
            # Get predictions
            rf_prediction = self.rf_classifier.predict(features_scaled)[0]
            rf_proba = self.rf_classifier.predict_proba(features_scaled)[0][1]
            iso_prediction = self.isolation_forest.predict(features_scaled)[0]
            
            # Calculate risk score
            risk_score = 0
            indicators = []
            
            # Entropy check
            entropy = features[0][0]
            if entropy > self.entropy_threshold:
                risk_score += 30
                indicators.append(f"High entropy: {entropy:.2f}")
                
            # ML predictions
            if rf_prediction == 1:
                risk_score += 40
                indicators.append(f"ML detection: {rf_proba*100:.1f}% confidence")
            
            if iso_prediction == -1:
                risk_score += 20
                indicators.append("Anomalous behavior detected")
            
            # Behavioral checks
            mod_burst = features[0][4]
            if mod_burst > self.modification_threshold:
                risk_score += 30
                indicators.append(f"Mass modification: {int(mod_burst)} files")
            
            rename_pattern = features[0][5]
            if rename_pattern > self.rename_threshold:
                risk_score += 25
                indicators.append(f"Mass renaming: {int(rename_pattern)} files")
            
            # Cap at 100
            risk_score = min(risk_score, 100)
            
            return {
                'file_path': file_path,
                'risk_score': risk_score,
                'entropy': entropy,
                'is_suspicious': risk_score > 25,
                'indicators': indicators,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'file_path': file_path,
                'risk_score': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_system_behavior(self):
        """Analyze overall system behavior"""
        features = self.feature_extractor.extract_features()
        features_scaled = self.scaler.transform(features)
        
        rf_proba = self.rf_classifier.predict_proba(features_scaled)[0][1]
        
        risk_score = 0
        indicators = []
        
        # Check behavioral patterns
        mod_burst = features[0][4]
        if mod_burst > self.modification_threshold:
            risk_score += 40
            indicators.append(f"Rapid file modifications: {int(mod_burst)}/10s")
        
        rename_pattern = features[0][5]
        if rename_pattern > self.rename_threshold:
            risk_score += 35
            indicators.append(f"Mass file renaming: {int(rename_pattern)}/30s")
        
        deletion_pattern = features[0][6]
        if deletion_pattern > 15:
            risk_score += 25
            indicators.append(f"Mass deletions: {int(deletion_pattern)}/30s")
        
        if rf_proba > 0.7:
            risk_score += 30
            indicators.append(f"AI confidence: {rf_proba*100:.1f}%")
        
        risk_score = min(risk_score, 100)
        
        return {
            'risk_score': risk_score,
            'is_attack': risk_score > 70,
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_alert_callback(self, callback):
        """Set callback function for alerts"""
        self.alert_callback = callback
    
    def trigger_alert(self, alert_data):
        """Trigger ransomware alert"""
        self.alerts.append(alert_data)
        
        if self.alert_callback:
            self.alert_callback(alert_data)
        
        # Determine threat level
        risk = alert_data['risk_score']
        if risk >= 90:
            level = "CRITICAL"
            icon  = "🔴"
        elif risk >= 70:
            level = "HIGH"
            icon  = "🟠"
        elif risk >= 40:
            level = "MEDIUM"
            icon  = "🟡"
        else:
            level = "LOW"
            icon  = "🟢"

        print(f"\n{'='*70}")
        print(f"  {icon}  RANSOMWARE ALERT — Threat Level: {level}")
        print(f"{'='*70}")
        print(f"  {'FIELD':<25} {'VALUE'}")
        print(f"  {'-'*50}")
        print(f"  {'Risk Score':<25} {risk}/100")
        print(f"  {'Threat Level':<25} {level}")
        print(f"  {'Time':<25} {alert_data.get('timestamp', 'N/A')[:19]}")
        if 'file_path' in alert_data:
            fname = alert_data['file_path'].split('\\')[-1].split('/')[-1]
            print(f"  {'File':<25} {fname}")
        if 'entropy' in alert_data and alert_data['entropy'] > 0:
            print(f"  {'Entropy':<25} {alert_data['entropy']:.2f} / 8.0")
        print(f"  {'-'*50}")
        print(f"  INDICATORS DETECTED")
        print(f"  {'-'*50}")
        for i, indicator in enumerate(alert_data['indicators'], 1):
            print(f"  {i}. {indicator}")
        print(f"{'='*70}\n")


class FileSystemMonitor(FileSystemEventHandler):
    """Monitor file system events in real-time"""
    
    def __init__(self, detector, watch_path):
        self.detector = detector
        self.watch_path = watch_path
        self.last_check = time.time()
        self.check_interval = 5  # seconds
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"[INFO] File Modified: {event.src_path}")
            self.detector.access_monitor.log_access(event.src_path, 'modified')

            result = self.detector.analyze_file(event.src_path)

            risk = result['risk_score']
            entropy = result.get('entropy', 0)

            if risk >= 90:
                status = "🔴 ATTACK"
            elif risk >= 26:
                status = "🟡 SUSPICIOUS"
            else:
                status = "🟢 NORMAL"

            print(f"  ┌─────────────────────────────────────────────┐")
            print(f"  │  Entropy: {entropy:<6.2f}  Risk: {risk:<4}  {status}")
            print(f"  └─────────────────────────────────────────────┘")

            if result['is_suspicious']:
                self.detector.trigger_alert(result)

            self._periodic_check()
    
    def on_created(self, event):
        if not event.is_directory:
            print(f"[INFO] File Created: {event.src_path}")
            self.detector.access_monitor.log_access(event.src_path, 'modified')

            result = self.detector.analyze_file(event.src_path)

            risk = result['risk_score']
            entropy = result.get('entropy', 0)

            if risk >= 90:
                status = "🔴 ATTACK"
            elif risk >= 26:
                status = "🟡 SUSPICIOUS"
            else:
                status = "🟢 NORMAL"

            print(f"  ┌─────────────────────────────────────────────┐")
            print(f"  │  Entropy: {entropy:<6.2f}  Risk: {risk:<4}  {status}")
            print(f"  └─────────────────────────────────────────────┘")

            if result['is_suspicious']:
                self.detector.trigger_alert(result)

            self._periodic_check()
    
    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[INFO] File Deleted: {event.src_path}")
            self.detector.access_monitor.log_access(event.src_path, 'deleted')
            self._periodic_check()
    
    def on_moved(self, event):
        if not event.is_directory:
            print(f"[INFO] File Renamed: {event.src_path}")
            self.detector.access_monitor.log_access(event.src_path, 'renamed')

            if os.path.exists(event.dest_path):
                result = self.detector.analyze_file(event.dest_path)
                if result['is_suspicious']:
                    self.detector.trigger_alert(result)
                    
            self._periodic_check()
    
    def _periodic_check(self):
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self.last_check = current_time

            analysis = self.detector.analyze_system_behavior()

            if analysis['is_attack']:
                self.detector.trigger_alert(analysis)


def start_monitoring(watch_path, model_path='ransomware_model.pkl'):
    """Start real-time ransomware monitoring"""
    print(f"Starting AI-Based Ransomware Detection System")
    print(f"Monitoring path: {watch_path}")
    print(f"{'='*70}\n")
    
    # Initialize detector
    detector = RansomwareDetector(model_path)
    
    # Setup file system monitoring
    event_handler = FileSystemMonitor(detector, watch_path)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    
    print("✓ Real-time monitoring active")
    print("✓ ML models loaded")
    print("✓ Entropy analysis enabled")
    print("✓ Behavioral analysis enabled\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping ransomware detection system...")
    
    observer.join()
    return detector


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        watch_directory = sys.argv[1]
    else:
        watch_directory = "./monitored_directory"  # Default test directory
    
    os.makedirs(watch_directory, exist_ok=True)
    
    detector = start_monitoring(watch_directory)