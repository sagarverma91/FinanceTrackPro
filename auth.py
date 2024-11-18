import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from database import get_db_connection
import requests

def setup_google_oauth():
    st.title("Welcome to Personal Finance Manager")
    
    try:
        # Google OAuth configuration
        client_config = {
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["https://financetrackpro.sv10491.repl.co/callback"],
                "javascript_origins": ["https://financetrackpro.sv10491.repl.co"]
            }
        }

        # Initialize OAuth flow
        flow = Flow.from_client_config(
            client_config,
            scopes=["openid", "email", "profile"],
            redirect_uri=client_config["web"]["redirect_uris"][0]
        )
        
        if "oauth_state" not in st.session_state:
            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
            st.session_state.oauth_state = state
            st.markdown(
                f'<a href="{authorization_url}" target="_self" class="button">Login with Google</a>',
                unsafe_allow_html=True
            )
            st.markdown("""
            <style>
            .button {
                background-color: #4285f4;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Handle OAuth callback
        params = st.experimental_get_query_params()
        if "code" in params:
            try:
                flow.fetch_token(code=params["code"][0])
                credentials = flow.credentials
                st.session_state.user = get_or_create_user(credentials)
                st.experimental_set_query_params()
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
                if "oauth_state" in st.session_state:
                    del st.session_state.oauth_state

    except Exception as e:
        st.error(f"Error setting up authentication: {str(e)}")
        st.write("Please ensure all required environment variables are set.")

def check_authentication():
    return "user" in st.session_state

def get_or_create_user(credentials):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get user info from Google
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
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
        st.error(f"Error getting user information: {str(e)}")
        return None
    finally:
        cur.close()
        conn.close()
