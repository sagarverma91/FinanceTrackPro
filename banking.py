import gocardless_pro
import streamlit as st
from database import save_transaction

def setup_gocardless():
    client = gocardless_pro.Client(
        access_token=st.secrets["GOCARDLESS_ACCESS_TOKEN"],
        environment='live'
    )
    
    try:
        # Create new customer
        customer = client.customers.create(
            params={
                "email": st.session_state.user["email"],
                "given_name": "User",
                "family_name": "Name",
                "country_code": "GB"
            }
        )
        
        # Create bank authorization flow
        redirect_flow = client.redirect_flows.create(
            params={
                "description": "Connect your bank account",
                "session_token": st.session_state.user["id"],
                "success_redirect_url": "http://localhost:5000/callback"
            }
        )
        
        st.markdown(f"[Connect Your Bank]({redirect_flow.redirect_url})")
        
    except Exception as e:
        st.error(f"Failed to setup bank connection: {str(e)}")

def sync_transactions(user_id):
    client = gocardless_pro.Client(
        access_token=st.secrets["GOCARDLESS_ACCESS_TOKEN"],
        environment='live'
    )
    
    try:
        # Get transactions from GoCardless
        transactions = client.payments.list().records
        
        for transaction in transactions:
            save_transaction(
                user_id=user_id,
                amount=transaction.amount,
                category="Uncategorized",
                description=transaction.description,
                bank_reference=transaction.id
            )
            
        return True
    except Exception as e:
        st.error(f"Failed to sync transactions: {str(e)}")
        return False
