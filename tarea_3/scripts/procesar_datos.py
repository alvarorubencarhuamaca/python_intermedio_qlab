"""Limpia los datos del MEF y arma los indicadores y el archivo del dashboard.

Entrada:  datos/originales/gasto_departamento_nivel_generica.csv y peru_departamentos.geojson
Salida:   datos/procesados/panel.csv  (año x nivel x departamento)
          web/data/datos.js            (panel + mapa, lo que lee el dashboard)
Uso: python scripts/procesar_datos.py
"""
import json
import unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ORIG, PROC, WEB = BASE / "datos/originales", BASE / "datos/procesados", BASE / "web/data"
PROC.mkdir(parents=True, exist_ok=True)
WEB.mkdir(parents=True, exist_ok=True)
NUM = ["pia", "pim", "devengado"]


def norm(s):
    s = unicodedata.normalize("NFD", str(s).upper()).encode("ascii", "ignore").decode().strip()
    return "CALLAO" if "CALLAO" in s else s


raw = pd.read_csv(ORIG / "gasto_departamento_nivel_generica.csv", dtype={"codigo": str, "cod_dep": str})
raw["cod_dep"] = raw["cod_dep"].str.zfill(2)
raw = raw.drop_duplicates(subset=["anio", "nivel", "cod_dep", "codigo"])
for c in NUM:
    raw[c] = pd.to_numeric(raw[c].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
raw["departamento"] = raw["departamento"].map(norm)
raw["es_inversion"] = raw["nombre"].map(norm).str.contains("ACTIVOS NO FINANCIEROS")
print("Genéricas encontradas:", sorted(raw["nombre"].unique()))

g = ["anio", "nivel", "nivel_nombre", "cod_dep", "departamento"]
total = raw.groupby(g)[NUM].sum().add_suffix("_total")
inv = raw[raw["es_inversion"]].groupby(g)[NUM].sum().add_suffix("_inv")
panel = total.join(inv, how="left").fillna(0).reset_index()
panel.to_csv(PROC / "panel.csv", index=False)

# Validación: sumas por año
print((panel.groupby("anio")[["pim_total", "pim_inv", "devengado_inv"]].sum() / 1e6).round(0))

geo = json.loads((ORIG / "peru_departamentos.geojson").read_text(encoding="utf-8"))
clave = next(k for k in geo["features"][0]["properties"] if "NOMB" in k.upper() or "NAME" in k.upper())
for f in geo["features"]:
    f["id"] = norm(f["properties"][clave])
    f["properties"] = {"nombre": f["id"]}
print("Departamentos sin polígono:", (set(panel["departamento"]) - {f["id"] for f in geo["features"]}) or "ninguno")

cols = g + [c + s for s in ("_total", "_inv") for c in NUM]
salida = {"panel": panel[cols].round(0).to_dict("records"), "geo": geo,
          "fecha_descarga": str(raw["fecha_descarga"].iloc[0])}
(WEB / "datos.js").write_text("window.DATOS = " + json.dumps(salida, ensure_ascii=False) + ";", encoding="utf-8")
print("OK:", len(panel), "filas en el panel")
