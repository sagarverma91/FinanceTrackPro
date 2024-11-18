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
    try:
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
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page. If the problem persists, contact support.")

def show_settings():
    st.subheader("Settings")
    
    # Email report settings
    st.subheader("Email Reports")
    email = st.text_input("Email Address", value=st.session_state.user.get("email", ""))
    frequency = st.selectbox("Report Frequency", ["Weekly", "Monthly"])
    if st.button("Save Email Preferences"):
        save_email_preferences(email, frequency)
        st.success("Email preferences saved successfully!")

def save_email_preferences(email, frequency):
    # TODO: Implement email preferences saving
    pass

if __name__ == "__main__":
    main()
