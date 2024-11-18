import pandas as pd
from datetime import datetime, timedelta

def format_currency(amount):
    return f"${amount:,.2f}"

def calculate_spending_metrics(transactions):
    df = pd.DataFrame(transactions)
    
    return {
        'total_spent': df['amount'].sum(),
        'average_transaction': df['amount'].mean(),
        'transaction_count': len(df),
        'largest_transaction': df['amount'].max()
    }

def get_date_range(period):
    today = datetime.now()
    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    elif period == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)
    
    return start_date, today

def categorize_transaction(description):
    # Simple rule-based categorization
    keywords = {
        'food': ['restaurant', 'cafe', 'grocery', 'food'],
        'transport': ['uber', 'taxi', 'train', 'bus', 'transport'],
        'entertainment': ['cinema', 'movie', 'theater', 'concert'],
        'shopping': ['amazon', 'shop', 'store', 'retail'],
        'bills': ['utility', 'electricity', 'water', 'gas', 'internet']
    }
    
    description = description.lower()
    for category, words in keywords.items():
        if any(word in description for word in words):
            return category
    
    return "Other"
