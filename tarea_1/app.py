from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------------------------
# Configuración
# -------------------------------------------------

st.set_page_config(
    page_title="Clasificador de Noticias",
    page_icon="📰",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
RUTA_DATOS = BASE_DIR / "datos" / "noticias.csv"


# -------------------------------------------------
# Carga de datos
# -------------------------------------------------

df = pd.read_csv(RUTA_DATOS)

# Longitud del titular
df["longitud_titular"] = df["titular"].astype(str).str.len()


# -------------------------------------------------
# Encabezado
# -------------------------------------------------

st.title("📰 Clasificador y análisis de noticias")

st.write(
    "Dashboard desarrollado para analizar noticias de La República "
    "y comparar métodos de clasificación automática."
)


# -------------------------------------------------
# Filtros
# -------------------------------------------------

st.sidebar.header("Filtros")

categorias = sorted(df["etiqueta"].dropna().unique())

categorias_seleccionadas = st.sidebar.multiselect(
    "Categoría",
    options=categorias,
    default=categorias
)

busqueda = st.sidebar.text_input(
    "Buscar en titulares",
    placeholder="Ejemplo: elecciones"
)


# Aplicar filtros
df_filtrado = df[
    df["etiqueta"].isin(categorias_seleccionadas)
].copy()

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["titular"].str.contains(
            busqueda,
            case=False,
            na=False
        )
    ]


# -------------------------------------------------
# Métricas principales
# -------------------------------------------------

st.subheader("Resumen")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Noticias",
    len(df_filtrado)
)

col2.metric(
    "Categorías",
    df_filtrado["etiqueta"].nunique()
)

promedio_longitud = (
    df_filtrado["longitud_titular"].mean()
    if len(df_filtrado) > 0
    else 0
)

col3.metric(
    "Longitud promedio del titular",
    f"{promedio_longitud:.1f} caracteres"
)

# -------------------------------------------------
# Gráficos
# -------------------------------------------------

st.subheader("Visualización de noticias")

col_grafico1, col_grafico2 = st.columns(2)

# Gráfico 1: noticias por categoría
conteo_categorias = (
    df_filtrado["etiqueta"]
    .value_counts()
    .reset_index()
)

conteo_categorias.columns = ["categoria", "cantidad"]

fig_categorias = px.bar(
    conteo_categorias,
    x="categoria",
    y="cantidad",
    title="Noticias por categoría",
    labels={
        "categoria": "Categoría",
        "cantidad": "Número de noticias"
    }
)

col_grafico1.plotly_chart(
    fig_categorias,
    use_container_width=True
)


# Gráfico 2: longitud de titulares
fig_longitud = px.histogram(
    df_filtrado,
    x="longitud_titular",
    nbins=20,
    title="Distribución de longitud de titulares",
    labels={
        "longitud_titular": "Número de caracteres"
    }
)

col_grafico2.plotly_chart(
    fig_longitud,
    use_container_width=True
)
# -------------------------------------------------
# Tabla
# -------------------------------------------------

st.subheader("Dataset de noticias")

st.dataframe(
    df_filtrado[
        [
            "titular",
            "bajada",
            "etiqueta",
            "fecha"
        ]
    ],
    use_container_width=True,
    hide_index=True
)