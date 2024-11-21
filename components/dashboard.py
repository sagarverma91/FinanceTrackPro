import streamlit as st
from database import get_user_transactions, get_db_connection
import visualization as viz
import pandas as pd

def show_dashboard():
    # Add a prominent dashboard button at the top
    st.markdown("### 🏠 Dashboard Overview")
    if st.button("Show Welcome Message", type="primary", key="welcome_btn"):
        st.markdown("## 👋 Welcome to your dashboard!")
        st.write("Here you can track all your financial activities.")
        st.balloons()
    
    # Add a visual separator
    st.markdown("---")
    
    # Rest of the dashboard content
    col1, col2 = st.columns(2)
    
    # Get user's transaction data
    transactions = get_user_transactions(st.session_state.user["id"])
    
    with col1:
        # Key metrics
        if transactions:
            df = pd.DataFrame(transactions)
            total_spent = df['amount'].sum()
            avg_transaction = df['amount'].mean()
            st.metric("Total Spent", f"${total_spent:,.2f}")
            st.metric("Average Transaction", f"${avg_transaction:,.2f}")
        
        # Spending trend
        spending_trend = viz.create_spending_trend(transactions)
        st.plotly_chart(spending_trend, use_container_width=True, key="spending_trend_chart")
        
        # Recent transactions
        st.subheader("Recent Transactions")
        if transactions:
            for transaction in transactions[:5]:
                st.write(f"{transaction['date'].strftime('%Y-%m-%d')}: ${transaction['amount']:,.2f} - {transaction['description']}")
        else:
            st.info("No recent transactions")
    
    with col2:
        # Category breakdown
        category_chart = viz.create_category_breakdown(transactions)
        st.plotly_chart(category_chart, use_container_width=True, key="category_breakdown_chart")
        
        # Budget overview
        st.subheader("Budget Overview")
        budget_data = get_budget_data()
        actual_spending = get_actual_spending(transactions)
        if not budget_data.empty and not actual_spending.empty:
            budget_progress = viz.create_budget_progress(budget_data, actual_spending)
            st.plotly_chart(budget_progress, use_container_width=True, key="budget_progress_chart")
        else:
            st.info("Set up your budget to see the overview")

def get_budget_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT category, amount
        FROM budgets
        WHERE user_id = %s
    """, (st.session_state.user["id"],))
    
    budgets = cur.fetchall()
    cur.close()
    conn.close()
    
    if budgets:
        return pd.DataFrame(budgets, columns=['category', 'amount'])
    return pd.DataFrame()

def get_actual_spending(transactions):
    if not transactions:
        return pd.DataFrame()
    
    df = pd.DataFrame(transactions)
    actual = df.groupby('category')['amount'].sum().reset_index()
    return actual[['category', 'amount']]
