# Tarea 1

Trabajo individual del curso intermedio de Python - QLab PUCP.
## Dashboard interactivo

Se desarrolló un dashboard con Streamlit para explorar las noticias recolectadas y utilizar el modelo de clasificación entrenado.

El dashboard permite:

- Filtrar noticias por categoría.
- Buscar palabras dentro de los titulares.
- Visualizar métricas principales del dataset.
- Explorar gráficos interactivos desarrollados con Plotly.
- Visualizar y descargar las noticias filtradas en formato CSV.
- Ingresar un nuevo titular y predecir su categoría mediante el modelo Transformer fine-tuned.

### Modelos evaluados

Los tres métodos fueron evaluados sobre el mismo conjunto de prueba de 60 noticias.

| Modelo | Accuracy | F1 Macro |
|---|---:|---:|
| Zero-Shot | 0.733 | 0.731 |
| Qwen LLM | 0.933 | 0.933 |
| DistilBERT fine-tuned | 0.900 | 0.901 |

El modelo utilizado para la predicción interactiva del dashboard es DistilBERT multilingüe fine-tuned con las etiquetas generadas mediante el LLM.

### Ejecución local

Instalar las dependencias:

```bash
pip install -r tarea_1/requirements.txt
streamlit run tarea_1/app.py