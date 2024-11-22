import streamlit as st

def show_landing():
    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="gradient-text">Manage Your Finances with Confidence</h1>', unsafe_allow_html=True)
    st.markdown("""
        <p style='font-size: 1.2em; color: #ffffff; text-align: center; margin-bottom: 2rem;'>
            Take control of your financial future with our powerful personal finance management tools
        </p>
    """, unsafe_allow_html=True)
    
    # CTA Button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.button("Get Started", use_container_width=True, key="cta_button")
    
    # Feature Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='feature-card'>
                <h3 style='text-align: center; color: #4ECDC4;'>📊 Smart Analytics</h3>
                <p style='text-align: center;'>
                    Visualize your spending patterns and make informed financial decisions
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class='feature-card'>
                <h3 style='text-align: center; color: #4ECDC4;'>🎯 Budget Tracking</h3>
                <p style='text-align: center;'>
                    Set and monitor budgets to reach your financial goals faster
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class='feature-card'>
                <h3 style='text-align: center; color: #4ECDC4;'>🔄 Real-time Sync</h3>
                <p style='text-align: center;'>
                    Automatically sync and categorize your transactions
                </p>
            </div>
        """, unsafe_allow_html=True)
