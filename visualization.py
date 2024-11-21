import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_spending_trend(transactions_data):
    if not transactions_data:
        # Return empty figure if no data
        return go.Figure()
    
    df = pd.DataFrame(transactions_data)
    # Ensure date column exists and is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        return go.Figure()
    
    fig = px.line(
        df.groupby(df['date'].dt.date)['amount'].sum().reset_index(),
        x='date',
        y='amount',
        title='Daily Spending Trend'
    )
    return fig

def create_category_breakdown(transactions_data):
    if not transactions_data:
        return go.Figure()
    
    df = pd.DataFrame(transactions_data)
    if 'category' not in df.columns or 'amount' not in df.columns:
        return go.Figure()
    
    category_sums = df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(
        category_sums,
        values='amount',
        names='category',
        title='Spending by Category'
    )
    return fig

def create_budget_progress(budget_data, actual_spending):
    if budget_data.empty or actual_spending.empty:
        return go.Figure()
        
    fig = go.Figure(data=[
        go.Bar(
            name='Budget',
            x=budget_data['category'],
            y=budget_data['amount']
        ),
        go.Bar(
            name='Actual',
            x=actual_spending['category'],
            y=actual_spending['amount']
        )
    ])
    
    fig.update_layout(
        title='Budget vs. Actual Spending',
        barmode='group'
    )
    return fig
