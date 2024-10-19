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

    # Gráfico de Barras
    # Agrupar los datos por Predicción y sumar los valores facturados
    df_grouped_bars = df.groupby('Prediccion').agg({'Valor Facturado': 'sum'}).reset_index()

    # Crear el gráfico de barras
    bar_chart = alt.Chart(df_grouped_bars).mark_bar().encode(
        x=alt.X('Prediccion:N', title='Predicción', sort=None),  # Ordenar sin orden específico
        y=alt.Y('Valor Facturado:Q', title='Valor Facturado'),
        color=alt.Color('Prediccion:N', title='Categoría'),
        tooltip=['Prediccion', 'Valor Facturado']  # Mostrar información al pasar el cursor
    ).properties(
        title='Valor Facturado por Categoría de Predicción',
        height=400,
        width=600
    )

    # Gráfico de Líneas
    # Agrupar los datos por Mes y Predicción
    df_grouped_lines = df.groupby(['Mes', 'Prediccion']).agg({'Valor Facturado': 'sum'}).reset_index()

    # Crear el gráfico de líneas
    line_chart = alt.Chart(df_grouped_lines).mark_line().encode(
        x=alt.X('Mes:T', title='Mes'),
        y=alt.Y('Valor Facturado:Q', title='Valor Facturado'),
        color=alt.Color('Prediccion:N', title='Predicción'),
        tooltip=['Mes', 'Prediccion', 'Valor Facturado']
    ).properties(
        title='Valor Facturado por Mes y Categoría de Predicción',
        height=400,
        width=600
    )

    # Mostrar los gráficos en Streamlit
    st.subheader("Valor Facturado por Categoría de Predicción")
    st.altair_chart(bar_chart, use_container_width=True)

    st.subheader("Valor Facturado por Mes y Categoría de Predicción")
    st.altair_chart(line_chart, use_container_width=True)
