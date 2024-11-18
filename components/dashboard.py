import streamlit as st
from database import get_user_transactions
import visualization as viz
import pandas as pd

def show_dashboard():
    col1, col2 = st.columns(2)
    
    # Get user's transaction data
    transactions = get_user_transactions(st.session_state.user["id"])
    
    with col1:
        # Spending trend
        spending_trend = viz.create_spending_trend(transactions)
        st.plotly_chart(spending_trend, use_container_width=True)
        
        # Recent transactions
        st.subheader("Recent Transactions")
        for transaction in transactions[:5]:
            st.write(f"{transaction['date']}: ${transaction['amount']} - {transaction['description']}")
    
    with col2:
        # Category breakdown
        category_chart = viz.create_category_breakdown(transactions)
        st.plotly_chart(category_chart, use_container_width=True)
        
        # Budget overview
        st.subheader("Budget Overview")
        budget_progress = viz.create_budget_progress(
            get_budget_data(),
            get_actual_spending()
        )
        st.plotly_chart(budget_progress, use_container_width=True)

def get_budget_data():
    # Get budget data from database
    return pd.DataFrame({
        'category': ['Food', 'Transport', 'Entertainment'],
        'amount': [500, 200, 300]
    })

def get_actual_spending():
    # Calculate actual spending from transactions
    return pd.DataFrame({
        'category': ['Food', 'Transport', 'Entertainment'],
        'amount': [450, 180, 250]
    })
