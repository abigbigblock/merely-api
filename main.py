
import pandas as pd
import requests
from fastapi import FastAPI, Request
from motor_final_mejorado import motor_optimizado, informe_interno

app = FastAPI()

CATALOGO_URL = "https://www.dropbox.com/scl/fi/16rdsm0sa0zdl47cd18as/Catalogo_extendido_por_ingrediente.xlsx?rlkey=5ehm51ij2zs9z2nkpcva42y5d&st=hxe68147&dl=1"
CATALOGO_ARCHIVO = "Catalogo_extendido_por_ingrediente.xlsx"

def descargar_catalogo():
    try:
        response = requests.get(CATALOGO_URL)
        response.raise_for_status()
        with open(CATALOGO_ARCHIVO, "wb") as f:
            f.write(response.content)
        print("Archivo Excel descargado correctamente.")
    except Exception as e:
        print(f"Error al descargar el archivo Excel: {e}")

# Descargar el archivo al iniciar la app
descargar_catalogo()

@app.get("/")
def root():
    return {"message": "API de búsqueda de Merely funcionando (con descarga automática)."}

@app.post("/buscar")
async def buscar(request: Request):
    data = await request.json()
    sintoma = data.get("sintoma", "")
    resultados = motor_optimizado(CATALOGO_ARCHIVO, sintoma)
    texto = ""
    for _, row in resultados.iterrows():
        texto += f"Producto: {row.get('Nombre', 'N/A')}\n"
        texto += f"Descripción: {row.get('Descripcion', 'N/A')}\n"
        texto += f"Uso sugerido: {row.get('Forma de uso', 'N/A')}\n"
        texto += f"Puntaje: {row.get('Puntaje', 0)} | Origen: {row.get('Origen', 'Desconocido')}\n"
        texto += "-"*30 + "\n"
    return {"respuesta": texto}

@app.get("/informe")
def obtener_informe():
    return informe_interno()
