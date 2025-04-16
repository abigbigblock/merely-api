
from fastapi import FastAPI, Request
import pandas as pd
import unicodedata

app = FastAPI()

def normalizar(frase):
    return ''.join(
        c for c in unicodedata.normalize('NFD', frase)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

def expandir_sintoma(frase_usuario):
    df = pd.read_csv("sintomas_frases_relacionadas_limpio.csv")
    frase_normalizada = normalizar(frase_usuario)

    for _, fila in df.iterrows():
        equivalentes = [normalizar(eq) for eq in str(fila["síntomas o frases relacionadas"]).split(",")]
        if any(eq in frase_normalizada for eq in equivalentes):
            return normalizar(fila["condición catalogada"])
    
    return frase_normalizada

@app.post("/buscar")
async def buscar(request: Request):
    try:
        data = await request.json()
        sintoma = data.get("sintoma", "")
        print(f"Sintoma recibido: {sintoma}")
        sintoma_exp = expandir_sintoma(sintoma)
        print(f"Sintoma expandido: {sintoma_exp}")

        df_catalogo = pd.read_csv("catalogo.csv")
        resultados = df_catalogo[df_catalogo["Recomendado para"].str.lower().str.contains(sintoma_exp, na=False)]

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

@app.head("/")
def health_check_head():
    return {"status": "ok"}
