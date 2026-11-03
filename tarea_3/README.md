# Tarea 3 · Inversión pública en el Perú: ¿quién deja el dinero sin gastar?

**Dashboard:** https://alvarorubencarhuamaca.github.io/python_intermedio_qlab/tarea_3/web/
**Reel:** [`reel/reel.mp4`](reel/reel.mp4) (≈50 s, 1080×1920)
**Publicación de LinkedIn:** _(pendiente: pegar enlace)_

## 1. Tema y pregunta de investigación

**Tema:** ejecución del presupuesto de inversión pública en el Perú.

**Pregunta:** ¿Cómo evolucionó la ejecución del presupuesto de inversión pública entre 2019 y 2026, y qué niveles de
gobierno y departamentos se quedan atrás?

- Cobertura geográfica: 25 departamentos (según la ubicación de la meta presupuestal).
- Cobertura temporal: 2019–2026. El año 2026 está en curso (datos al 2 de noviembre de 2026).

## 2. Descripción

Descargué de Consulta Amigable (MEF) el presupuesto y la ejecución por año, nivel de gobierno, departamento y
genérica de gasto. Con eso construí indicadores de avance de ejecución de la inversión y un dashboard interactivo
(4 o más KPIs, 5 visualizaciones con mapa y 4 controles). Los hallazgos se cuentan en un reel vertical de unos 60 segundos, narrado con mi
voz clonada con IA.

## 3. Fuentes y metodología

| Fuente | Uso | Enlace |
|---|---|---|
| MEF – Consulta Amigable (Consulta de Ejecución del Gasto) | PIA, PIM y devengado | https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx |
| juaneladio/peru-geojson (basado en INEI) | Límites departamentales | https://github.com/juaneladio/peru-geojson |

**Obtención** (`scripts/obtener_datos.py`): Consulta Amigable navega en jerarquía, así que para cada año (2019–2026),
nivel de gobierno (Nacional `E`, Regional `R`, Local `M`) y departamento (`01`–`25`) se pide la tabla desagregada por
genérica de gasto. Son 600 consultas. Cada fila guarda la URL de origen y la fecha de descarga.

**Procesamiento** (`scripts/procesar_datos.py`): limpieza de montos, eliminación de duplicados, normalización de
nombres (tildes, Callao) y un panel año × nivel × departamento en `datos/procesados/panel.csv`.

**Indicadores:**
- Inversión = genérica 2.6 *Adquisición de activos no financieros*.
- Avance (%) = devengado / PIM.
- No ejecutado = PIM − devengado.
- % inversión = PIM de inversión / PIM total.
- PIM/PIA = cuánto creció el presupuesto durante el año.

## 4. Tres hallazgos principales

1. **La ejecución mejoró mucho desde 2019.** El avance de la inversión pasó de 64.4% (2019) a 83.7% (2025) y el devengado
   casi se duplicó: de S/ 33.0 mil millones a S/ 61.6 mil millones (+87%). Aun así, en 2025 quedaron S/ 12.0 mil millones
   sin ejecutar.
2. **Los gobiernos locales son el cuello de botella.** Tienen el mayor PIM de inversión (S/ 30.7 mil millones en 2025), pero
   ejecutan 72.9%, frente a 90.3% del Gobierno Nacional y 93.5% de los gobiernos regionales. Concentran S/ 8.3 de los
   12.0 mil millones no ejecutados (69%). Además, su PIM es 1.9 veces su PIA: gran parte del dinero llega durante el año.
3. **Persisten brechas territoriales.** En 2025, Tacna (89.6%) y Piura (88.9%) lideran, y Ica y Áncash (76.5%) quedan
   últimos. Piura es el departamento que más mejoró desde 2019 (+37 pp) y Ucayali el único que retrocedió (82.1% → 80.3%).

Dato 2026 (parcial, al 2 de noviembre): el avance total es 64.4% y el de los gobiernos locales, 53.5%.

## 5. Limitaciones

- 2026 está en curso: su avance no es comparable con los años cerrados.
- El devengado mide el gasto registrado, no la calidad ni la culminación de las obras.
- La genérica 2.6 incluye equipamiento de actividades, no solo proyectos de inversión.
- Montos nominales (sin deflactar) y no per cápita.
- Se excluyen los montos multidepartamentales o en el exterior. Las cifras corresponden a la fecha de descarga, porque el MEF actualiza su base.

## 6. Estructura

```
tarea_3/
├── README.md
├── requirements.txt
├── datos/
│   ├── originales/   gasto_departamento_nivel_generica.csv, peru_departamentos.geojson
│   └── procesados/   panel.csv
├── scripts/          obtener_datos.py, procesar_datos.py
├── web/              index.html (dashboard), assets/plotly.min.js, data/datos.js, capturas/
└── reel/             guion.json, hacer_reel.py, subtitulos.srt, reel.mp4, recursos/ (imágenes y música)
```

## 7. Cómo reproducirlo

```bash
cd tarea_3
pip install -r requirements.txt
python scripts/obtener_datos.py     # ~5 min, 600 consultas al MEF
python scripts/procesar_datos.py    # genera datos/procesados y web/data/datos.js
# abrir web/index.html en el navegador
```

**Reel** (entorno de la Sesión 15 del curso: `qwen-tts faster-whisper pillow imageio-ffmpeg soundfile jiwer num2words`):

```bash
cd tarea_3/reel
python hacer_reel.py --voz mi_voz.wav --musica recursos/musica.mp3
```

Si la laptop no tiene RAM suficiente, el notebook [`reel/generar_reel_colab.ipynb`](reel/generar_reel_colab.ipynb)
corre lo mismo en Google Colab con GPU (así se generó el reel final). Después se corrigió a mano un subtítulo que Whisper
transcribió mal («cada uno» → «cada diez») y la tilde de «Áncash», y se añadió un cierre de 4 s con el enlace al dashboard.

`hacer_reel.py` reutiliza `reel.py` de la [Sesión 15](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/15-texto-a-reel)
para la voz clonada (Qwen3-TTS) y los subtítulos (Whisper). Sobre eso arma el video con imágenes del dashboard, un zoom suave,
subtítulos sincronizados y música de fondo. Las cifras del guion están verificadas en `guion.json` (campo `verificacion`).

**Créditos del reel:** voz generada con IA (Qwen3-TTS) a partir de mi propia voz. Música: «Synthwave» de The_Mountain ([Pixabay](https://pixabay.com/music/), Pixabay Content License).
Imágenes: capturas del propio dashboard.

## 8. Uso de inteligencia artificial

Usé Claude (Anthropic) para escribir los scripts de descarga y procesamiento, el dashboard y el guion. Revisé las cifras
contra los datos descargados. La narración se generó con Qwen3-TTS a partir de una grabación de mi propia voz, y los subtítulos
con Whisper.
