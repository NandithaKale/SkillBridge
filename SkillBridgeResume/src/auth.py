import sqlite3
import hashlib
import os
from datetime import datetime

class AuthManager:
    def __init__(self, db_path='data/users.db'):
        """Initialize authentication manager with SQLite database"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create users and user_courses tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User courses table - MODIFIED to prevent duplicates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course_name TEXT NOT NULL,
                progress REAL,
                grade REAL,
                hours REAL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, course_name)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password):
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password, full_name=""):
        """Register a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, full_name))
            conn.commit()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            return False, "Username or email already exists"
        finally:
            conn.close()
    
    def login_user(self, username, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self._hash_password(password)
        cursor.execute('''
            SELECT user_id, username, email, full_name 
            FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'full_name': user[3]
            }
        return False, None
    
    def add_or_update_course(self, user_id, course_name, progress, grade, hours):
        """Add a new course or update existing one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if course exists
            cursor.execute('''
                SELECT id FROM user_courses 
                WHERE user_id = ? AND course_name = ?
            ''', (user_id, course_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing course
                cursor.execute('''
                    UPDATE user_courses 
                    SET progress = ?, grade = ?, hours = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND course_name = ?
                ''', (progress, grade, hours, user_id, course_name))
            else:
                # Insert new course
                cursor.execute('''
                    INSERT INTO user_courses (user_id, course_name, progress, grade, hours)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, course_name, progress, grade, hours))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving course: {e}")
            return False
        finally:
            conn.close()
    
    def save_courses(self, user_id, courses_data):
        """Save multiple courses (adds new, updates existing, keeps old)"""
        for course in courses_data:
            self.add_or_update_course(
                user_id,
                course['course'],
                course['progress'],
                course['grade'],
                course['hours']
            )
    
    def delete_course(self, user_id, course_name):
        """Delete a specific course"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM user_courses 
            WHERE user_id = ? AND course_name = ?
        ''', (user_id, course_name))
        
        conn.commit()
        conn.close()
    
    def delete_all_courses(self, user_id):
        """Delete all courses for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_courses WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_courses(self, user_id):
        """Get all courses for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT course_name, progress, grade, hours, added_at
            FROM user_courses
            WHERE user_id = ?
            ORDER BY added_at DESC
        ''', (user_id,))
        
        courses = cursor.fetchall()
        conn.close()
        
        return [
            {
                'course': row[0],
                'progress': row[1],
                'grade': row[2],
                'hours': row[3],
                'added_at': row[4]
            }
            for row in courses
        ]
    
    def has_saved_courses(self, user_id):
        """Check if user has any saved courses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM user_courses WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0