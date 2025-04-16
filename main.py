
from fastapi import FastAPI, Request
import pandas as pd

app = FastAPI()

def expandir_sintoma(frase_usuario):
    df = pd.read_csv("sintomas_frases_relacionadas_limpio.csv")
    frase_normalizada = frase_usuario.strip().lower()

    for _, fila in df.iterrows():
        equivalentes = str(fila["síntomas o frases relacionadas"]).lower().split(",")
        if any(eq.strip() in frase_normalizada for eq in equivalentes):
            return fila["condición catalogada"].strip().lower()

    return frase_usuario.strip().lower()

@app.post("/buscar")
async def buscar(request: Request):
    try:
        data = await request.json()
        sintoma = data.get("sintoma", "")
        print(f"Sintoma recibido: {sintoma}")
        sintoma = expandir_sintoma(sintoma)

        df = pd.read_csv("catalogolisto.csv")
        resultados = df[df["Recomendado para"].str.lower().str.contains(sintoma)]

        texto = ""
        for _, row in resultados.iterrows():
            texto += f"Producto: {row.get('Producto', 'N/A')}\n"
            texto += f"Descripción: {row.get('Descripcion', 'N/A')}\n"
            texto += f"Uso sugerido: {row.get('Forma de uso', 'N/A')}\n"
            texto += f"Puntaje: {row.get('Puntaje', 0)} | Origen: {row.get('Origen', 'N/A')}\n"
            texto += "-"*30 + "\n"

        return {"respuesta": texto}
    except Exception as e:
        print(f"Error interno en /buscar: {e}")
        return {"respuesta": ""}

@app.get("/")
def health_check():
    return {"status": "ok"}
