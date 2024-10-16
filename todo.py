import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Configuración y carga de datos
def cargar_datos(file_path):
    """
    Carga un archivo CSV en un DataFrame.
    """
    return pd.read_csv(file_path)

# Ruta del archivo
file_path = r"C:\Users\omarv\Desktop\Proyecto_Org\Org_Datos_Colombia.csv"
df = cargar_datos(file_path)

# Identificación de género
def determinar_genero(nombre, nombres_femeninos):
    """
    Determina el género basado en el primer nombre de una lista de nombres femeninos.
    """
    primer_nombre = nombre.split()[0].upper()
    return 'Femenino' if primer_nombre in nombres_femeninos else 'Masculino'

# Lista de nombres femeninos
nombres_femeninos = ['DANIELA', 'GLORIA', 'JULIETH', 'LILIANA', 'YINETH', 'YENNY', 
                     'LEIDY', 'YURLEY', 'DIVIANA', 'SAIDA', 'DEISY', 'JENNIFFER', 
                     'DEICY', 'NANCY', 'ANYELA', 'ERIKA', 'NORVY', 'CECILIA', 'ARACELY', 
                     'CARMEN', 'MIRIAM', 'YORLEY', 'LAURA', 'YANEIRA', 'LISBETH', 
                     'ALEXANDRA', 'DIANA', 'CLAUDIA', 'RUBY', 'LUCIA']

# Aplicar la función para identificar género
df['GENERO'] = df['NOMBRES Y APELLIDOS'].apply(lambda x: determinar_genero(x, nombres_femeninos))

# Asignar valores numéricos al género
df = df.assign(GENERO_NUMERICO=np.where(df['GENERO'] == 'Femenino', 0, 1))

# Función para convertir escala salarial
SMLV = 1_300_000
def convertir_smlv(escala, smlv=SMLV):
    """
    Convierte la escala salarial basada en el salario mínimo (SMLV).
    """
    try:
        escala = escala.strip().upper()
        if re.match(r'^\d+\s*-\s*SMLV$', escala):
            numero = re.search(r'\d+', escala)
            return int(numero.group(0)) * smlv if numero else None
        elif '-' in escala:
            numeros = re.findall(r'\d+', escala)
            if len(numeros) == 2:
                val_min, val_max = map(int, numeros)
                promedio = (val_min + val_max) / 2
                return promedio * smlv
        else:
            numero = re.search(r'\d+', escala)
            return int(numero.group(0)) * smlv if numero else None
    except Exception as e:
        print(f"Error procesando la escala: {escala} - {e}")
    return None

# Aplicar la conversión de escala salarial
df['SALARIO_CALCULADO'] = df['ESCALA SALARIAL SEGÚN LAS CATEGORÍAS PARRA SERVIDORES PÚBLICOS Y/O EMPREADOS DEL SECTOR PRIVADO.'].apply(lambda x: convertir_smlv(str(x)))

# Renombrar columnas
df = df.rename(columns={
    'ESCALA SALARIAL SEGÚN LAS CATEGORÍAS PARRA SERVIDORES PÚBLICOS Y/O EMPREADOS DEL SECTOR PRIVADO.': 'ESCALA_SALARIO',
    'GENERO_NUMERICO': 'GENERO_NUMERICO'
})

# Lista de niveles de educación en el orden deseado, combinando "TÉCNICO" y "TECNICO"
niveles_educacion = ['PRIMARIA', 'BACHILLER', 'MEDIA BOCACIONAL', 'TÉCNICO', 
                     'TECNOLOGO', 'PASANTE SENA', 'PASANTE UNIVERSITARIO', 'PROFESIONAL']

# Crear un diccionario que asigne valores del 1 al 8 a cada nivel (ya que "TÉCNICO" y "TECNICO" son el mismo)
educacion_dict = {nivel: valor for valor, nivel in enumerate(niveles_educacion, start=1)}

# Asegurarse de que tanto "TÉCNICO" como "TECNICO" reciban el mismo valor
educacion_dict['TECNICO'] = educacion_dict['TÉCNICO']

# Crear una nueva columna con el valor numérico correspondiente al nivel de educación
df['NIVEL EDUCACION ORDENADO'] = df['FORMACIÓN ACADEMICA'].map(educacion_dict)

# Filtrar columnas importantes
df = df[['NUMERO', 'NOMBRES Y APELLIDOS', 'GENERO', 'GENERO_NUMERICO', 'FORMACIÓN ACADEMICA', 'NIVEL EDUCACION ORDENADO', 'ESCALA_SALARIO', 'SALARIO_CALCULADO']]

# Análisis y agrupación de datos
def calcular_estadisticas_genero(df):
    """
    Calcula estadísticas (promedio) de salario agrupado por género.
    """
    return df.groupby('GENERO')['SALARIO_CALCULADO'].agg(promedio='mean').reset_index()

# Calcular las estadísticas de salario por género
estadisticas_genero = calcular_estadisticas_genero(df)

# Obtener los salarios promedio de hombres y mujeres
salario_promedio_mujeres = estadisticas_genero[estadisticas_genero['GENERO'] == 'Femenino']['promedio'].values[0]
salario_promedio_hombres = estadisticas_genero[estadisticas_genero['GENERO'] == 'Masculino']['promedio'].values[0]

# Calcular la diferencia absoluta y el porcentaje
diferencia_salario = salario_promedio_hombres - salario_promedio_mujeres
diferencia_porcentual = (diferencia_salario / salario_promedio_mujeres) * 100

###############################################################################################################################################

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Suponiendo que ya tienes calculados los siguientes valores:
# salario_promedio_mujeres, salario_promedio_hombres, diferencia_salario, diferencia_porcentual, df, promedio_total, df_filtered

# Mostrar resultados de salario promedio
st.markdown("<h1 style='text-align: center;'>Resultados de Colombia:</h1>", unsafe_allow_html=True)
st.header("Estadísiscas de Colombia:")
st.metric("Salario promedio de mujeres", f"{salario_promedio_mujeres:.2f}")
st.metric("Salario promedio de hombres", f"{salario_promedio_hombres:.2f}")
st.metric("Diferencia absoluta de salario (Hombres - Mujeres)", f"{diferencia_salario:.2f}")
st.metric("Diferencia porcentual", f"{diferencia_porcentual:.2f}%")

st.header("Correlograma Colombia:")
# Visualización de la matriz de correlación
def generar_correlograma(df, title):
    """
    Genera un correlograma para las columnas seleccionadas.
    """
    st.write("Columnas del DataFrame:", df.columns.tolist())  # Mostrar las columnas disponibles
    try:
        df_selected = df[['GENERO_NUMERICO', 'NIVEL EDUCACION ORDENADO', 'SALARIO_CALCULADO']]
    except KeyError as e:
        st.error(f"Error: {str(e)}")  # Mostrar el error si las columnas no están
        return  # Termina la función si hay un error

    correlation_matrix = df_selected.corr()
    
    plt.figure(figsize=(10, 6))  # Ajustar el tamaño del gráfico
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title(title)
    
    st.pyplot(plt)  # Mostrar el gráfico en Streamlit
    plt.clf()  # Limpiar la figura para evitar superposición en futuros gráficos

# Generar correlograma
generar_correlograma(df, 'Correlograma de Datos Completos')
###############################################################################################################################################

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Cargar Datos
# Ruta del archivo CSV
file_path = r'C:\Users\omarv\Desktop\Proyecto_Org\España\datos.csv'

# Leer el archivo CSV usando ';' como separador
df = pd.read_csv(file_path, sep=';')

# 2. Filtrar Datos
# Filtrar las filas donde 'Sexo/Brecha de género' no contenga "Cociente" y donde 'Tipo de jornada' no sea 'Total'
df_filtered = df[
    (~df['Sexo/Brecha de género'].str.contains('Cociente', case=False, na=False)) &
    (df['Tipo de jornada'] != 'Total')
]

# Limpiar la columna 'Total', reemplazar comas por puntos y convertir a numérico
df_filtered['Total'] = pd.to_numeric(df_filtered['Total'].str.replace(',', '.'), errors='coerce')

# 3. Agrupar y Calcular Promedio
# Agrupar por 'Tipo de jornada' y 'Sexo/Brecha de género', y calcular el promedio de 'Total'
promedio_total = df_filtered.groupby(['Tipo de jornada', 'Sexo/Brecha de género'])['Total'].mean().reset_index()

# Asignar valores numéricos al género (Mujeres = 0, Hombres = 1)
promedio_total['GENERO_NUMERICO'] = np.where(promedio_total['Sexo/Brecha de género'] == 'Mujeres', 0, 1)

# 4. Crear DataFrame Filtrado por Género
# Filtrar para obtener solo datos de 'Mujeres' y 'Hombres'
df_filtered = df[df['Sexo/Brecha de género'].isin(['Mujeres', 'Hombres'])]

# Asignar valores numéricos al género en el DataFrame filtrado
df_filtered['GENERO_NUMERICO'] = df_filtered['Sexo/Brecha de género'].apply(lambda x: 0 if x == 'Mujeres' else 1)

# Limpiar la columna 'Total' en el DataFrame filtrado
df_filtered['Total'] = pd.to_numeric(df_filtered['Total'].str.replace(',', '.'), errors='coerce')

# Filtrar filas donde 'Tipo de jornada' no sea 'Total'
df_filtered = df_filtered[df_filtered['Tipo de jornada'] != 'Total']



###############################################################################################################################################

st.markdown("<h1 style='text-align: center;'>Resultados de España:</h1>", unsafe_allow_html=True)
st.header("Estadísiscas de España:")

# Cálculo de la diferencia salarial por jornada
def calcular_diferencias_salariales(promedio_total):
    """
    Calcula la diferencia salarial entre hombres y mujeres en cada tipo de jornada.
    """
    diferencias = []

    for jornada in promedio_total['Tipo de jornada'].unique():
        jornada_data = promedio_total[promedio_total['Tipo de jornada'] == jornada]
        salario_hombres = jornada_data[jornada_data['Sexo/Brecha de género'] == 'Hombres']['Total'].values[0]
        salario_mujeres = jornada_data[jornada_data['Sexo/Brecha de género'] == 'Mujeres']['Total'].values[0]

        diferencia_salarial = salario_hombres - salario_mujeres
        diferencia_porcentual = (diferencia_salarial / salario_mujeres) * 100

        diferencias.append({
            'Tipo de jornada': jornada,
            'Salario Hombres': salario_hombres,
            'Salario Mujeres': salario_mujeres,
            'Diferencia Salarial': diferencia_salarial,
            'Diferencia Porcentual (%)': diferencia_porcentual
        })

    return pd.DataFrame(diferencias)

# Calcular las diferencias salariales
diferencias_salariales = calcular_diferencias_salariales(promedio_total)

# Mostrar los resultados en una tabla
st.subheader("Diferencias Salariales por Tipo de Jornada")
st.dataframe(diferencias_salariales)

st.header("Correlograma España:")

# Correlogramas
def generar_correlograma_filtrado(df, title):
    """
    Genera un correlograma para el DataFrame filtrado.
    """
    correlation_matrix = df.corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title(title)
    st.pyplot(plt)
    plt.clf()  # Limpiar la figura

# Correlograma del DataFrame filtrado
st.write("Columnas del DataFrame filtrado:", df_filtered.columns.tolist())  # Mostrar columnas del DataFrame filtrado
generar_correlograma_filtrado(df_filtered[['Total', 'GENERO_NUMERICO']], 'Correlograma de Datos Filtrados por Género')



###############################################################################################################################################
