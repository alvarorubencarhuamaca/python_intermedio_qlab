from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import torch

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# -------------------------------------------------
# Configuración
# -------------------------------------------------

st.set_page_config(
    page_title="Clasificador de Noticias",
    page_icon="📰",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
RUTA_MODELO = BASE_DIR / "modelo" / "modelo_final"


@st.cache_resource
def cargar_modelo():
    tokenizer_modelo = AutoTokenizer.from_pretrained(
        str(RUTA_MODELO)
    )

    modelo = AutoModelForSequenceClassification.from_pretrained(
        str(RUTA_MODELO)
    )

    modelo.eval()

    return tokenizer_modelo, modelo
def predecir_categoria(titular, tokenizer_modelo, modelo):
    entradas = tokenizer_modelo(
        titular,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        salida = modelo(**entradas)

    probabilidades = torch.softmax(
        salida.logits,
        dim=-1
    )[0]

    id_prediccion = int(torch.argmax(probabilidades).item())

    categoria = modelo.config.id2label[id_prediccion]
    probabilidad = float(probabilidades[id_prediccion].item())

    return categoria, probabilidad
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
# Clasificación de nuevo titular
# -------------------------------------------------

st.subheader("Clasificar un nuevo titular")

titular_usuario = st.text_input(
    "Nuevo titular",
    placeholder="Ejemplo: Congreso aprueba nueva reforma electoral"
)

if st.button("Predecir categoría"):

    if titular_usuario.strip():

        tokenizer_modelo, modelo_clasificador = cargar_modelo()

        categoria, probabilidad = predecir_categoria(
            titular_usuario,
            tokenizer_modelo,
            modelo_clasificador
        )

        nombres_categorias = {
            "politica": "Política",
            "economia": "Economía",
            "deportes": "Deportes",
            "ciencia_tecnologia": "Ciencia y tecnología"
        }

        categoria_mostrada = nombres_categorias.get(
            categoria,
            categoria
        )

        st.success(
            f"Categoría predicha: **{categoria_mostrada}**"
        )

        st.metric(
            "Probabilidad estimada",
            f"{probabilidad:.1%}"
        )

    else:
        st.warning(
            "Ingresa un titular antes de realizar la predicción."
        )
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
# Preparar archivo CSV descargable
columnas_descarga = [
    "titular",
    "bajada",
    "etiqueta",
    "fecha"
]

csv_descarga = (
    df_filtrado[columnas_descarga]
    .to_csv(index=False)
    .encode("utf-8-sig")
)

st.download_button(
    label="⬇️ Descargar noticias filtradas",
    data=csv_descarga,
    file_name="noticias_filtradas.csv",
    mime="text/csv"
)