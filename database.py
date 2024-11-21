import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
import logging

logger = logging.getLogger(__name__)

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
        logger.error(f"Database connection error: {str(e)}")
        st.error(f"Database connection error. Please try again.")
        raise

def init_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create tables in proper order
        logger.info("Creating database tables...")
        
        # Users table first
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                google_id VARCHAR(255) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Users table created successfully")
        
        # Categories table second
        cur.execute('''
            CREATE TABLE IF NOT EXISTS transaction_categories (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                name VARCHAR(50) NOT NULL,
                icon VARCHAR(20),
                color VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, name)
            )
        ''')
        logger.info("Transaction categories table created successfully")
        
        # Transactions table third
        cur.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(50),
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bank_reference VARCHAR(255),
                tags TEXT[]
            )
        ''')
        logger.info("Transactions table created successfully")
        
        # Budgets table last
        cur.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                category VARCHAR(50),
                amount DECIMAL(10,2),
                period VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, period)
            )
        ''')
        logger.info("Budgets table created successfully")
        
        conn.commit()
        logger.info("All tables created successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Database initialization error: {str(e)}")
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
        logger.error(f"Error fetching transactions: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()

def get_user_categories(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT name, icon, color FROM transaction_categories 
            WHERE user_id = %s 
            ORDER BY name
        """, (user_id,))
        categories = cur.fetchall()
        if not categories:
            # Insert default categories if none exist
            default_categories = [
                ('Food', '🍽️', '#FF6B6B'),
                ('Transport', '🚗', '#4ECDC4'),
                ('Entertainment', '🎮', '#45B7D1'),
                ('Shopping', '🛍️', '#96CEB4'),
                ('Bills', '📄', '#FFEEAD'),
                ('Other', '📌', '#D4D4D4')
            ]
            for cat in default_categories:
                cur.execute("""
                    INSERT INTO transaction_categories (user_id, name, icon, color)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, name) DO NOTHING
                """, (user_id, cat[0], cat[1], cat[2]))
            conn.commit()
            cur.execute("""
                SELECT name, icon, color FROM transaction_categories 
                WHERE user_id = %s 
                ORDER BY name
            """, (user_id,))
            categories = cur.fetchall()
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()

def save_transaction(user_id, amount, category, description, date=None, bank_reference=None, tags=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO transactions (user_id, amount, category, description, date, bank_reference, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, amount, category, description, date, bank_reference, tags))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving transaction: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

def save_category(user_id, name, icon, color):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO transaction_categories (user_id, name, icon, color)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, name) 
            DO UPDATE SET icon = EXCLUDED.icon, color = EXCLUDED.color
        """, (user_id, name, icon, color))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving category: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()
