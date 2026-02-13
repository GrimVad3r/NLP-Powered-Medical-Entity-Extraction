"""
Visualization utilities for Streamlit dashboard.

BRANCH-7: Dashboard
Author: Boris (Claude Code)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional

from ..core.logger import get_logger

logger = get_logger(__name__)


def plot_bar_chart(
    data: Dict[str, int],
    title: str,
    x_label: str = "Category",
    y_label: str = "Count",
    use_plotly: bool = True
) -> None:
    """
    Plot bar chart.

    Args:
        data: Dictionary of {category: value}
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not data:
        st.warning("No data to display")
        return

    df = pd.DataFrame(list(data.items()), columns=[x_label, y_label])

    if use_plotly:
        fig = px.bar(df, x=x_label, y=y_label, title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(df[x_label], df[y_label])
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        st.pyplot(fig)

    logger.debug(f"Plotted bar chart: {title}")


def plot_line_chart(
    data: List[float],
    title: str,
    labels: Optional[List[str]] = None,
    use_plotly: bool = True
) -> None:
    """
    Plot line chart.

    Args:
        data: List of values
        title: Chart title
        labels: Optional x-axis labels
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not data:
        st.warning("No data to display")
        return

    if use_plotly:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=data, mode='lines+markers', name='Values'))
        fig.update_layout(title=title, xaxis_title="Index", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data, marker='o')
        ax.set_title(title)
        ax.set_ylabel("Value")
        st.pyplot(fig)

    logger.debug(f"Plotted line chart: {title}")


def plot_pie_chart(
    data: Dict[str, int],
    title: str,
    use_plotly: bool = True
) -> None:
    """
    Plot pie chart.

    Args:
        data: Dictionary of {category: value}
        title: Chart title
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not data:
        st.warning("No data to display")
        return

    if use_plotly:
        fig = px.pie(values=list(data.values()), names=list(data.keys()), title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        ax.set_title(title)
        st.pyplot(fig)

    logger.debug(f"Plotted pie chart: {title}")


def plot_histogram(
    data: List[float],
    title: str,
    bins: int = 20,
    use_plotly: bool = True
) -> None:
    """
    Plot histogram.

    Args:
        data: List of values
        title: Chart title
        bins: Number of bins
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not data:
        st.warning("No data to display")
        return

    if use_plotly:
        fig = px.histogram(x=data, nbins=bins, title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data, bins=bins)
        ax.set_title(title)
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

    logger.debug(f"Plotted histogram: {title}")


def plot_scatter(
    x_data: List[float],
    y_data: List[float],
    title: str,
    x_label: str = "X",
    y_label: str = "Y",
    use_plotly: bool = True
) -> None:
    """
    Plot scatter chart.

    Args:
        x_data: X-axis data
        y_data: Y-axis data
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not x_data or not y_data or len(x_data) != len(y_data):
        st.warning("Invalid data for scatter plot")
        return

    if use_plotly:
        fig = px.scatter(x=x_data, y=y_data, title=title, labels={
            "x": x_label,
            "y": y_label,
        })
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x_data, y_data)
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        st.pyplot(fig)

    logger.debug(f"Plotted scatter chart: {title}")


def plot_heatmap(
    data: pd.DataFrame,
    title: str,
    use_plotly: bool = True
) -> None:
    """
    Plot heatmap.

    Args:
        data: DataFrame with numeric values
        title: Chart title
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if data.empty:
        st.warning("No data to display")
        return

    if use_plotly:
        fig = px.imshow(data, title=title, labels=dict(color="Value"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(data.values, cmap='viridis')
        ax.set_title(title)
        ax.set_xticks(range(len(data.columns)))
        ax.set_xticklabels(data.columns, rotation=45)
        ax.set_yticks(range(len(data.index)))
        ax.set_yticklabels(data.index)
        plt.colorbar(im)
        st.pyplot(fig)

    logger.debug(f"Plotted heatmap: {title}")


def plot_box(
    data: Dict[str, List[float]],
    title: str,
    use_plotly: bool = True
) -> None:
    """
    Plot box plot.

    Args:
        data: Dictionary of {category: values}
        title: Chart title
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not data:
        st.warning("No data to display")
        return

    if use_plotly:
        # Convert dict to long format for plotly
        records = []
        for category, values in data.items():
            for value in values:
                records.append({"Category": category, "Value": value})

        df = pd.DataFrame(records)
        fig = px.box(df, x="Category", y="Value", title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.boxplot([values for values in data.values()], labels=data.keys())
        ax.set_title(title)
        ax.set_ylabel("Value")
        st.pyplot(fig)

    logger.debug(f"Plotted box plot: {title}")


def plot_comparison_bars(
    data: Dict[str, Dict[str, float]],
    title: str,
    use_plotly: bool = True
) -> None:
    """
    Plot comparison bar chart (multiple categories).

    Args:
        data: Dictionary of {category: {subcategory: value}}
        title: Chart title
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not data:
        st.warning("No data to display")
        return

    if use_plotly:
        fig = go.Figure()

        for category, values in data.items():
            fig.add_trace(go.Bar(
                x=list(values.keys()),
                y=list(values.values()),
                name=category
            ))

        fig.update_layout(title=title, barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(12, 6))

        x_labels = list(list(data.values())[0].keys())
        x_pos = range(len(x_labels))
        width = 0.8 / len(data)

        for i, (category, values) in enumerate(data.items()):
            offset = (i - len(data) / 2 + 0.5) * width
            ax.bar([x + offset for x in x_pos], list(values.values()), width, label=category)

        ax.set_title(title)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.legend()
        st.pyplot(fig)

    logger.debug(f"Plotted comparison bars: {title}")


def plot_time_series(
    dates: List[str],
    values: List[float],
    title: str,
    y_label: str = "Value",
    use_plotly: bool = True
) -> None:
    """
    Plot time series chart.

    Args:
        dates: List of date strings
        values: List of values
        title: Chart title
        y_label: Y-axis label
        use_plotly: Use Plotly (True) or Matplotlib (False)
    """
    if not dates or not values or len(dates) != len(values):
        st.warning("Invalid data for time series")
        return

    if use_plotly:
        fig = px.line(x=dates, y=values, title=title, labels={"x": "Date", "y": y_label})
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, values, marker='o')
        ax.set_title(title)
        ax.set_xlabel("Date")
        ax.set_ylabel(y_label)
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

    logger.debug(f"Plotted time series: {title}")