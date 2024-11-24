import streamlit as st

def show_landing():
    try:
        # Container for better organization
        with st.container():
            st.write("")  # Add some spacing
            # Hero Section with custom styling
            st.markdown('<div class="hero-section">', unsafe_allow_html=True)
            st.markdown('<h1 class="gradient-text">Take Control of Your Finances</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle-text">Track, analyze, and optimize your spending with our intuitive personal finance app.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add some spacing
            st.write("")
            st.write("")
            
            # Feature Section
            st.markdown('<div class="features-section">', unsafe_allow_html=True)
            st.header("Key Features")
            
            # Create three columns for features
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown("### 📊 Smart Analytics")
                st.markdown("""
                Advanced visualization of your spending patterns with interactive charts and reports.
                """)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown("### 🎯 Budget Tracking")
                st.markdown("""
                Set custom budgets and get real-time insights on your spending habits.
                """)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col3:
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown("### 🔄 Real-time Sync")
                st.markdown("""
                Automatically sync your transactions and keep your finances up to date.
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add spacing before CTA
            st.write("")
            st.write("")
            
            # CTA Button with prominent styling
            if st.button("Get Started", key="cta_button", type="primary", use_container_width=True):
                st.session_state.cta_button = True
                return True
                
    except Exception as e:
        st.error(f"Error displaying landing page: {str(e)}")
        return False
    
    return True
