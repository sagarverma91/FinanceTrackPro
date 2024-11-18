import streamlit as st
from database import get_db_connection, get_user_transactions
import pandas as pd

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
    
    # Get and display transactions
    transactions = get_filtered_transactions(date_range, category_filter)
    if transactions:
        df = pd.DataFrame(transactions)
        st.dataframe(df)
    else:
        st.info("No transactions found")
    
    # Manual transaction entry
    st.subheader("Add Transaction")
    with st.form("transaction_form"):
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]
        )
        description = st.text_input("Description")
        
        if st.form_submit_button("Add Transaction"):
            save_manual_transaction(amount, category, description)
            st.success("Transaction added successfully")

def get_filtered_transactions(date_range, categories):
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT * FROM transactions
        WHERE user_id = %s
        AND date BETWEEN %s AND %s
    """
    params = [st.session_state.user["id"], date_range[0], date_range[1]]
    
    if categories:
        query += " AND category = ANY(%s)"
        params.append(categories)
    
    cur.execute(query, params)
    transactions = cur.fetchall()
    
    cur.close()
    conn.close()
    return transactions

def save_manual_transaction(amount, category, description):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO transactions (user_id, amount, category, description)
        VALUES (%s, %s, %s, %s)
    """, (st.session_state.user["id"], amount, category, description))
    
    conn.commit()
    cur.close()
    conn.close()
