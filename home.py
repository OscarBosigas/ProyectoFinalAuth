import altair as alt
import pandas as pd
import streamlit as st
from datetime import datetime

def app():

    # Título y descripción
    st.title("Análisis de Valor Facturado por Medios de Pago (2023)")
    st.markdown("""
        Esta herramienta permite visualizar la evolución mensual del valor facturado 
        por diferentes medios de pago durante el año 2023, así como la distribución 
        de los valores facturados mediante un histograma interactivo.
    """)

    # Función para cargar los datos desde el archivo Excel
    @st.cache
    def get_data():
        # Cargar datos de Excel
        df = pd.read_excel('facturas_dataset_v2.xlsx')

        # Convertir la columna 'Fecha Emisión' a formato datetime
        df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'])

        # Filtrar solo los datos del año 2023
        df = df[df['Fecha Emisión'].dt.year == 2023]

        # Eliminar registros con errores lógicos
        df = df[~df['Medios De Pago'].isin(['Error logico', 'Error en datos'])]

        # Agrupar los datos por mes y sumar los valores facturados
        df['Mes'] = df['Fecha Emisión'].dt.to_period('M')  # Convertir a períodos mensuales
        df_grouped = df.groupby(['Mes', 'Medios De Pago'], as_index=False)['Valor Facturado'].sum()

        # Convertir de nuevo a timestamp para el gráfico
        df_grouped['Mes'] = df_grouped['Mes'].dt.to_timestamp()  

        return df_grouped

    # Obtener los datos
    data = get_data()

    # Filtros interactivos de selección
    st.sidebar.header("Filtros de Visualización")
    
    # Selector de medios de pago
    medios_pago = st.sidebar.multiselect(
        "Selecciona los medios de pago:",
        options=data['Medios De Pago'].unique(),
        default=data['Medios De Pago'].unique()
    )

    # Selector de fechas
    fecha_inicio, fecha_fin = st.sidebar.slider(
        "Selecciona el rango de fechas:",
        min_value=datetime(2023, 1, 1),
        max_value=datetime(2023, 12, 31),
        value=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
        format="YYYY-MM-DD"
    )

    # Filtrar los datos con base en los filtros seleccionados
    data_filtered = data[
        (data['Medios De Pago'].isin(medios_pago)) &
        (data['Mes'] >= pd.to_datetime(fecha_inicio)) &
        (data['Mes'] <= pd.to_datetime(fecha_fin))
    ]

    # Función para crear el gráfico de líneas
    def get_line_chart(data):
        hover = alt.selection_single(
            fields=["Mes"],
            nearest=True,
            on="mouseover",
            empty="none",
        )

        lines = (
            alt.Chart(data, height=500, title="Valor Facturado por Medios de Pago (2023)")
            .mark_line()
            .encode(
                x=alt.X("Mes:T", title="Fecha de Emisión"),
                y=alt.Y("Valor Facturado:Q", title="Valor Facturado"),
                color="Medios De Pago:N",
            )
        )

        # Dibujar puntos en la línea, y resaltar según la selección
        points = lines.transform_filter(hover).mark_circle(size=65)

        # Dibujar una regla en la ubicación de la selección
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="yearmonthdate(Mes)",
                y="Valor Facturado",
                opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                tooltip=[
                    alt.Tooltip("Mes:T", title="Fecha"),
                    alt.Tooltip("Valor Facturado:Q", title="Valor Facturado"),
                    alt.Tooltip("Medios De Pago:N", title="Medios de Pago"),
                ],
            )
            .add_selection(hover)
        )

        return (lines + points + tooltips).interactive()

    # Crear gráfico de área apilada
    def get_area_chart(data):
        area = (
            alt.Chart(data, height=400, title="Distribución del Valor Facturado por Medios de Pago (2023)")
            .mark_area(opacity=0.5, interpolate='basis')
            .encode(
                x=alt.X("Mes:T", title="Fecha de Emisión"),
                y=alt.Y("Valor Facturado:Q", stack='zero', title="Valor Facturado"),
                color="Medios De Pago:N",
                tooltip=["Mes:T", "Valor Facturado:Q", "Medios De Pago:N"]
            )
        )
        return area

    # Crear histograma
    def get_histogram(data):
        histogram = (
            alt.Chart(data, height=400, title="Distribución de los Valores Facturados (2023)")
            .mark_bar()
            .encode(
                alt.X("Valor Facturado:Q", bin=alt.Bin(maxbins=20), title="Valor Facturado (Binned)"),
                y="count():Q",
                color="Medios De Pago:N",
                tooltip=["count():Q", "Medios De Pago:N"]
            )
        )
        return histogram

    # Mostrar ambos gráficos
    line_chart = get_line_chart(data_filtered)
    area_chart = get_area_chart(data_filtered)
    histogram = get_histogram(data_filtered)

    # Mostrar el gráfico de líneas
    st.altair_chart(line_chart, use_container_width=True)

    # Mostrar el gráfico de área apilada
    st.altair_chart(area_chart, use_container_width=True)

    # Mostrar el histograma
    st.altair_chart(histogram, use_container_width=True)

    # Muestra una métrica del valor facturado total
    total_facturado = data_filtered['Valor Facturado'].sum()
    st.sidebar.subheader(f"Valor Facturado Total: ${total_facturado:,.2f}")

    # Información adicional
    st.markdown("""
        El histograma muestra la distribución de los valores facturados en diferentes 
        rangos de cantidades. Esto es útil para identificar los rangos más comunes de 
        facturación y ver en qué segmentos se concentran más los valores facturados.
    """)

