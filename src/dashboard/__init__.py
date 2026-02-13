"""
Dashboard module for Streamlit visualization.

BRANCH-7: Dashboard
"""

from .wordcloud_generator import MedicalWordCloudGenerator, StreamlitWordCloudDashboard
from .components import (
    setup_sidebar,
    display_metrics,
    metric_card,
    data_quality_card,
    entity_frequency_chart,
    product_table,
    timeline_chart,
    status_indicator,
)

__all__ = [
    "MedicalWordCloudGenerator",
    "StreamlitWordCloudDashboard",
    "setup_sidebar",
    "display_metrics",
    "metric_card",
    "data_quality_card",
    "entity_frequency_chart",
    "product_table",
    "timeline_chart",
    "status_indicator",
]