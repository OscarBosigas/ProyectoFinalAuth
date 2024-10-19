import altair as alt
import pandas as pd
import streamlit as st

def app():

    # Función para cargar los datos desde el archivo Excel
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

    # Función para crear el gráfico
    def get_chart(data):
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

    # Obtener los datos y generar el gráfico
    source = get_data()
    chart = get_chart(source)

    # Mostrar el gráfico en Streamlit
    st.altair_chart(chart.interactive(), use_container_width=True)
