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
        de los valores facturados.
    """)

    # Cargar y preparar los datos
    def get_data():
        # Cargar datos de Excel
        df = pd.read_excel('facturas_dataset_v2.xlsx')

        # Convertir la columna 'Fecha Emisión' a formato datetime
        df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'])

        # Filtrar solo los datos del año 2023
        df = df[df['Fecha Emisión'].dt.year == 2023]

        # Eliminar registros con errores lógicos
        df = df[~df['Medios De Pago'].isin(['Error logico', 'Error en datos'])]

        # Crear una columna de mes y calcular la frecuencia
        df['Mes'] = df['Fecha Emisión'].dt.to_period('M')
        df_grouped = df.groupby(['Mes', 'Medios De Pago'], as_index=False).agg({
            'Valor Facturado': 'sum',
            'Fecha Emisión': 'count'  # Cuenta la frecuencia de transacciones
        })

        df_grouped = df_grouped.rename(columns={'Fecha Emisión': 'Frecuencia'})
        df_grouped['Mes'] = df_grouped['Mes'].dt.to_timestamp()  # Convertir a timestamp

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

    # Gráfico de burbujas (Bubble Chart)
    def get_bubble_chart(data):
        # Asegúrate de que cada gráfico de burbujas tenga un nombre único para el hover
        hover_bubble = alt.selection_single(
            name="hover_bubble",  # Renombrado para evitar duplicados
            fields=["Mes"],
            nearest=True,
            on="mouseover",
            empty="none",
        )

        bubble_chart = (
            alt.Chart(data, title="Frecuencia de Uso y Valor Facturado por Medios de Pago (2023)")
            .mark_circle()
            .encode(
                x=alt.X("Mes:T", title="Mes"),
                y=alt.Y("Frecuencia:Q", title="Frecuencia de Transacciones"),
                size=alt.Size("Valor Facturado:Q", title="Valor Facturado", scale=alt.Scale(range=[100, 1000])),
                color=alt.Color("Medios De Pago:N", title="Medio de Pago"),
                tooltip=[
                    alt.Tooltip("Mes:T", title="Mes"),
                    alt.Tooltip("Medios De Pago:N", title="Medio de Pago"),
                    alt.Tooltip("Frecuencia:Q", title="Frecuencia"),
                    alt.Tooltip("Valor Facturado:Q", title="Valor Facturado", format=",.2f")
                ]
            )
            .add_selection(hover_bubble)  # Añadir selección para hover
            .interactive()
        )
        return bubble_chart

    # Mostrar el gráfico de burbujas
    bubble_chart = get_bubble_chart(data_filtered)
    st.altair_chart(bubble_chart, use_container_width=True)

    # Gráfico de líneas
    def get_line_chart(data):
        # Renombramos la selección 'hover' para que tenga un nombre único
        hover_line = alt.selection_single(
            name="hover_line",  # Nombre único para la selección en el gráfico de líneas
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

        # Dibujar puntos en la línea y resaltar según la selección
        points = lines.transform_filter(hover_line).mark_circle(size=65)

        # Dibujar una regla en la ubicación de la selección
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="yearmonthdate(Mes)",
                y="Valor Facturado",
                opacity=alt.condition(hover_line, alt.value(0.3), alt.value(0)),
                tooltip=[
                    alt.Tooltip("Mes:T", title="Fecha"),
                    alt.Tooltip("Valor Facturado:Q", title="Valor Facturado"),
                    alt.Tooltip("Medios De Pago:N", title="Medios de Pago"),
                ],
            )
            .add_selection(hover_line)
        )

        return (lines + points + tooltips).interactive()

    # Mostrar el gráfico de líneas
    line_chart = get_line_chart(data_filtered)
    st.altair_chart(line_chart, use_container_width=True)

    # Muestra una métrica del valor facturado total
    total_facturado = data_filtered['Valor Facturado'].sum()
    st.sidebar.subheader(f"Valor Facturado Total: ${total_facturado:,.2f}")
