import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from database import get_db_connection
import requests
import json
from datetime import datetime

def setup_google_oauth():
    st.title("Welcome to Personal Finance Manager")
    
    try:
        # Get the Replit URL and construct redirect URI
        replit_url = f"https://financetrackpro.sv10491.repl.co"
        redirect_uri = f"{replit_url}/callback"
        
        # Google OAuth configuration
        client_config = {
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
                "javascript_origins": [replit_url]
            }
        }

        # Initialize OAuth flow with exact redirect URI
        flow = Flow.from_client_config(
            client_config,
            scopes=["openid", "email", "profile"],
            redirect_uri=redirect_uri
        )
        
        if "oauth_state" not in st.session_state:
            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
            st.session_state.oauth_state = state
            
            # Create a more visually appealing login button
            st.markdown("""
                <div style="display: flex; justify-content: center; margin: 2em;">
                    <a href="{}" target="_self" style="
                        text-decoration: none;
                        background-color: #4285f4;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 4px;
                        display: inline-flex;
                        align-items: center;
                        font-family: 'Google Sans',arial,sans-serif;
                        font-weight: 500;
                        letter-spacing: .25px;
                        box-shadow: 0 2px 4px 0 rgba(0,0,0,.25);">
                        <svg style="margin-right: 10px;" width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                        </svg>
                        Sign in with Google
                    </a>
                </div>
            """.format(authorization_url), unsafe_allow_html=True)
            
            # Add descriptive text
            st.markdown("""
                ### 🚀 Get Started with Personal Finance Manager
                
                Track your expenses, set budgets, and take control of your financial future.
                
                #### Features:
                - 📊 Visualize your spending patterns
                - 💰 Set and monitor budgets
                - 📱 Track transactions on the go
                - 📈 Get insights into your financial habits
                
                Sign in with your Google account to begin.
            """)
        
        # Handle OAuth callback with improved error handling
        if "code" in st.query_params:
            try:
                flow.fetch_token(code=st.query_params["code"])
                credentials = flow.credentials
                user_info = get_or_create_user(credentials)
                
                if user_info:
                    st.session_state.user = user_info
                    st.query_params.clear()
                    st.rerun()
                else:
                    raise Exception("Failed to get user information")
                
            except requests.exceptions.SSLError as ssl_error:
                st.error("SSL Certificate Error. Please try again.")
                log_oauth_error("SSL Error", str(ssl_error))
                
            except requests.exceptions.ConnectionError as conn_error:
                st.error("Connection Error. Please check your internet connection and try again.")
                log_oauth_error("Connection Error", str(conn_error))
                
            except requests.exceptions.HTTPError as http_error:
                error_message = "Authentication failed"
                if http_error.response.status_code == 400:
                    error_message = "Invalid request. Please try again."
                elif http_error.response.status_code == 401:
                    error_message = "Unauthorized. Please check your credentials."
                elif http_error.response.status_code == 403:
                    error_message = "Access forbidden. Please check your permissions."
                    
                st.error(error_message)
                log_oauth_error("HTTP Error", str(http_error))
                
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
                log_oauth_error("General Error", str(e))
                
            finally:
                if "oauth_state" in st.session_state:
                    del st.session_state.oauth_state

    except Exception as e:
        st.error("Failed to initialize authentication")
        st.info("Please ensure all required environment variables are set correctly.")
        log_oauth_error("Initialization Error", str(e))

def check_authentication():
    return "user" in st.session_state

def get_or_create_user(credentials):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get user info from Google with error handling
        try:
            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={'Authorization': f'Bearer {credentials.token}'},
                timeout=10
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
        except requests.exceptions.RequestException as e:
            st.error("Failed to fetch user information from Google")
            log_oauth_error("Google API Error", str(e))
            return None
        
        # Check if user exists
        cur.execute("SELECT id, email FROM users WHERE google_id = %s", (userinfo['id'],))
        user = cur.fetchone()
        
        if not user:
            cur.execute("""
                INSERT INTO users (email, google_id)
                VALUES (%s, %s)
                RETURNING id, email
            """, (userinfo['email'], userinfo['id']))
            user = cur.fetchone()
            conn.commit()
        
        return {"id": user[0], "email": user[1]} if user else None
        
    except Exception as e:
        st.error("Database error while processing user information")
        log_oauth_error("Database Error", str(e))
        return None
    finally:
        cur.close()
        conn.close()

def log_oauth_error(error_type, error_message):
    """Log OAuth errors for debugging"""
    error_log = {
        "timestamp": str(datetime.now()),
        "type": error_type,
        "message": error_message
    }
    print(f"OAuth Error: {json.dumps(error_log)}")  # For server logs
