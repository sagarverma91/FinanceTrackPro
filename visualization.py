import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_spending_trend(transactions_data):
    df = pd.DataFrame(transactions_data)
    df['date'] = pd.to_datetime(df['date'])
    
    fig = px.line(
        df.groupby(df['date'].dt.date)['amount'].sum().reset_index(),
        x='date',
        y='amount',
        title='Daily Spending Trend'
    )
    return fig

def create_category_breakdown(transactions_data):
    df = pd.DataFrame(transactions_data)
    
    fig = px.pie(
        df.groupby('category')['amount'].sum().reset_index(),
        values='amount',
        names='category',
        title='Spending by Category'
    )
    return fig

def create_budget_progress(budget_data, actual_spending):
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
