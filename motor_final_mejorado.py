
import pandas as pd
from collections import defaultdict

SINONIMOS = {
    "acidez estomacal": ["acidez estomacal"],
    "acido urico": ["acido urico"],
    "acne": ["acne"],
    "agruras": ["agruras"],
    "alcoholismo": ["alcoholismo"],
    "alergia": ["alergia"],
    "alzhaimer": ["alzhaimer"],
    "amenorrea": ["amenorrea"],
    "amigdalitis": ["amigdalitis"],
    "anemia": ["anemia"]
}

bitacora = {}

def preparar_dataframe(ruta_excel):
    df_catalogo = pd.read_excel(ruta_excel, sheet_name='Catálogo')
    df_ingredientes = pd.read_excel(ruta_excel, sheet_name='Ingredientes ')
    return df_catalogo, df_ingredientes

def combinar_ingredientes(df):
    if 'Ingredientes principales' not in df.columns:
        cols = ['1er. Ingrediente principal', '2.do Ingrediente principal', '3er. Ingrediente principal']
        df['Ingredientes principales'] = df[cols].fillna('').agg(', '.join, axis=1)
    return df

def expandir_sinonimos(sintoma):
    coincidencias = [s for s in SINONIMOS if sintoma in s]
    equivalentes = set(coincidencias + [sintoma])
    return list(equivalentes)

def motor_semantico(df_catalogo, sintomas):
    resultados = pd.DataFrame()
    for sintoma in sintomas:
        parciales = df_catalogo[
            df_catalogo['Descripcion'].str.contains(sintoma, case=False, na=False) |
            df_catalogo['Recomendado para'].str.contains(sintoma, case=False, na=False)
        ].copy()
        if not parciales.empty:
            parciales['Puntaje'] = (
                2 * parciales['Descripcion'].str.contains(sintoma, case=False, na=False).astype(int) +
                1 * parciales['Recomendado para'].str.contains(sintoma, case=False, na=False).astype(int)
            )
            parciales['Origen'] = 'Semántico'
            resultados = pd.concat([resultados, parciales], ignore_index=True)
    return resultados

def motor_clinico(df_catalogo, df_ingredientes, sintomas):
    df_catalogo = combinar_ingredientes(df_catalogo)
    resultados = pd.DataFrame()
    for sintoma in sintomas:
        ingredientes_utiles = df_ingredientes[
            df_ingredientes['Síntoma o Condición'].str.contains(sintoma, case=False, na=False)
        ]['Producto'].unique()
        if len(ingredientes_utiles) > 0:
            coincidencias = df_catalogo[
                df_catalogo['Ingredientes principales'].str.contains('|'.join(ingredientes_utiles), case=False, na=False)
            ].copy()
            if not coincidencias.empty:
                coincidencias['Puntaje'] = 3
                coincidencias['Origen'] = 'Clínico'
                resultados = pd.concat([resultados, coincidencias], ignore_index=True)
    return resultados

def motor_optimizado(ruta_excel, sintoma_entrada):
    global bitacora
    df_catalogo, df_ingredientes = preparar_dataframe(ruta_excel)
    sintomas_expandidos = expandir_sinonimos(sintoma_entrada.lower())
    
    semanticos = motor_semantico(df_catalogo.copy(), sintomas_expandidos)
    clinicos = motor_clinico(df_catalogo.copy(), df_ingredientes, sintomas_expandidos)

    combinados = pd.concat([semanticos, clinicos], ignore_index=True)
    combinados = combinados.drop_duplicates(subset=['Producto'], keep='first')

    if 'Puntaje' not in combinados.columns:
        combinados['Puntaje'] = 0

    combinados = combinados.sort_values(by='Puntaje', ascending=False).reset_index(drop=True)

    bitacora = {
        'Síntoma buscado': sintoma_entrada,
        'Síntomas expandidos': sintomas_expandidos,
        'Resultados totales': len(combinados),
        'Máximo puntaje': combinados['Puntaje'].max() if not combinados.empty else 0,
        'Mínimo puntaje': combinados['Puntaje'].min() if not combinados.empty else 0,
        'Resultados por origen': combinados['Origen'].value_counts().to_dict() if 'Origen' in combinados.columns else {}
    }

    return combinados

def informe_interno():
    return bitacora
