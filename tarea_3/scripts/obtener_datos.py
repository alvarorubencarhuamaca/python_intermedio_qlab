"""Descarga la ejecución del gasto público por departamento, nivel de gobierno y genérica de gasto
desde Consulta Amigable del MEF (2019-2026), y el GeoJSON de departamentos del Perú.

Consulta Amigable navega en jerarquía (nivel > ... > departamento > ... > genérica): por eso se filtra por
año, nivel y departamento y se desagrega por genérica. La inversión es la genérica 2-6
"Adquisición de activos no financieros" (obras, equipamiento).

Uso (desde la carpeta tarea_3):  python scripts/obtener_datos.py
Requiere: pandas, requests, lxml.
"""
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL_MEF = "https://apps5.mineco.gob.pe/transparencia/Navegador/Navegar_7.aspx"
GEOJSON = "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental_simple.geojson"
COLUMNAS = ["nombre", "pia", "pim", "certificacion", "compromiso_anual",
            "atencion_compromiso_mensual", "devengado", "girado", "avance_pct"]
ANIOS = range(2019, 2027)
NIVELES = {"E": "Gobierno Nacional", "R": "Gobiernos Regionales", "M": "Gobiernos Locales"}
DEPARTAMENTOS = [f"{i:02d}" for i in range(1, 26)]

BASE = Path(__file__).resolve().parents[1]
ORIG = BASE / "datos" / "originales"
ORIG.mkdir(parents=True, exist_ok=True)


def tabla(params):
    """Pide una tabla a Consulta Amigable. Devuelve un DataFrame (vacío si no hay datos)."""
    for intento in range(3):
        try:
            r = requests.get(URL_MEF, params=params, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
            if 'class="Data"' not in r.text:
                return pd.DataFrame(), r.url          # combinación sin gasto
            df = pd.read_html(StringIO(r.text), attrs={"class": "Data"}, flavor="lxml")[0]
            df = df.iloc[:, 1:]
            df.columns = COLUMNAS
            partes = df["nombre"].astype(str).str.split(": ", n=1, expand=True)
            df.insert(0, "codigo", partes[0].str.strip())
            df["nombre"] = partes[1].str.strip()
            return df, r.url
        except Exception as e:
            print(f"   reintento {intento + 1} {params}: {e}")
            time.sleep(3)
    raise RuntimeError(f"Sin respuesta para {params}")


def departamentos(anio):
    """Nombres de los departamentos (desagregado simple por departamento)."""
    df, _ = tabla({"y": str(anio), "21": ""})
    return df[["codigo", "nombre"]]


def bajar(args):
    anio, nivel, dep = args
    df, url = tabla({"y": str(anio), "1": nivel, "21": dep, "24": ""})
    return df.assign(anio=anio, nivel=nivel, nivel_nombre=NIVELES[nivel], cod_dep=dep, url=url)


def main():
    nombres = departamentos(2025).rename(columns={"codigo": "cod_dep", "nombre": "departamento"})
    tareas = [(a, n, d) for a in ANIOS for n in NIVELES for d in DEPARTAMENTOS]
    print(f"{len(tareas)} consultas al MEF (unos minutos)...")
    partes = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, df in enumerate(ex.map(bajar, tareas), 1):
            partes.append(df)
            if i % 50 == 0:
                print(f"   {i}/{len(tareas)}")
    datos = pd.concat(partes).merge(nombres, on="cod_dep", how="left")
    datos["fecha_descarga"] = date.today().isoformat()
    datos.to_csv(ORIG / "gasto_departamento_nivel_generica.csv", index=False, encoding="utf-8")
    print("Filas:", len(datos))

    geo = requests.get(GEOJSON, timeout=60)
    geo.raise_for_status()
    (ORIG / "peru_departamentos.geojson").write_bytes(geo.content)
    print("Listo. Archivos en", ORIG)


if __name__ == "__main__":
    main()
