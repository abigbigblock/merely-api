
import pandas as pd
import requests
from fastapi import FastAPI, Request
from motor_final_mejorado import motor_optimizado_csv, informe_interno

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
        validar_archivo()
    except Exception as e:
        print(f"Error al descargar el archivo Excel: {e}")

def validar_archivo():
    try:
        df_cat = pd.read_excel(CATALOGO_ARCHIVO, sheet_name='Catálogo')
        df_ing = pd.read_excel(CATALOGO_ARCHIVO, sheet_name='Ingredientes ')
        print(f"Hojas cargadas: Catálogo ({len(df_cat)} filas), Ingredientes ({len(df_ing)} filas)")
        print(f"Columnas en 'Catálogo': {list(df_cat.columns)}")
        print(f"Columnas en 'Ingredientes': {list(df_ing.columns)}")
    except Exception as e:
        print(f"Error al validar archivo Excel: {e}")

descargar_catalogo()

@app.get("/")
def root():
    return {"message": "API Merely con manejo de errores activo."}

@app.post("/buscar")
async def buscar(request: Request):
    try:
        data = await request.json()
        sintoma = data.get("sintoma", "")
        resultados = motor_optimizado_csv(CATALOGO_ARCHIVO, sintoma)
        texto = ""
        for _, row in resultados.iterrows():
            texto += f"Producto: {row.get('Nombre', 'N/A')}\n"
            texto += f"Descripción: {row.get('Descripcion', 'N/A')}\n"
            texto += f"Uso sugerido: {row.get('Forma de uso', 'N/A')}\n"
            texto += f"Puntaje: {row.get('Puntaje', 0)} | Origen: {row.get('Origen', 'Desconocido')}\n"
            texto += "-"*30 + "\n"
        return {"respuesta": texto}
    except Exception as e:
        print(f"ERROR interno en /buscar: {e}")
        return {"respuesta": ""}
