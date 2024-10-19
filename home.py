import pandas as pd
import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts

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

    # Función para crear los datos de las series para el gráfico de área
    def prepare_series_data(data):
        # Definir un diccionario de colores para cada medio de pago
        color_map = {
            'Tarjeta de Crédito': 'rgba(255, 192, 0, 1)',
            'Transferencia Bancaria': 'rgba(67, 83, 254, 1)',
            'Efectivo': 'rgba(0, 255, 0, 1)',
            'Otros': 'rgba(255, 0, 0, 1)'
            # Añade más medios de pago y colores según sea necesario
        }
        
        series_data = []
        for medio_pago in data['Medios De Pago'].unique():
            medio_pago_data = data[data['Medios De Pago'] == medio_pago]
            series_data.append({
                "type": 'Area',
                "data": [{"time": row['Mes'].strftime('%Y-%m-%d'), "value": row['Valor Facturado']} for _, row in medio_pago_data.iterrows()],
                "options": {
                    "topColor": color_map.get(medio_pago, 'rgba(255, 255, 255, 0.7)'),  # Color por defecto blanco semi-transparente
                    "bottomColor": color_map.get(medio_pago, 'rgba(255, 255, 255, 0.3)'),
                    "lineColor": color_map.get(medio_pago, 'rgba(255, 255, 255, 1)'),
                    "lineWidth": 2,
                },
                "markers": []  # Sin marcadores
            })
        return series_data

    # Configuración del gráfico de área
    overlaidAreaSeriesOptions = {
        "height": 400,
        "rightPriceScale": {
            "scaleMargins": {
                "top": 0.1,
                "bottom": 0.1,
            },
            "mode": 0,
            "borderColor": 'rgba(197, 203, 206, 0.4)',
        },
        "timeScale": {
            "borderColor": 'rgba(197, 203, 206, 0.4)',
        },
        "layout": {
            "background": {
                "type": 'solid',
                "color": '#100841'
            },
            "textColor": '#ffffff',
        },
        "grid": {
            "vertLines": {
                "color": 'rgba(197, 203, 206, 0.4)',
                "style": 1,
            },
            "horzLines": {
                "color": 'rgba(197, 203, 206, 0.4)',
                "style": 1,
            }
        }
    }

    # Obtener los datos y generar el gráfico
    source = get_data()
    series_data = prepare_series_data(source)  # Preparar datos para la gráfica

    # Mostrar el gráfico en Streamlit
    renderLightweightCharts([
        {
            "chart": overlaidAreaSeriesOptions,
            "series": series_data
        }
    ], 'facturacion_por_medios_de_pago')

# Ejecutar la aplicación
if __name__ == "__main__":
    app()
