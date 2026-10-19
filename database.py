import sqlite3
import os

DATABASE_PATH = os.environ.get("DATABASE_PATH", "resume.db")

def get_db_connection():
    """Establish a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize database schema safely.
    Preserves existing tables and adds recruitment-tech schema:
    - users: Recruiter authentication and role management
    - jobs: Job postings with required and preferred criteria
    - candidates: Candidate profiles, parsed info, match scores, status, notes
    - resumes: Preserved legacy table for backward compatibility
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Preserved legacy table for backward compatibility
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        score REAL,
        recommendation TEXT
    )
    """)

    # 2. Users table for recruiter authentication
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        role TEXT DEFAULT 'recruiter',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        department TEXT DEFAULT 'Engineering',
        description TEXT NOT NULL,
        required_skills TEXT DEFAULT '',
        preferred_skills TEXT DEFAULT '',
        min_experience TEXT DEFAULT '0-2 years',
        qualification TEXT DEFAULT 'Bachelor''s Degree',
        status TEXT DEFAULT 'Active',
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    """)

    # 4. Candidates / Screening Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        name TEXT NOT NULL,
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        github TEXT DEFAULT '',
        linkedin TEXT DEFAULT '',
        filename TEXT NOT NULL,
        raw_text TEXT DEFAULT '',
        score REAL DEFAULT 0.0,
        text_similarity REAL DEFAULT 0.0,
        skill_score REAL DEFAULT 0.0,
        matched_skills TEXT DEFAULT '',
        missing_skills TEXT DEFAULT '',
        matched_preferred TEXT DEFAULT '',
        status TEXT DEFAULT 'New',
        notes TEXT DEFAULT '',
        recommendation TEXT DEFAULT '',
        is_demo INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    """)

    # Create indexes for fast filtering and ranking
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_job_id ON candidates(job_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates(score DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status)")

    conn.commit()
    conn.close()
    print("HireSense AI database schema initialized successfully.")

if __name__ == "__main__":
    init_db()