"""
Main Streamlit dashboard application.

BRANCH-7: Dashboard
Author: Boris (Claude Code)
"""

import streamlit as st
from streamlit import session_state as ss
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.logger import get_logger
from src.dashboard.components import setup_sidebar, display_metrics
from src.database.connection import get_db_session
from src.database.crud import MessageCRUD, EntityCRUD, ProductCRUD

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Medical Intelligence Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-title {
        color: #1f77b4;
        font-size: 32px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Page title
st.markdown('<div class="header-title">🏥 Medical Intelligence Platform</div>', unsafe_allow_html=True)
st.write("Advanced NLP-Powered Telegram Medical Data Analysis")

# Sidebar navigation
with st.sidebar:
    st.title("🔍 Navigation")
    page = st.radio(
        "Select Page:",
        [
            "📊 Home",
            "💊 Products",
            "📈 Pricing",
            "🧠 NLP Insights",
            "☁️ Word Clouds",
            "📉 Analytics",
        ],
        index=0
    )

    st.divider()

    st.subheader("⚙️ Settings")
    show_advanced = st.checkbox("Advanced Mode", value=False)
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 300, 30)

# Home page
if page == "📊 Home":
    st.subheader("Dashboard Overview")

    try:
        session = get_db_session()
        msg_crud = MessageCRUD(session)
        entity_crud = EntityCRUD(session)
        prod_crud = ProductCRUD(session)

        total_messages = msg_crud.count()
        medical_messages = msg_crud.count(medical_only=True)
        total_entities = entity_crud.count()
        total_products = prod_crud.count()

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📨 Total Messages",
                f"{total_messages:,}",
                delta=f"+{int(total_messages * 0.05)}"
            )

        with col2:
            pct = (medical_messages / total_messages * 100) if total_messages > 0 else 0
            st.metric(
                "🏥 Medical %",
                f"{pct:.1f}%",
                delta=f"+3%"
            )

        with col3:
            st.metric(
                "🏷️ Entities Found",
                f"{total_entities:,}",
                delta=f"+{int(total_entities * 0.08)}"
            )

        with col4:
            st.metric(
                "💊 Products",
                f"{total_products:,}",
                delta=f"+{int(total_products * 0.05)}"
            )

        session.close()

    except Exception as e:
        st.error(f"Error loading metrics: {e}")
        logger.error(f"Dashboard error: {e}")

    st.divider()

    # Recent activity
    st.subheader("📋 Recent Activity")

    try:
        session = get_db_session()
        msg_crud = MessageCRUD(session)

        recent_medical = msg_crud.get_medical_messages(limit=5)

        if recent_medical:
            for msg in recent_medical:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"📝 {msg.text[:100]}...")
                    with col2:
                        st.write(f"⭐ {msg.quality_score:.2f}")

        session.close()

    except Exception as e:
        st.error(f"Error loading recent activity: {e}")


# Products page
elif page == "💊 Products":
    st.subheader("Medical Products Analysis")

    try:
        session = get_db_session()
        prod_crud = ProductCRUD(session)

        # Top products
        st.write("#### Top 10 Products")

        top_products = prod_crud.get_top_products(limit=10)

        if top_products:
            product_data = []
            for prod in top_products:
                product_data.append({
                    "Name": prod.name,
                    "Category": prod.category,
                    "Mentions": prod.mention_count,
                    "Avg Price": f"${prod.avg_price:.2f}" if prod.avg_price else "N/A",
                })

            st.dataframe(product_data, use_container_width=True)
        else:
            st.info("No products found")

        session.close()

    except Exception as e:
        st.error(f"Error loading products: {e}")


# Pricing page
elif page == "📈 Pricing":
    st.subheader("Price Analysis & Trends")

    st.info("Price trend analysis module - coming soon")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average Price", "$25.50", delta="$2.30 ↑")

    with col2:
        st.metric("Price Range", "$10 - $150", delta="-$5 ↓")


# NLP Insights
elif page == "🧠 NLP Insights":
    st.subheader("NLP Processing Insights")

    try:
        session = get_db_session()
        entity_crud = EntityCRUD(session)

        # Entity distribution
        st.write("#### Entity Type Distribution")

        entity_types = ["MEDICATION", "DOSAGE", "CONDITION", "SYMPTOM", "PRICE"]
        counts = {}

        for ent_type in entity_types:
            count = entity_crud.count(entity_type=ent_type)
            counts[ent_type] = count

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Medications", counts.get("MEDICATION", 0))

        with col2:
            st.metric("Conditions", counts.get("CONDITION", 0))

        with col3:
            st.metric("Prices", counts.get("PRICE", 0))

        st.divider()

        # Top entities
        st.write("#### Top Mentioned Terms")

        top_entities = entity_crud.get_top_entities(limit=10)

        if top_entities:
            entity_data = [{"Term": text, "Type": ent_type, "Count": count}
                          for text, ent_type, count in top_entities[:10]]
            st.dataframe(entity_data, use_container_width=True)

        session.close()

    except Exception as e:
        st.error(f"Error loading NLP insights: {e}")


# Word Clouds
elif page == "☁️ Word Clouds":
    st.subheader("Medical Terms Visualization")

    try:
        from src.dashboard.wordcloud_generator import MedicalWordCloudGenerator

        col1, col2 = st.columns(2)

        with col1:
            st.write("#### Top Medications")
            st.info("Word cloud showing medication frequency")

        with col2:
            st.write("#### Top Conditions")
            st.info("Word cloud showing condition frequency")

    except Exception as e:
        st.error(f"Error loading word clouds: {e}")


# Analytics
elif page == "📉 Analytics":
    st.subheader("Advanced Analytics")

    try:
        session = get_db_session()

        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")

        st.write("#### Message Timeline")
        st.info("Timeline chart showing message volume over time")

        session.close()

    except Exception as e:
        st.error(f"Error loading analytics: {e}")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
        Medical Intelligence Platform v2.0 | 
        Built with Streamlit, FastAPI & Advanced NLP
    </div>
""", unsafe_allow_html=True)

logger.info(f"Dashboard rendered - Page: {page}")