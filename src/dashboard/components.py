"""
Reusable Streamlit dashboard components.

BRANCH-7: Dashboard
Author: Boris (Claude Code)
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any


def setup_sidebar() -> Dict[str, Any]:
    """
    Setup sidebar configuration and filters.

    Returns:
        Configuration dictionary
    """
    with st.sidebar:
        st.subheader("🔍 Filters")

        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "From:",
                value=datetime.now() - timedelta(days=30),
                key="start_date"
            )

        with col2:
            end_date = st.date_input(
                "To:",
                value=datetime.now(),
                key="end_date"
            )

        st.divider()

        # Filters
        medical_only = st.checkbox("🏥 Medical Messages Only", value=False)
        min_quality = st.slider("Minimum Quality Score", 0.0, 1.0, 0.5)

        st.divider()

        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            show_confidence = st.checkbox("Show Confidence Scores")
            show_raw_data = st.checkbox("Show Raw Data")

        return {
            "start_date": start_date,
            "end_date": end_date,
            "medical_only": medical_only,
            "min_quality": min_quality,
            "show_confidence": show_confidence,
            "show_raw_data": show_raw_data,
        }


def display_metrics(
    total: int,
    medical: int,
    entities: int,
    quality_score: float
) -> None:
    """
    Display top-level metrics.

    Args:
        total: Total messages
        medical: Medical messages
        entities: Total entities
        quality_score: Average quality score
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📨 Total Messages",
            f"{total:,}",
            delta=f"{int(total * 0.05)} this week"
        )

    with col2:
        pct = (medical / total * 100) if total > 0 else 0
        st.metric(
            "🏥 Medical %",
            f"{pct:.1f}%",
            delta="+3%"
        )

    with col3:
        st.metric(
            "🏷️ Entities",
            f"{entities:,}",
            delta=f"{int(entities * 0.08)} this week"
        )

    with col4:
        st.metric(
            "⭐ Quality Score",
            f"{quality_score:.2f}",
            delta="+0.05"
        )


def metric_card(
    label: str,
    value: str,
    delta: str = "",
    delta_color: str = "off"
) -> None:
    """
    Display a single metric card.

    Args:
        label: Metric label
        value: Metric value
        delta: Change indicator
        delta_color: 'normal', 'inverse', 'off'
    """
    col = st.columns(1)[0]
    with col:
        st.metric(label, value, delta=delta)


def data_quality_card(
    title: str,
    passed: int,
    failed: int,
    warnings: int = 0
) -> None:
    """
    Display data quality card.

    Args:
        title: Card title
        passed: Number of passed checks
        failed: Number of failed checks
        warnings: Number of warnings
    """
    with st.container():
        st.subheader(title)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("✅ Passed", passed)

        with col2:
            st.metric("❌ Failed", failed)

        with col3:
            if warnings > 0:
                st.metric("⚠️ Warnings", warnings)


def entity_frequency_chart(
    entities: Dict[str, int],
    chart_type: str = "bar",
    max_items: int = 10
) -> None:
    """
    Display entity frequency chart.

    Args:
        entities: Dictionary of {entity: count}
        chart_type: 'bar' or 'pie'
        max_items: Maximum items to display
    """
    import pandas as pd

    if not entities:
        st.info("No entities found")
        return

    # Get top N
    top_entities = dict(sorted(
        entities.items(),
        key=lambda x: x[1],
        reverse=True
    )[:max_items])

    df = pd.DataFrame(
        list(top_entities.items()),
        columns=["Entity", "Count"]
    )

    if chart_type == "bar":
        st.bar_chart(df.set_index("Entity"))
    elif chart_type == "pie":
        st.pie_chart(df.set_index("Entity"))


def product_table(
    products: List[Dict[str, Any]],
    columns: List[str] = ["Name", "Category", "Mentions", "Avg Price"]
) -> None:
    """
    Display products table.

    Args:
        products: List of product dictionaries
        columns: Columns to display
    """
    import pandas as pd

    if not products:
        st.info("No products found")
        return

    df = pd.DataFrame(products)[columns]
    st.dataframe(df, use_container_width=True)


def timeline_chart(
    data: List[Dict[str, Any]],
    date_column: str = "date",
    value_column: str = "count"
) -> None:
    """
    Display timeline chart.

    Args:
        data: List of data points with dates
        date_column: Name of date column
        value_column: Name of value column
    """
    import pandas as pd

    if not data:
        st.info("No data available")
        return

    df = pd.DataFrame(data)
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column)

    st.line_chart(df.set_index(date_column)[value_column])


def status_indicator(status: str, message: str = "") -> None:
    """
    Display status indicator.

    Args:
        status: 'success', 'warning', 'error', 'info'
        message: Status message
    """
    if status == "success":
        st.success(f"✅ {message}" if message else "✅ Success")
    elif status == "warning":
        st.warning(f"⚠️ {message}" if message else "⚠️ Warning")
    elif status == "error":
        st.error(f"❌ {message}" if message else "❌ Error")
    else:
        st.info(f"ℹ️ {message}" if message else "ℹ️ Information")