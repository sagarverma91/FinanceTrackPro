import streamlit as st
from database import (
    get_db_connection, 
    get_user_transactions, 
    get_user_categories,
    save_transaction,
    save_category
)
import pandas as pd
from utils import categorize_transaction
import io
import csv
from datetime import datetime, timedelta

def show_transactions():
    st.subheader("Transactions")
    
    # Create tabs for different transaction management features
    tab1, tab2, tab3 = st.tabs(["📝 Add Transaction", "📊 View Transactions", "⚙️ Categories"])
    
    with tab1:
        show_transaction_form()
    
    with tab2:
        show_transaction_list()
    
    with tab3:
        manage_categories()

def show_transaction_form():
    st.subheader("Add New Transaction")
    
    # Transaction form with improved layout
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "Amount ($)", 
                min_value=0.0, 
                step=1.0,
                help="Enter the transaction amount"
            )
            
            categories = get_user_categories(st.session_state.user["id"])
            category = st.selectbox(
                "Category",
                options=[cat["name"] for cat in categories],
                format_func=lambda x: f"{next((c['icon'] for c in categories if c['name'] == x), '')} {x}"
            )
        
        with col2:
            date = st.date_input(
                "Date",
                value=datetime.now(),
                help="Select the transaction date"
            )
            
            description = st.text_input(
                "Description",
                help="Enter a description for this transaction"
            )
        
        # Tags input
        tags = st.multiselect(
            "Tags",
            options=["Essential", "One-time", "Subscription", "Investment"],
            help="Add tags to organize your transactions"
        )
        
        col3, col4 = st.columns([3, 1])
        with col4:
            submit = st.form_submit_button("Add Transaction", use_container_width=True)
        
        if submit:
            save_transaction(
                st.session_state.user["id"],
                amount,
                category,
                description,
                date,
                tags=tags
            )
            st.success("Transaction added successfully")
            st.rerun()

def show_transaction_list():
    # Transaction filters
    with st.expander("🔍 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input(
                "Date Range",
                value=(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                )
            )
        
        with col2:
            categories = get_user_categories(st.session_state.user["id"])
            category_filter = st.multiselect(
                "Categories",
                options=[cat["name"] for cat in categories],
                format_func=lambda x: f"{next((c['icon'] for c in categories if c['name'] == x), '')} {x}"
            )
        
        with col3:
            min_amount = st.number_input("Min Amount", value=0.0, step=10.0)
            max_amount = st.number_input("Max Amount", value=1000000.0, step=10.0)
    
    # Import/Export options
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Import Transactions")
        csv_file = st.file_uploader("Upload CSV file", type=['csv'])
        if csv_file is not None:
            import_transactions_from_csv(csv_file)
    
    with col2:
        st.subheader("Export Transactions")
        if st.button("Export to CSV"):
            export_transactions_to_csv()
    
    # Get and display transactions
    transactions = get_filtered_transactions(date_range, category_filter, min_amount, max_amount)
    if transactions:
        st.subheader("Transaction List")
        
        # Summary metrics
        total_amount = sum(t['amount'] for t in transactions)
        avg_amount = total_amount / len(transactions)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Amount", f"${total_amount:,.2f}")
        col2.metric("Number of Transactions", len(transactions))
        col3.metric("Average Amount", f"${avg_amount:,.2f}")
        
        # Transaction list with expanded details
        for idx, transaction in enumerate(transactions):
            with st.expander(
                f"{transaction['date'].strftime('%Y-%m-%d')} - ${transaction['amount']:,.2f} - {transaction['description']}",
                expanded=False
            ):
                edit_transaction(transaction, idx)
    else:
        st.info("No transactions found")

def manage_categories():
    st.subheader("Manage Categories")
    
    # Add new category
    with st.form("category_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Category Name")
            icon = st.selectbox("Icon", ['🍽️', '🚗', '🎮', '🛍️', '📄', '🏠', '💰', '💊', '✈️', '📚', '🎵', '💡'])
        with col2:
            color = st.color_picker("Color", '#FF6B6B')
        
        if st.form_submit_button("Add Category"):
            save_category(st.session_state.user["id"], name, icon, color)
            st.success(f"Category '{name}' added successfully")
            st.rerun()
    
    # Display existing categories
    categories = get_user_categories(st.session_state.user["id"])
    if categories:
        st.subheader("Current Categories")
        cols = st.columns(3)
        for idx, category in enumerate(categories):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style="
                        padding: 10px;
                        border-radius: 5px;
                        background-color: {category['color']};
                        margin: 5px 0;
                    ">
                        {category['icon']} {category['name']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

def import_transactions_from_csv(csv_file):
    try:
        content = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(content))
        
        for row in csv_data:
            try:
                amount = float(row.get('amount', 0))
                date = datetime.strptime(row.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
                description = row.get('description', '')
                category = row.get('category', categorize_transaction(description))
                tags = row.get('tags', '').split(',') if row.get('tags') else None
                
                save_transaction(
                    st.session_state.user["id"],
                    amount,
                    category,
                    description,
                    date,
                    tags=tags
                )
            except ValueError as e:
                st.warning(f"Skipped invalid row: {str(e)}")
        
        st.success("CSV import completed successfully")
        st.rerun()
    except Exception as e:
        st.error(f"Error importing CSV: {str(e)}")

def export_transactions_to_csv():
    transactions = get_user_transactions(st.session_state.user["id"])
    if transactions:
        df = pd.DataFrame(transactions)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv"
        )
    else:
        st.warning("No transactions to export")

def get_filtered_transactions(date_range, categories, min_amount, max_amount):
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT id, amount, category, description, date, tags
        FROM transactions
        WHERE user_id = %s
        AND date::date BETWEEN %s AND %s
        AND amount BETWEEN %s AND %s
    """
    params = [st.session_state.user["id"], date_range[0], date_range[1], min_amount, max_amount]
    
    if categories:
        query += " AND category = ANY(%s)"
        params.append(categories)
    
    query += " ORDER BY date DESC"
    
    cur.execute(query, params)
    transactions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if transactions:
        return [
            {
                'id': t[0],
                'amount': t[1],
                'category': t[2],
                'description': t[3],
                'date': t[4],
                'tags': t[5]
            }
            for t in transactions
        ]
    return []

def edit_transaction(transaction, idx):
    with st.form(f"edit_transaction_{idx}"):
        col1, col2 = st.columns(2)
        with col1:
            new_amount = st.number_input(
                "Amount",
                value=float(transaction['amount']),
                min_value=0.0,
                step=1.0
            )
            
            categories = get_user_categories(st.session_state.user["id"])
            new_category = st.selectbox(
                "Category",
                options=[cat["name"] for cat in categories],
                index=[cat["name"] for cat in categories].index(transaction['category']),
                format_func=lambda x: f"{next((c['icon'] for c in categories if c['name'] == x), '')} {x}"
            )
        
        with col2:
            new_date = st.date_input("Date", value=transaction['date'])
            new_description = st.text_input("Description", value=transaction['description'])
        
        new_tags = st.multiselect(
            "Tags",
            options=["Essential", "One-time", "Subscription", "Investment"],
            default=transaction.get('tags', [])
        )
        
        col3, col4 = st.columns([3, 1])
        with col3:
            delete = st.form_submit_button("🗑️ Delete", type="secondary")
        with col4:
            update = st.form_submit_button("Update")
        
        if update:
            update_transaction(
                transaction['id'],
                new_amount,
                new_category,
                new_description,
                new_date,
                new_tags
            )
            st.success("Transaction updated successfully")
            st.rerun()
        
        if delete:
            delete_transaction(transaction['id'])
            st.success("Transaction deleted successfully")
            st.rerun()

def update_transaction(transaction_id, amount, category, description, date, tags):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE transactions
            SET amount = %s, category = %s, description = %s, date = %s, tags = %s
            WHERE id = %s AND user_id = %s
        """, (amount, category, description, date, tags, transaction_id, st.session_state.user["id"]))
        
        conn.commit()
    finally:
        cur.close()
        conn.close()

def delete_transaction(transaction_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            DELETE FROM transactions
            WHERE id = %s AND user_id = %s
        """, (transaction_id, st.session_state.user["id"]))
        
        conn.commit()
    finally:
        cur.close()
        conn.close()
