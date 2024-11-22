import streamlit as st

def show_landing():
    # Simple Hero Section
    st.title("Personal Finance Manager")
    st.write("Track, analyze, and optimize your spending with our intuitive personal finance app.")
    
    # Simple CTA Button
    st.button("Get Started", key="cta_button")
    
    # Simple Feature Section
    st.markdown("---")
    st.subheader("Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Smart Analytics")
        st.write("Visualize your spending patterns")
        
    with col2:
        st.markdown("### 🎯 Budget Tracking")
        st.write("Set and monitor budgets")
        
    with col3:
        st.markdown("### 🔄 Real-time Sync")
        st.write("Auto-sync transactions")
