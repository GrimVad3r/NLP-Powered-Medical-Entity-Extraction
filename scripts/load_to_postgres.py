import json
import psycopg2
from pathlib import Path
from psycopg2.extras import execute_values
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import get_settings

# Database connection config

settings = get_settings()

DB_CONFIG = {
    "dbname": settings.db_name,
    "user": "postgres",
    "password": settings.db_password,
    "host": settings.db_host,
    "port": settings.db_port
}

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 1. Create Schema and Tables
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            message_id TEXT PRIMARY KEY,
            channel_name TEXT,
            text TEXT,
            metadata JSONB,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.nlp_results (
            message_id TEXT PRIMARY KEY,
            channel_name TEXT,
            is_medical BOOLEAN,
            entities JSONB,
            quality_score FLOAT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Load Raw Files
    raw_path = Path("data/raw")
    for channel_dir in raw_path.iterdir():
        if channel_dir.is_dir():
            for file in channel_dir.glob("*.json"):
                with open(file, 'r', encoding='utf-8') as f:
                    msgs = json.load(f)
                    # Prepare data for batch insert
                    data = [(f"{channel_dir.name}_{m['id']}", channel_dir.name, m.get('text', ''), json.dumps(m)) for m in msgs]
                    execute_values(cur, """
                        INSERT INTO raw.telegram_messages (message_id, channel_name, text, metadata)
                        VALUES %s ON CONFLICT (message_id) DO UPDATE SET metadata = EXCLUDED.metadata
                    """, data)

    # 3. Load Processed Files (NLP)
    processed_path = Path("data/processed")
    for channel_dir in processed_path.iterdir():
        if channel_dir.is_dir():
            for file in channel_dir.glob("*.json"):
                with open(file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    data = [
                                (
                                    f"{channel_dir.name}_{r.get('message_id', r.get('id', i))}", 
                                    channel_dir.name, 
                                    r.get('is_medical', False), 
                                    json.dumps(r.get('entities', [])), 
                                    r.get('quality_score', 0.0)
                                ) 
                                for i, r in enumerate(results)
                            ]
                    execute_values(cur, """
                        INSERT INTO raw.nlp_results (message_id, channel_name, is_medical, entities, quality_score)
                        VALUES %s ON CONFLICT (message_id) DO UPDATE SET entities = EXCLUDED.entities
                    """, data)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Successfully loaded data to PostgreSQL")

if __name__ == "__main__":
    load_data()