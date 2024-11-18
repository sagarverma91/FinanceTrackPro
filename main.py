import streamlit as st
from auth import check_authentication, setup_google_oauth
from components import dashboard, budget, transactions
from database import init_database
import visualization as viz
import logging
import sys
import traceback

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide"
)

def main():
    try:
        # Initialize database
        init_database()
        
        # Development mode - bypass authentication
        if st.query_params.get("dev_mode"):
            st.session_state["user"] = {"id": 1, "email": "dev@example.com"}
            st.session_state["authentication_status"] = True
        
        # Check authentication
        if not check_authentication():
            setup_google_oauth()
            return

        # If authenticated, show the navigation and content
        st.sidebar.markdown(f"Welcome, {st.session_state.user['email']}")
        
        # Navigation
        selected_page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Transactions", "Budget", "Settings"],
            index=["Dashboard", "Transactions", "Budget", "Settings"].index(
                st.session_state.get("page", "Dashboard")
            )
        )

        # Update session state
        st.session_state["page"] = selected_page

        # Header
        st.header(f"Personal Finance Manager - {selected_page}")
        
        try:
            logger.info(f"Loading {selected_page} page...")
            if selected_page == "Dashboard":
                dashboard.show_dashboard()
            elif selected_page == "Transactions":
                transactions.show_transactions()
            elif selected_page == "Budget":
                budget.show_budget()
            elif selected_page == "Settings":
                show_settings()
            logger.info(f"{selected_page} page loaded successfully")
        except Exception as page_error:
            logger.error(f"Error in {selected_page} page: {str(page_error)}")
            logger.error(traceback.format_exc())
            st.error(f"An error occurred while loading the {selected_page} page. Please try again.")
            
    except Exception as e:
        logger.error(f"Critical application error: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("An error occurred while starting the application.")
        st.info("Please try refreshing the page. If the problem persists, contact support.")

def show_settings():
    st.subheader("Settings")
    
    # Email report settings
    st.subheader("Email Reports")
    email = st.text_input("Email Address", value=st.session_state.user.get("email", ""))
    frequency = st.selectbox("Report Frequency", ["Weekly", "Monthly"])
    if st.button("Save Email Preferences"):
        try:
            save_email_preferences(email, frequency)
            st.success("Email preferences saved successfully!")
        except Exception as e:
            logger.error(f"Error saving email preferences: {str(e)}")
            logger.error(traceback.format_exc())
            st.error("Failed to save email preferences. Please try again.")

def save_email_preferences(email, frequency):
    # TODO: Implement email preferences saving
    pass

if __name__ == "__main__":
    main()