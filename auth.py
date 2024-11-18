import os
import streamlit as st
from database import get_db_connection
import requests
import json
from datetime import datetime, timedelta
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

def initialize_mock_data(user_id):
    """Initialize sample data for the mock user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Initialize default categories
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
        
        # Add sample transactions
        sample_transactions = [
            (75.50, 'Food', 'Grocery shopping', datetime.now() - timedelta(days=5)),
            (45.00, 'Transport', 'Uber ride', datetime.now() - timedelta(days=3)),
            (120.00, 'Entertainment', 'Movie night', datetime.now() - timedelta(days=2)),
            (250.00, 'Shopping', 'New clothes', datetime.now() - timedelta(days=1)),
            (100.00, 'Bills', 'Electricity bill', datetime.now())
        ]
        
        for trans in sample_transactions:
            cur.execute("""
                INSERT INTO transactions (user_id, amount, category, description, date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (user_id, trans[0], trans[1], trans[2], trans[3]))
        
        # Add sample budget
        sample_budgets = [
            ('Food', 500.00, 'Monthly'),
            ('Transport', 200.00, 'Monthly'),
            ('Entertainment', 300.00, 'Monthly'),
            ('Shopping', 400.00, 'Monthly'),
            ('Bills', 600.00, 'Monthly')
        ]
        
        for budget in sample_budgets:
            cur.execute("""
                INSERT INTO budgets (user_id, category, amount, period)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, category, period, start_date) DO NOTHING
            """, (user_id, budget[0], budget[1], budget[2]))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize mock data: {str(e)}")
        st.error("Failed to initialize mock data")
    finally:
        cur.close()
        conn.close()

def log_oauth_error(error_type, error_message):
    """Log OAuth errors for debugging"""
    error_log = {
        "timestamp": str(datetime.now()),
        "type": error_type,
        "message": error_message
    }
    print(f"OAuth Error: {json.dumps(error_log)}")  # For server logs