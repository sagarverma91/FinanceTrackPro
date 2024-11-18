import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from database import get_user_transactions
import pandas as pd

def send_monthly_report(user_email, user_id):
    # Get transaction data
    transactions = get_user_transactions(user_id)
    df = pd.DataFrame(transactions)
    
    # Create report content
    total_spent = df['amount'].sum()
    top_categories = df.groupby('category')['amount'].sum().nlargest(5)
    
    # Create email content
    msg = MIMEMultipart()
    msg['Subject'] = 'Monthly Financial Report'
    msg['From'] = st.secrets["EMAIL_FROM"]
    msg['To'] = user_email
    
    body = f"""
    Monthly Financial Summary
    
    Total Spent: ${total_spent:.2f}
    
    Top Spending Categories:
    {top_categories.to_string()}
    
    View your full dashboard at: http://localhost:5000
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(st.secrets["EMAIL_USERNAME"], st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False
