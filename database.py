import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.environ['PGHOST'],
            database=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            port=os.environ['PGPORT']
        )
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        raise

def init_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category)
            )
        """)
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

@st.cache_data(ttl=300)
def get_user_transactions(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            ORDER BY date DESC
        """, (user_id,))
        return cur.fetchall()
    except Exception as e:
        st.error(f"Error fetching transactions: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()

def save_transaction(user_id, amount, category, description, bank_reference=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO transactions (user_id, amount, category, description, bank_reference)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, amount, category, description, bank_reference))
        conn.commit()
    except Exception as e:
        st.error(f"Error saving transaction: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()
