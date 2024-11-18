import streamlit as st
from database import get_db_connection
import pandas as pd

def show_budget():
    st.subheader("Budget Management")
    
    # Budget form
    with st.form("budget_form"):
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]
        )
        amount = st.number_input("Budget Amount", min_value=0.0, step=10.0)
        period = st.selectbox("Period", ["Monthly", "Weekly"])
        
        if st.form_submit_button("Set Budget"):
            save_budget(category, amount, period)
            st.success(f"Budget set for {category}")
    
    # Show current budgets
    show_budget_table()

def save_budget(category, amount, period):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO budgets (user_id, category, amount, period)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, category) 
        DO UPDATE SET amount = %s, period = %s
    """, (st.session_state.user["id"], category, amount, period, amount, period))
    
    conn.commit()
    cur.close()
    conn.close()

def show_budget_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT category, amount, period
        FROM budgets
        WHERE user_id = %s
    """, (st.session_state.user["id"],))
    
    budgets = cur.fetchall()
    if budgets:
        df = pd.DataFrame(budgets, columns=["Category", "Amount", "Period"])
        st.dataframe(df)
    
    cur.close()
    conn.close()
