#!/usr/bin/env python3
import sqlite3

DB_PATH = 'carriers.db'

NEW_COLUMNS = [
    ('final_rate', 'TEXT'),
    ('initial_rate', 'TEXT'),
    ('transcript', 'TEXT'),
    ('call_duration', 'REAL'),
    ('booked_at', 'TEXT')
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    altered = False
    for col, coltype in NEW_COLUMNS:
        if not column_exists(cursor, 'carriers', col):
            print(f"Adding column: {col} ({coltype})")
            cursor.execute(f'ALTER TABLE carriers ADD COLUMN {col} {coltype}')
            altered = True
        else:
            print(f"Column already exists: {col}")
    if altered:
        print("Migration complete. New columns added.")
    else:
        print("No changes needed. All columns already exist.")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate() 