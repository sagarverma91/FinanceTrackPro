import streamlit as st
import logging
import traceback
import os
from components import dashboard, budget, transactions
import database
from auth import initialize_mock_data
import visualization as viz

# Must call set_page_config as the first Streamlit command
st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load and inject custom CSS
def load_css():
    try:
        logger.info("Loading CSS...")
        with open('.streamlit/style.css') as f:
            css = f.read()
            # Inject the CSS with proper encoding
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
        logger.info("CSS loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CSS: {str(e)}")
        st.error("Failed to load styling. The application may not look as intended.")

# Load CSS at the start
if "css_loaded" not in st.session_state:
    load_css()
    st.session_state.css_loaded = True

def main():
    try:
        # Add debug logging
        logger.info("Starting main application flow")
        
        # Initialize database with better error handling
        try:
            database.init_database()
            logger.info("Database initialized successfully")
            
            # Verify database connection
            conn = database.get_db_connection()
            if conn:
                logger.info("Database connection established")
                conn.close()
                logger.info("Database connection verified and closed")
            else:
                logger.error("Failed to establish database connection")
                raise Exception("Database connection failed")
            
        except Exception as db_error:
            logger.error(f"Database initialization error: {str(db_error)}")
            st.error("Failed to initialize database. Please try again.")
            return
        
        # Initialize session state if needed
        if "page" not in st.session_state:
            st.session_state.page = "Landing"
            
        # Clear any existing streamlit elements
        st.empty()
        
        # Check if user is authenticated
        if "user" not in st.session_state:
            logger.info("User not authenticated, showing landing page")
            # Show landing page for non-authenticated users
            try:
                from components.landing import show_landing
                logger.info("Landing page component imported successfully")
                st.empty()  # Clear any existing content
                show_landing()
                logger.info("Landing page rendered successfully")
            except Exception as e:
                logger.error(f"Failed to load landing page: {str(e)}")
                logger.error(traceback.format_exc())
                st.error("Failed to load the landing page. Please try refreshing.")
            
            # Handle Get Started button click
            if st.session_state.get("cta_button", False):
                # Create mock user for demo
                conn = database.get_db_connection()
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
            index=0  # Always default to Dashboard
        )

        # Update session state
        st.session_state["page"] = selected_page

        # Add return to landing page button
        if st.sidebar.button("Return to Landing Page", type="secondary"):
            # Clear session state
            st.session_state.clear()
            st.rerun()

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
