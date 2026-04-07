import sqlite3

DB_PATH = "jobs.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT,
        location TEXT,
        experience_level TEXT,
        description TEXT,
        skills TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_job(job):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO jobs (id, title, location, experience_level, description, skills)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job["id"],
        job["title"],
        job["location"],
        job["experience_level"],
        job["description"],
        ",".join(job["requirements"]["required_skills"])
    ))

    conn.commit()
    conn.close()


def get_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()

    conn.close()

    jobs = []
    for r in rows:
        jobs.append({
            "id": r[0],
            "title": r[1],
            "location": r[2],
            "experience_level": r[3],
            "description": r[4],
            "requirements": {
                "required_skills": r[5].split(",") if r[5] else []
            }
        })

    return jobs


def delete_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()