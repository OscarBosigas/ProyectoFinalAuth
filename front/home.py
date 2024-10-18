import pandas as pd
import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts

def app():
    # Función para cargar los datos y preparar el conteo de facturas emitidas por mes
    def get_data():
        df = pd.read_excel('facturas_dataset_v2.xlsx')
        df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'])  # Convertir a formato datetime
        df = df[df['Fecha Emisión'].dt.year == 2023]  # Filtrar por el año 2023
        
        # Eliminar registros con errores lógicos
        df = df[~df['Medios De Pago'].isin(['Error logico', 'Error en datos'])]
        
        # Agrupar los datos por mes y contar el número de facturas emitidas
        df['Mes'] = df['Fecha Emisión'].dt.to_period('M')
        df_grouped = df.groupby(['Mes'], as_index=False)['Valor Facturado'].count()  # Contar facturas emitidas
        df_grouped = df_grouped.rename(columns={"Valor Facturado": "Facturas Emitidas"})
        df_grouped['Mes'] = df_grouped['Mes'].dt.to_timestamp()  # Convertir de nuevo a timestamp
        
        # Convertir el DataFrame en el formato adecuado para Lightweight Charts
        facturas_data = [
            {"time": row['Mes'].strftime('%Y-%m-%d'), "value": row['Facturas Emitidas']}
            for _, row in df_grouped.iterrows()
        ]
        
        return facturas_data

    # Obtener los datos preparados
    facturas_data = get_data()

    # Configuración del gráfico en Lightweight Charts
    chartOptions = {
        "height": 400,
        "rightPriceScale": {
            "scaleMargins": {
                "top": 0.2,
                "bottom": 0.25,
            },
            "borderVisible": False,
        },
        "layout": {
            "background": {
                "type": 'solid',
                "color": '#131722'
            },
            "textColor": '#d1d4dc',
        },
        "grid": {
            "vertLines": {
                "color": 'rgba(42, 46, 57, 0)',
            },
            "horzLines": {
                "color": 'rgba(42, 46, 57, 0.6)',
            }
        }
    }

    # Configuración de la serie del gráfico con sombreado (Área)
    seriesOptions = [
        {
            "type": 'Area',  # Cambiar de 'Line' a 'Area' para incluir sombreado
            "data": facturas_data,  # Datos preparados
            "options": {
                "topColor": 'rgba(38,198,218, 0.56)',  # Color en la parte superior del área
                "bottomColor": 'rgba(38,198,218, 0.04)',  # Color en la parte inferior del área
                "lineColor": 'rgba(38,198,218, 1)',  # Color de la línea principal
                "lineWidth": 2,  # Ancho de la línea
            }
        }
    ]

    # Renderizar el gráfico en Streamlit
    st.subheader("Número de Facturas Emitidas por Mes (2023)")
    renderLightweightCharts([{
        "chart": chartOptions,
        "series": seriesOptions
    }], 'facturas_emitidas')