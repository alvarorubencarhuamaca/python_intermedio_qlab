"""Reel vertical (1080x1920) de la Tarea 3: voz clonada + imágenes del dashboard + subtítulos + música.

Reutiliza el módulo reel.py de la Sesión 15 del curso (d2cml-ai/Data-Science-Python) para la voz clonada
(Qwen3-TTS), el control de calidad y los subtítulos (Whisper). Lo nuevo aquí es el video: cada escena muestra
una imagen del dashboard (recursos/escenaN.png) con un zoom lento, subtítulos sincronizados y música de fondo.

Uso (desde tarea_3/reel, en el entorno de la sesión 15):
    python hacer_reel.py --voz mi_voz.m4a --musica recursos/musica.mp3
Salidas: reel.mp4, subtitulos.srt, narracion.wav
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument("--voz", required=True, help="15 a 25 s de tu propia voz (m4a, opus, wav, mp3)")
p.add_argument("--musica", default=str(AQUI / "recursos" / "musica.mp3"), help="música con licencia libre")
p.add_argument("--volumen-musica", type=float, default=0.10)
p.add_argument("--sesion15", default=str(AQUI.parents[2] / "Data-Science-Python" / "sessions" / "15-texto-a-reel"),
               help="carpeta de la sesión 15 (donde está reel.py)")
p.add_argument("--tts", default="Qwen/Qwen3-TTS-12Hz-0.6B-Base")
p.add_argument("--device", default="cpu")
p.add_argument("--velocidad", type=float, default=1.0)
a = p.parse_args()

sys.path.insert(0, a.sesion15)
import reel  # noqa: E402  (módulo de la Sesión 15)

ANCHO, ALTO, FPS = 1080, 1920, 30
ACENTO, TEXTO, CAJA = "#e9a23b", "#ffffff", "#0e1830"

guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
imagenes = [Image.open(AQUI / e["imagen"]).convert("RGB").resize((ANCHO, ALTO)) for e in guion["escenas"]]

# 1. Voz clonada y control de calidad (WER por escena)
voz = reel.Voz(a.voz, modelo=a.tts, device=a.device)
print("Referencia transcrita:", voz.texto_ref)
narr = reel.narrar(voz, guion, velocidad=a.velocidad)
print(f"Narración: {narr.duracion:.1f} s · WER por escena:", [round(e["wer"], 2) for e in guion["escenas"]])
if not 45 <= narr.duracion <= 75:
    print("¡Ojo! La tarea pide entre 45 y 75 segundos; prueben --velocidad o acorten el guion.")

# 2. Subtítulos palabra por palabra (Whisper) y archivo .srt
reel.subtitulos(narr, guion)
reel.a_srt(narr, AQUI / "subtitulos.srt")
bloques = reel._bloques(narr.palabras)
fuente_sub = reel._fuente("PublicSans", 58, 800)
wav = AQUI / "narracion.wav"
reel.sf.write(wav, narr.audio, narr.sr)


def escena_en(t):
    return max([k for k, (ini, _) in enumerate(narr.escenas) if ini - reel.PAUSA <= t] or [0])


def zoom(img, avance):
    """Zoom lento (de 100% a 104%) centrado, para que la imagen no quede estática."""
    z = 1 + 0.04 * avance
    w, h = int(ANCHO / z), int(ALTO / z)
    x, y = (ANCHO - w) // 2, (ALTO - h) // 2
    return img.crop((x, y, x + w, y + h)).resize((ANCHO, ALTO), Image.BILINEAR)


def cuadro(t):
    i = escena_en(t)
    ini = narr.escenas[i][0] - reel.PAUSA if i else 0
    fin = narr.escenas[i + 1][0] - reel.PAUSA if i + 1 < len(narr.escenas) else narr.duracion
    img = zoom(imagenes[i], (t - ini) / max(fin - ini, 0.1))
    if i and t - ini < 0.4:  # fundido desde la escena anterior
        img = Image.blend(zoom(imagenes[i - 1], 1), img, (t - ini) / 0.4)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 30, ANCHO - 60, 38), radius=4, fill="#2b3a5c")
    d.rounded_rectangle((60, 30, 60 + (ANCHO - 120) * t / narr.duracion, 38), radius=4, fill=ACENTO)
    b = next((b for b in bloques if b[0][0] - 0.1 <= t <= b[-1][1] + 0.25), None)
    if b:
        texto = " ".join(x[2] for x in b)
        w = d.textlength(texto, font=fuente_sub)
        x, y = (ANCHO - w) / 2, 1610
        d.rounded_rectangle((x - 36, y - 26, x + w + 36, y + fuente_sub.size + 34), radius=28, fill=CAJA)
        for s, e, palabra in b:
            d.text((x, y), palabra, font=fuente_sub, fill=ACENTO if s <= t <= e + 0.05 else TEXTO)
            x += d.textlength(palabra + " ", font=fuente_sub)
    return img


# 3. Video + narración + música (más baja que la voz y con fundido al final)
salida = AQUI / "reel.mp4"
musica = Path(a.musica)
entradas = ["-i", str(wav)]
if musica.exists():
    entradas += ["-stream_loop", "-1", "-i", str(musica)]
    dur = narr.duracion
    filtro = (f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[v];"
              f"[2:a]volume={a.volumen_musica},afade=t=out:st={dur - 2:.2f}:d=2,aresample=48000[m];"
              f"[v][m]amix=inputs=2:duration=first:normalize=0[a]")
    audio = ["-filter_complex", filtro, "-map", "0:v", "-map", "[a]"]
else:
    print("No encontré la música en", musica, "- el video saldrá solo con la narración.")
    audio = ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a"]
cmd = [reel.FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ANCHO}x{ALTO}",
       "-r", str(FPS), "-i", "-", *entradas, *audio, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-t", f"{narr.duracion:.2f}",
       "-movflags", "+faststart", str(salida)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for k in range(int(narr.duracion * FPS)):
    proc.stdin.write(cuadro(k / FPS).tobytes())
proc.stdin.close()
proc.wait()
(AQUI / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
print("Listo:", salida)
