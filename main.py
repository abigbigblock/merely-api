
from fastapi import FastAPI, Request
from motor_final_mejorado import motor_optimizado, informe_interno

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API de búsqueda de Merely funcionando."}

@app.post("/buscar")
async def buscar(request: Request):
    data = await request.json()
    sintoma = data.get("sintoma", "")
    resultados = motor_optimizado("Catalogo_extendido_por_ingrediente.xlsx", sintoma)
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
