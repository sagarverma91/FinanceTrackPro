import streamlit as st
from database import get_db_connection, get_user_transactions
import pandas as pd
from utils import categorize_transaction
import io
import csv
from datetime import datetime, timedelta

def show_transactions():
    st.subheader("Transactions")
    
    # Transaction filters
    col1, col2 = st.columns(2)
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now())
        )
    with col2:
        category_filter = st.multiselect(
            "Categories",
            ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]
        )
    
    # Add CSV Import
    st.subheader("Import Transactions")
    csv_file = st.file_uploader("Upload CSV file", type=['csv'])
    if csv_file is not None:
        import_transactions_from_csv(csv_file)
    
    # Manual transaction entry
    st.subheader("Add Transaction")
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount", min_value=0.0, step=1.0)
            category = st.selectbox(
                "Category",
                ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]
            )
        with col2:
            date = st.date_input("Date", value=datetime.now())
            description = st.text_input("Description")
        
        if st.form_submit_button("Add Transaction"):
            save_manual_transaction(amount, category, description, date)
            st.success("Transaction added successfully")
            st.rerun()
    
    # Get and display transactions
    transactions = get_filtered_transactions(date_range, category_filter)
    if transactions:
        st.subheader("Transaction List")
        for idx, transaction in enumerate(transactions):
            with st.expander(f"{transaction['date'].strftime('%Y-%m-%d')} - ${transaction['amount']:,.2f} - {transaction['description']}"):
                edit_transaction(transaction, idx)
    else:
        st.info("No transactions found")

def edit_transaction(transaction, idx):
    with st.form(f"edit_transaction_{idx}"):
        col1, col2 = st.columns(2)
        with col1:
            new_amount = st.number_input("Amount", value=float(transaction['amount']), min_value=0.0, step=1.0)
            new_category = st.selectbox(
                "Category",
                ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"],
                index=["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"].index(transaction['category'])
            )
        with col2:
            new_date = st.date_input("Date", value=transaction['date'])
            new_description = st.text_input("Description", value=transaction['description'])
        
        if st.form_submit_button("Update Transaction"):
            update_transaction(
                transaction['id'],
                new_amount,
                new_category,
                new_description,
                new_date
            )
            st.success("Transaction updated successfully")
            st.rerun()
        
        if st.form_submit_button("Delete Transaction", type="secondary"):
            delete_transaction(transaction['id'])
            st.success("Transaction deleted successfully")
            st.rerun()

def import_transactions_from_csv(csv_file):
    try:
        content = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(content))
        
        for row in csv_data:
            try:
                amount = float(row.get('amount', 0))
                date = datetime.strptime(row.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
                description = row.get('description', '')
                category = row.get('category', categorize_transaction(description))
                
                save_manual_transaction(amount, category, description, date)
            except ValueError as e:
                st.warning(f"Skipped invalid row: {str(e)}")
        
        st.success("CSV import completed successfully")
        st.rerun()
    except Exception as e:
        st.error(f"Error importing CSV: {str(e)}")

def get_filtered_transactions(date_range, categories):
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT id, amount, category, description, date
        FROM transactions
        WHERE user_id = %s
        AND date::date BETWEEN %s AND %s
    """
    params = [st.session_state.user["id"], date_range[0], date_range[1]]
    
    if categories:
        query += " AND category = ANY(%s)"
        params.append(categories)
    
    query += " ORDER BY date DESC"
    
    cur.execute(query, params)
    transactions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if transactions:
        return [
            {
                'id': t[0],
                'amount': t[1],
                'category': t[2],
                'description': t[3],
                'date': t[4]
            }
            for t in transactions
        ]
    return []

def save_manual_transaction(amount, category, description, date):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO transactions (user_id, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (st.session_state.user["id"], amount, category, description, date))
    
    conn.commit()
    cur.close()
    conn.close()

def update_transaction(transaction_id, amount, category, description, date):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE transactions
        SET amount = %s, category = %s, description = %s, date = %s
        WHERE id = %s AND user_id = %s
    """, (amount, category, description, date, transaction_id, st.session_state.user["id"]))
    
    conn.commit()
    cur.close()
    conn.close()

def delete_transaction(transaction_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        DELETE FROM transactions
        WHERE id = %s AND user_id = %s
    """, (transaction_id, st.session_state.user["id"]))
    
    conn.commit()
    cur.close()
    conn.close()
