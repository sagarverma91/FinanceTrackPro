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
        logger.info("Starting application initialization...")
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialization completed successfully")
        
        # Setup authentication
        logger.info("Checking authentication status...")
        if not check_authentication():
            logger.info("User not authenticated, showing login page...")
            try:
                setup_google_oauth()
                logger.info("Google OAuth setup completed")
            except Exception as auth_error:
                logger.error(f"Error in OAuth setup: {str(auth_error)}")
                logger.error(traceback.format_exc())
                st.error("Failed to setup authentication. Please try again.")
            return

        # Sidebar navigation with page state management
        logger.info("Setting up navigation...")
        page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Transactions", "Budget", "Settings"],
            key="page"  # Add key parameter for state management
        )

        # Header
        st.header(f"Personal Finance Manager - {page}")
        
        try:
            logger.info(f"Loading {page} page...")
            if page == "Dashboard":
                dashboard.show_dashboard()
            elif page == "Transactions":
                transactions.show_transactions()
            elif page == "Budget":
                budget.show_budget()
            elif page == "Settings":
                show_settings()
            logger.info(f"{page} page loaded successfully")
        except Exception as page_error:
            logger.error(f"Error in {page} page: {str(page_error)}")
            logger.error(traceback.format_exc())
            st.error(f"An error occurred while loading the {page} page. Please try again.")
            
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
