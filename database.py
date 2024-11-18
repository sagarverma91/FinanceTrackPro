import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_db_connection():
    return psycopg2.connect(
        host=os.environ['PGHOST'],
        database=os.environ['PGDATABASE'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        port=os.environ['PGPORT']
    )

def init_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create necessary tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            google_id VARCHAR(255) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            amount DECIMAL(10,2) NOT NULL,
            category VARCHAR(50),
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            bank_reference VARCHAR(255)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            category VARCHAR(50),
            amount DECIMAL(10,2),
            period VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

@st.cache_data
def get_user_transactions(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT * FROM transactions 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    return transactions

def save_transaction(user_id, amount, category, description, bank_reference=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (user_id, amount, category, description, bank_reference)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, amount, category, description, bank_reference))
    conn.commit()
    cur.close()
    conn.close()
