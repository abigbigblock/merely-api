
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
import unicodedata
import requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar catálogos
df_catalogo = pd.read_csv("catalogo.csv")
df_sintomas = pd.read_csv("sintomas_frases_relacionadas_limpio.csv")
df_ingredientes = pd.read_csv("ingredientes.csv")

# Expandir síntomas (sinónimos)
def expandir_sintoma(sintoma_usuario):
    sintoma_normalizado = normalizar(sintoma_usuario)
    coincidencias = []

    for _, row in df_sintomas.iterrows():
        cond = normalizar(row["condición catalogada"])
        if sintoma_normalizado == cond or sintoma_normalizado in normalizar(row["Síntomas o frases relacionadas"]):
            coincidencias.append(cond)
    
    return list(set(coincidencias + [sintoma_normalizado]))

# Normalización para evitar errores por acentos
def normalizar(texto):
    if pd.isna(texto):
        return ""
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("utf-8").lower()

# Buscar productos relevantes
@app.post("/buscar")
async def buscar(request: Request):
    data = await request.json()
    sintoma = data.get("sintoma", "")
    sintomas_expandido = expandir_sintoma(sintoma)

    resultados = []

    for _, row in df_catalogo.iterrows():
        puntaje = 0
        motivos = []

        # Revisión en descripción
        desc = normalizar(row.get("Descripcion", ""))
        if any(s in desc for s in sintomas_expandido):
            puntaje += 3
            motivos.append("Coincidencia en descripción")

        # Revisión en campo 'Recomendado para'
        recomendado = normalizar(row.get("Recomendado para", ""))
        if any(s in recomendado for s in sintomas_expandido):
            puntaje += 2
            motivos.append("Coincidencia en campo recomendado")

        # Revisión en archivo de síntomas/frases
        if any(s in recomendado or s in desc for s in sintomas_expandido):
            puntaje += 1.5
            motivos.append("Coincidencia con frase relacionada")

        # Revisión por ingrediente
        ingredientes_producto = df_ingredientes[df_ingredientes["Producto"] == row.get("Producto")]
        ingredientes_relevantes = ingredientes_producto["Síntoma o Condición"].dropna().apply(normalizar).tolist()

        if any(s in sintomas_expandido for s in ingredientes_relevantes):
            puntaje += 1
            motivos.append("Ingrediente útil para el síntoma")

        if puntaje > 0:
            resultados.append({
                "Producto": row.get("Producto", "N/A"),
                "Descripcion": row.get("Descripcion", "N/A"),
                "Forma de uso": row.get("Forma de uso", "N/A"),
                "Puntaje": round(puntaje, 2),
                "Motivos": ", ".join(motivos)
            })

    # Ordenar por puntaje descendente
    resultados = sorted(resultados, key=lambda x: x["Puntaje"], reverse=True)
    return {"respuesta": resultados}

# HEAD y GET para mantener vivo el render
@app.get("/")
async def head_check():
    return {"message": "API de búsqueda de Merely funcionando."}

@app.head("/")
async def head_status():
    return {}
