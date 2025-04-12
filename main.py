
from fastapi import FastAPI, Request
from motor_final_csv import motor_optimizado_csv, informe_interno

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API CSV de Merely corriendo correctamente."}

@app.post("/buscar")
async def buscar(request: Request):
    try:
        data = await request.json()
        sintoma = data.get("sintoma", "")
        print(f"Síntoma recibido: {sintoma}")
        resultados = motor_optimizado_csv(sintoma)
        print(f"Bitácora de búsqueda: {informe_interno()}")
        texto = ""
        for _, row in resultados.iterrows():
            texto += f"Producto: {row.get('Producto', 'N/A')}\n"
            texto += f"Descripción: {row.get('Descripcion', 'N/A')}\n"
            texto += f"Uso sugerido: {row.get('Forma de uso', 'N/A')}\n"
            texto += f"Puntaje: {row.get('Puntaje', 0)} | Origen: {row.get('Origen', 'Desconocido')}\n"
            texto += "-"*30 + "\n"
        return {"respuesta": texto}
    except Exception as e:
        print(f"Error interno en /buscar: {e}")
        return {"respuesta": ""}
