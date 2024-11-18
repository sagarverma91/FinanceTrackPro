import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from database import get_db_connection
import requests

def setup_google_oauth():
    st.title("Welcome to Personal Finance Manager")
    
    # Google OAuth configuration
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": st.secrets["GOOGLE_CLIENT_ID"],
                "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["openid", "email", "profile"]
    )
    
    if "oauth_state" not in st.session_state:
        authorization_url, state = flow.authorization_url()
        st.session_state.oauth_state = state
        st.markdown(f"[Login with Google]({authorization_url})")
    
    # Handle OAuth callback
    params = st.experimental_get_query_params()
    if "code" in params:
        try:
            flow.fetch_token(code=params["code"][0])
            credentials = flow.credentials
            st.session_state.user = get_or_create_user(credentials)
            st.experimental_set_query_params()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")

def check_authentication():
    return "user" in st.session_state

def get_or_create_user(credentials):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get user info from Google
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={'Authorization': f'Bearer {credentials.token}'}
    )
    userinfo = userinfo_response.json()
    
    # Check if user exists
    cur.execute("SELECT * FROM users WHERE google_id = %s", (userinfo['id'],))
    user = cur.fetchone()
    
    if not user:
        cur.execute("""
            INSERT INTO users (email, google_id)
            VALUES (%s, %s)
            RETURNING id
        """, (userinfo['email'], userinfo['id']))
        user_id = cur.fetchone()[0]
    else:
        user_id = user[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"id": user_id, "email": userinfo['email']}
