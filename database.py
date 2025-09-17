import sqlite3
import hashlib
import bcrypt
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

class DatabaseManager:
    def __init__(self, db_path: str = "medical_assistant.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Patient records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                patient_name TEXT,
                patient_data TEXT,  -- JSON string of patient data
                file_name TEXT,
                file_type TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Diagnostic results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                patient_record_id INTEGER,
                diagnostic_data TEXT,  -- JSON string of diagnostic results
                confidence_threshold REAL,
                max_diagnoses INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (patient_record_id) REFERENCES patient_records (id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                default_confidence_threshold REAL DEFAULT 0.3,
                default_max_diagnoses INTEGER DEFAULT 8,
                enable_red_flags BOOLEAN DEFAULT TRUE,
                theme_preference TEXT DEFAULT 'dark',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str, full_name: str) -> bool:
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return False
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, full_name))
            
            user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, full_name, role
                FROM users 
                WHERE (username = ? OR email = ?) AND is_active = TRUE
            ''', (username, username))
            
            user = cursor.fetchone()
            
            if user and self.verify_password(password, user[3]):
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user[0],))
                conn.commit()
                
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[4],
                    'role': user[5]
                }
                
                conn.close()
                return user_data
            
            conn.close()
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def create_session(self, user_id: int) -> str:
        """Create a new session for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_token = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, datetime('now', '+7 days'))
            ''', (user_id, session_token))
            
            conn.commit()
            conn.close()
            
            return session_token
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return ""
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session and return user data if valid"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.full_name, u.role
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? 
                AND s.expires_at > datetime('now')
                AND s.is_active = TRUE
                AND u.is_active = TRUE
            ''', (session_token,))
            
            user = cursor.fetchone()
            
            if user:
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[3],
                    'role': user[4]
                }
                conn.close()
                return user_data
            
            conn.close()
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by deactivating session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = FALSE 
                WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def save_patient_data(self, user_id: int, patient_data: List[Dict], file_name: str, file_type: str) -> Optional[int]:
        """Save patient data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract patient name if available
            patient_name = "Unknown"
            if patient_data:
                for key, value in patient_data[0].items():
                    if 'name' in key.lower() or 'patient' in key.lower():
                        patient_name = str(value)
                        break
            
            cursor.execute('''
                INSERT INTO patient_records (user_id, patient_name, patient_data, file_name, file_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, patient_name, json.dumps(patient_data), file_name, file_type))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return record_id if record_id is not None else 0
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def save_diagnostic_results(self, user_id: int, patient_record_id: int, 
                              diagnostic_data: Dict, confidence_threshold: float, 
                              max_diagnoses: int) -> bool:
        """Save diagnostic results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO diagnostic_results 
                (user_id, patient_record_id, diagnostic_data, confidence_threshold, max_diagnoses)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, patient_record_id, json.dumps(diagnostic_data), 
                  confidence_threshold, max_diagnoses))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_user_patient_records(self, user_id: int) -> List[Dict]:
        """Get all patient records for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, patient_name, file_name, file_type, uploaded_at
                FROM patient_records
                WHERE user_id = ?
                ORDER BY uploaded_at DESC
            ''', (user_id,))
            
            records = cursor.fetchall()
            
            patient_records = []
            for record in records:
                patient_records.append({
                    'id': record[0],
                    'patient_name': record[1],
                    'file_name': record[2],
                    'file_type': record[3],
                    'uploaded_at': record[4]
                })
            
            conn.close()
            return patient_records
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_user_diagnostic_history(self, user_id: int) -> List[Dict]:
        """Get diagnostic history for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dr.id, pr.patient_name, dr.diagnostic_data, dr.created_at,
                       dr.confidence_threshold, dr.max_diagnoses
                FROM diagnostic_results dr
                JOIN patient_records pr ON dr.patient_record_id = pr.id
                WHERE dr.user_id = ?
                ORDER BY dr.created_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            
            diagnostic_history = []
            for result in results:
                try:
                    diagnostic_data = json.loads(result[2])
                except json.JSONDecodeError:
                    diagnostic_data = {}
                
                diagnostic_history.append({
                    'id': result[0],
                    'patient_name': result[1],
                    'diagnostic_data': diagnostic_data,
                    'created_at': result[3],
                    'confidence_threshold': result[4],
                    'max_diagnoses': result[5]
                })
            
            conn.close()
            return diagnostic_history
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT default_confidence_threshold, default_max_diagnoses, 
                       enable_red_flags, theme_preference
                FROM user_preferences
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                preferences = {
                    'default_confidence_threshold': result[0],
                    'default_max_diagnoses': result[1],
                    'enable_red_flags': bool(result[2]),
                    'theme_preference': result[3]
                }
            else:
                # Create default preferences
                cursor.execute('''
                    INSERT INTO user_preferences (user_id)
                    VALUES (?)
                ''', (user_id,))
                conn.commit()
                
                preferences = {
                    'default_confidence_threshold': 0.3,
                    'default_max_diagnoses': 8,
                    'enable_red_flags': True,
                    'theme_preference': 'dark'
                }
            
            conn.close()
            return preferences
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {
                'default_confidence_threshold': 0.3,
                'default_max_diagnoses': 8,
                'enable_red_flags': True,
                'theme_preference': 'dark'
            }
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_preferences 
                SET default_confidence_threshold = ?, default_max_diagnoses = ?,
                    enable_red_flags = ?, theme_preference = ?
                WHERE user_id = ?
            ''', (
                preferences.get('default_confidence_threshold', 0.3),
                preferences.get('default_max_diagnoses', 8),
                preferences.get('enable_red_flags', True),
                preferences.get('theme_preference', 'dark'),
                user_id
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
