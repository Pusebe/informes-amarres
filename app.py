import streamlit as st
import pandas as pd
import json
from collections import defaultdict

# 1. Título e instrucciones de la página
st.title("⚓ Calculadora de Ocupación de Amarres")
st.write("Sube el informe de estancias descargado del sistema para calcular la ocupación por tamaño de pantalán.")

# 2. Cargar la "base de datos" de tamaños (asumimos que amarres.json está en la misma carpeta)
@st.cache_data # Esto hace que la app vaya más rápido y no lea el json cada vez
def cargar_tamanos():
    try:
        with open('amarres.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Falta el archivo de configuración de amarres.")
        return {}

tamanos_amarres = cargar_tamanos()

# 3. El botón mágico donde el usuario sube su archivo
archivo_subido = st.file_uploader("Sube tu archivo CSV o Excel aquí", type=["csv", "xlsx"])

# 4. Procesamiento si el usuario ha subido algo
if archivo_subido is not None:
    try:
        # Leemos el archivo (teniendo en cuenta las 2 filas de cabecera que vimos)
        if archivo_subido.name.endswith('.csv'):
            df = pd.read_csv(archivo_subido, skiprows=2)
        else:
            df = pd.read_excel(archivo_subido, skiprows=2)

        ocupacion_por_eslora = defaultdict(int)

        # La misma lógica que ya teníamos
        for index, fila in df.iterrows():
            amarre = str(fila['Amarre']).strip()
            # Ajustamos el nombre de la columna según lo que vimos en tu CSV
            columna_dias = 'Días Estancias.2' if 'Días Estancias.2' in df.columns else 'Días Estancias'
            
            if pd.notna(amarre) and pd.notna(fila.get(columna_dias)):
                dias_ocupados = int(fila[columna_dias])
                if amarre in tamanos_amarres:
                    eslora_pantalan = tamanos_amarres[amarre]
                    ocupacion_por_eslora[eslora_pantalan] += dias_ocupados

        # 5. Mostrar los resultados de forma visual y bonita
        st.subheader("📊 Resumen de Ocupación")
        
        # Preparamos los datos para mostrarlos en una tabla limpia
        datos_tabla = [{"Tamaño Pantalán (m)": f"{eslora} m", "Días Ocupados": dias} 
                       for eslora, dias in sorted(ocupacion_por_eslora.items())]
        
        st.dataframe(datos_tabla, use_container_width=True)

        # ¡Incluso podemos añadir un gráfico de barras con una línea de código!
        st.bar_chart(pd.DataFrame(datos_tabla).set_index("Tamaño Pantalán (m)"))

    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo. Asegúrate de que es el formato correcto. Detalle: {e}")