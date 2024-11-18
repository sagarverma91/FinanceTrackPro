import streamlit as st
from auth import check_authentication, setup_google_oauth
from components import dashboard, budget, transactions
from database import init_database
import visualization as viz

st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide"
)

def main():
    # Initialize database
    init_database()
    
    # Setup authentication
    if not check_authentication():
        setup_google_oauth()
        return

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Transactions", "Budget", "Settings"]
    )

    # Header
    st.header(f"Personal Finance Manager - {page}")

    if page == "Dashboard":
        dashboard.show_dashboard()
    elif page == "Transactions":
        transactions.show_transactions()
    elif page == "Budget":
        budget.show_budget()
    elif page == "Settings":
        show_settings()

def show_settings():
    st.subheader("Settings")
    if st.button("Connect Bank Account"):
        banking.setup_gocardless()
    
    if st.button("Configure Email Reports"):
        st.text_input("Email Address")
        st.selectbox("Report Frequency", ["Weekly", "Monthly"])

if __name__ == "__main__":
    main()
