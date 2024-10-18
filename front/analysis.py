import altair as alt
import pandas as pd
import streamlit as st

def app():
    # Función para cargar y preparar los datos
    def get_data():
        # Cargar el archivo Excel
        df = pd.read_excel('facturas_dataset_v2.xlsx')
        
        # Convertir la columna de Fecha Emisión a formato datetime
        df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'])  
        
        # Filtrar los datos del año 2023
        df = df[df['Fecha Emisión'].dt.year == 2023]  
        
        # Eliminar registros con errores lógicos en la columna Medios De Pago
        df = df[~df['Medios De Pago'].isin(['Error logico', 'Error en datos'])]  
        
        # Agrupar por mes y sumar los valores facturados
        df['Mes'] = df['Fecha Emisión'].dt.to_period('M')  # Convertir las fechas a períodos mensuales
        df_grouped = df.groupby(['Mes', 'Medios De Pago'], as_index=False)['Valor Facturado'].sum()
        
        # Convertir el período de nuevo a timestamps para trabajar con Altair
        df_grouped['Mes'] = df_grouped['Mes'].dt.to_timestamp()  
        
        return df_grouped

    # Función para generar el gráfico de Altair
    def get_chart(data):
        # Crear el gráfico de líneas
        lines = (
            alt.Chart(data, height=500, title="Valor Facturado por Medios de Pago (2023)")
            .mark_line()
            .encode(
                x=alt.X("Mes:T", title="Fecha de Emisión",
                        axis=alt.Axis(format='%b %Y', labelAngle=-45),  # Mostrar solo mes y año, etiquetas inclinadas
                        scale=alt.Scale(domain=[data['Mes'].min(), data['Mes'].max()], padding=20)),  # Ajustar escala y agregar padding
                y=alt.Y("Valor Facturado:Q", title="Valor Facturado",
                        scale=alt.Scale(zero=False)),  # Ajuste dinámico de la escala
                color=alt.Color("Medios De Pago:N", title="Medios de Pago", 
                                scale=alt.Scale(scheme="category20")),  # Usar una paleta de colores distintivos
            )
        )

        # Agregar tooltips para mostrar los detalles al pasar el cursor
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="yearmonthdate(Mes)",
                y="Valor Facturado",
                tooltip=[  # Mostrar información al hacer hover
                    alt.Tooltip("Mes:T", title="Fecha"),
                    alt.Tooltip("Valor Facturado:Q", title="Valor Facturado"),
                    alt.Tooltip("Medios De Pago:N", title="Medios de Pago"),
                ],
            )
        )

        return lines + tooltips  # Combinar el gráfico de líneas con los tooltips

    # Cargar los datos y generar el gráfico
    source = get_data()
    chart = get_chart(source)

    # Mostrar el gráfico en Streamlit
    st.altair_chart(chart.interactive(), use_container_width=True)

