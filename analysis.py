import pandas as pd
import streamlit as st
import altair as alt

def app():
    # Cargar los datos (ajusta la ruta según sea necesario)
    df = pd.read_excel('facturas_dataset_v2.xlsx')

    # Procesar y preparar los datos
    df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'], errors='coerce')
    df = df[df['Fecha Emisión'].dt.year == 2023]
    df = df[~df['Medios De Pago'].isin(['Error logico', 'Error en datos'])]

    # Asegúrate de que la columna Predicción exista y no tenga NaN
    if 'Prediccion' not in df.columns:
        st.error("La columna 'Prediccion' no existe en el DataFrame.")
        return
    
    df['Prediccion'] = df['Prediccion'].fillna('Sin Predicción')  # Reemplaza NaN con 'Sin Predicción'

    # Crear una columna de Mes
    df['Mes'] = df['Fecha Emisión'].dt.to_period('M')

    # Gráfico de Barras Mejorado
    # Agrupar los datos por Predicción y sumar los valores facturados
    df_grouped_bars = df.groupby('Prediccion').agg({'Valor Facturado': 'sum'}).reset_index()

    # Crear el gráfico de barras mejorado
    bar_chart = alt.Chart(df_grouped_bars).mark_bar().encode(
        x=alt.X('Prediccion:N', title='Predicción', sort='-y'),  # Ordenar de mayor a menor
        y=alt.Y('Valor Facturado:Q', title='Valor Facturado'),
        color=alt.Color('Prediccion:N', title='Categoría', scale=alt.Scale(scheme='tableau10')),  # Esquema de color
        tooltip=['Prediccion', alt.Tooltip('Valor Facturado:Q', format=',.2f')]  # Formato de tooltip
    )

    # Añadir etiquetas de valor en las barras
    bar_labels = bar_chart.mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Desplazamiento hacia arriba para colocar encima de la barra
        fontSize=12
    ).encode(
        text=alt.Text('Valor Facturado:Q', format=',.2f')
    )

    # Combinar gráfico de barras y etiquetas, y luego configurar
    bar_chart_combined = (bar_chart + bar_labels).properties(
        title='Valor Facturado por Categoría de Predicción',
        height=400,
        width=600
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )

    # Mostrar el gráfico de barras mejorado en Streamlit
    st.subheader("Valor Facturado por Categoría de Predicción (Mejorado)")
    st.altair_chart(bar_chart_combined, use_container_width=True)
    
    df_grouped_lines = df.groupby(['Mes', 'Prediccion']).agg({'Valor Facturado': 'sum'}).reset_index()

# Mejorar el gráfico de líneas con puntos y colores atractivos
    line_chart = alt.Chart(df_grouped_lines).mark_line(point=True, size=2).encode(
        x=alt.X('Mes:T', title='Mes'),
        y=alt.Y('Valor Facturado:Q', title='Valor Facturado', scale=alt.Scale(zero=False)),
        color=alt.Color('Prediccion:N', title='Predicción', scale=alt.Scale(scheme='tableau10')),
        tooltip=[
            alt.Tooltip('Mes:T', title='Mes'),
            alt.Tooltip('Prediccion:N', title='Predicción'),
            alt.Tooltip('Valor Facturado:Q', title='Valor Facturado', format=',')
        ]
    ).properties(
        title='Valor Facturado por Mes y Categoría de Predicción',
        height=400,
        width=600
    )

    st.subheader("Valor Facturado por Mes y Categoría de Predicción")
    st.altair_chart(line_chart, use_container_width=True)
