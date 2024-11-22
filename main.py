import streamlit as st
# Must call set_page_config as the first Streamlit command
st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide"
)

import logging
import traceback
import os
from components import dashboard, budget, transactions
from database import init_database, get_db_connection
from auth import initialize_mock_data
import visualization as viz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Load custom CSS
with open('.streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
def main():
    try:
        # Initialize database
        init_database()
        
        # Check if user is authenticated
        if "user" not in st.session_state:
            # Show landing page for non-authenticated users
            from components.landing import show_landing
            show_landing()
            
            # Handle Get Started button click
            if st.session_state.get("cta_button", False):
                # Create mock user for demo
                conn = get_db_connection()
                cur = conn.cursor()
                try:
                    # Insert mock user
                    cur.execute(
                        "INSERT INTO users (id, email) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                        (1, "dev@example.com")
                    )
                    conn.commit()
                    
                    # Set session state
                    st.session_state["user"] = {"id": 1, "email": "dev@example.com"}
                    
                    # Initialize mock data after user exists
                    initialize_mock_data(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to initialize user: {str(e)}")
                finally:
                    cur.close()
                    conn.close()
            return
        
        # Show navigation and content for authenticated users
        st.sidebar.markdown("### Navigation")
        
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
