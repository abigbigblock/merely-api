
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
        print(f"Síntoma recibido: {sintoma}")
        condicion = expandir_sintoma(sintoma)
        print(f"Condición catalogada encontrada: {condicion}")

        df_catalogo = pd.read_csv("catalogolisto.csv")
        resultados = df_catalogo[df_catalogo["Recomendado para"].str.lower().str.contains(condicion, na=False)]

        texto = ""
        for _, row in resultados.iterrows():
            texto += f"Producto: {row.get('Producto', 'N/A')}
"
            texto += f"Descripción: {row.get('Descripcion', 'N/A')}
"
            texto += f"Uso sugerido: {row.get('Forma de uso', 'N/A')}
"
            texto += f"Puntaje: {row.get('Puntaje', 0)} | Origen: {row.get('Origen', 'N/A')}
"
            texto += "-"*30 + "\n"

        return {"respuesta": texto}
    except Exception as e:
        print(f"Error interno en /buscar: {e}")
        return {"respuesta": ""}
