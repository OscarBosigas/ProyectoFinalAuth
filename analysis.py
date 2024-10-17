import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

def app():

    def get_data():
        source = data.stocks()
        source = source[source.date.gt("2004-01-01")]
        return source

    def get_chart(data):
        hover = alt.selection_single(
            fields=["date"],
            nearest=True,
            on="mouseover",
            empty="none",
        )

        lines = (
            alt.Chart(data, height=500, title="Gastos")
            .mark_line()
            .encode(
                x=alt.X("date", title="Fechas"),
                y=alt.Y("price", title="Peecio"),
                color="symbol",
            )
        )

        # Draw points on the line, and highlight based on selection
        points = lines.transform_filter(hover).mark_circle(size=65)

        # Draw a rule at the location of the selection
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="yearmonthdate(date)",
                y="price",
                opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                tooltip=[
                    alt.Tooltip("date", title="Fecha"),
                    alt.Tooltip("price", title="Valor"),
                ],
            )
            .add_selection(hover)
        )

        return (lines + points + tooltips).interactive()


    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.text_input("Choose a ticker (⬇💬👇ℹ️ ...)", value="⬇")
    with col2:
        ticker_dx = st.slider(
            "Horizontal offset", min_value=-30, max_value=30, step=1, value=0
        )
    with col3:
        ticker_dy = st.slider(
            "Vertical offset", min_value=-30, max_value=30, step=1, value=-10
        )

    # Original time series chart. Omitted `get_chart` for clarity
    source = get_data()
    chart = get_chart(source)

    # Input annotations
    ANNOTATIONS = [
        ("Mar 01, 2008", "Pretty good day for GOOG"),
        ("Dec 01, 2007", "Something's going wrong for GOOG & AAPL"),
        ("Nov 01, 2008", "Market starts again thanks to..."),
        ("Dec 01, 2009", "Small crash for GOOG after..."),
    ]

    # Create a chart with annotations
    annotations_df = pd.DataFrame(ANNOTATIONS, columns=["date", "event"])
    annotations_df.date = pd.to_datetime(annotations_df.date)
    annotations_df["y"] = 0
    annotation_layer = (
        alt.Chart(annotations_df)
        .mark_text(size=15, text=ticker, dx=ticker_dx, dy=ticker_dy, align="center")
        .encode(
            x="date:T",
            y=alt.Y("y:Q"),
            tooltip=["event"],
        )
        .interactive()
    )

    # Display both charts together
    st.altair_chart((chart + annotation_layer).interactive(), use_container_width=True)