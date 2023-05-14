# Librerias utilizadas
from fastapi import FastAPI
from fastapi.responses import HTMLResponse # Utilizado para generar el formato de texto de la pagina de inicio 
import pandas as pd
import calendar
import locale
import json
import ast
import re

from collections import Counter
# Establecer el idioma en español
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

# Creacion de la App
app = FastAPI(title = "Project Data Engineer", description = "Henry's Data Engineering Project")

# Carga de csv con las transofrmaciones ya realizadas
df = pd.read_csv('Dataset/movies_final.csv', dtype={'popularity': str}, encoding='utf-8')

#Creamos una función index con mensaje de bienvenida
@app.get("/", response_class=HTMLResponse)
async def index ():
    output = "¡Bienvenido a la interfaz de consultas de películas. <br> Para conocer el formato de bÚsqueda, consulte el archivo README.md ubicado en el repositorio de GitHub."
    return output

# Se desarrollan las consultas que fueron solicitadas
# Consulta 1: Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes 
# (nombre del mes, en str, ejemplo 'enero') historicamente, return {'mes':mes, 'cantidad':respuesta}

@app.get("/peliculas_mes/")
def peliculas_mes(mes:str):
    # Convertir la columna "release_date" de object a datetime
    df['release_date'] = pd.to_datetime(df['release_date'], format='%Y-%m-%d', errors='coerce') # Se reemplaza las fechas dejando de lado los errores
    # Crear la columna release_month donde se extraerá el mes de la fecha de estreno.
    df['release_month'] = df['release_date'].apply(lambda x: x.month if x is not pd.NaT else None)
    df['release_month'] = df['release_month'].fillna(0).astype(int)
    meses = dict(enumerate(calendar.month_name))
    df['release_month'] = df['release_month'].map(meses)
    #meses = { i+1: calendar.month_name[i+1] for i in range(12) }
    #meses
    cantidad = df[df["release_month"] == mes]["release_month"].count()
    #print(cantidad)
    return f'Mes: {mes}, Cantidad: {cantidad}'
# Ejemplo de consulta testeada en deta: https://qlprmb.deta.dev/peliculas_mes/?mes=octubre

peliculas_mes('octubre')

# Consulta 2: Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron ese dia (de la semana, en str, ejemplo 'lunes') historicamente, return {'dia':dia, 'cantidad':respuesta}
@app.get("/peliculas_dia/")
def peliculas_dia(dia:str):
    # Convertir la columna "release_date" de object a datetime
    df['release_date'] = pd.to_datetime(df['release_date'], format='%Y-%m-%d', errors='coerce') # Se reemplaza las fechas dejando de lado los errores
    df["release_day"] = df['release_date'].dt.strftime('%A').apply(lambda x: x if type(x) != float else x)
    df["release_day"]
    respuesta = df[df["release_day"] == dia]["release_day"].count()
    return f'Día: {dia}, Cantidad: {respuesta}'

# Consulta 3: Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio, return {'franquicia':franquicia, 'cantidad':respuesta, 'ganancia_total':respuesta, 'ganancia_promedio':respuesta}
@app.get("/franquicia/")
def franquicia(franquicia:str):
    # Filtramos las filas que pertenecen a la franquicia deseada y contamos cuántas filas hay en el resultado filtrado.
    cantidad = df[df['name'] == franquicia].shape[0]
    
    df_franquicia = df[df['name'] == franquicia] # Filtra la franquicia solicitada

    # Calculamos la ganancia total
    gananciaTotal = (df_franquicia['revenue'] - df_franquicia['budget']).sum()
    gananciaPromedio = (df_franquicia['revenue'] - df_franquicia['budget'] / df_franquicia['budget']).mean()

    return f'Franquicia: {franquicia}, Cantidad: {cantidad}, Ganancia Total: {gananciaTotal}, Ganancia Promedio: {gananciaPromedio}'

# Consulta 4: Ingresas el pais, retornando la cantidad de peliculas producidas en el mismo, return {'pais':pais, 'cantidad':respuesta}
@app.get("/peliculas_pais/")
def peliculas_pais(pais:str):
    mask = df['production_countries'].str.join(',').str.contains(pais, na=False)
   
    can = mask.count()
    # cantidad = df[mask]['title'].count()

    return f'pais: {pais}, cantidad:{can}'

# Consulta 5: Ingresas la productora, retornando la ganancia total y la cantidad de peliculas que produjeron, return {'productora':productora, 'ganancia_total':respuesta, 'cantidad':respuesta}
'''@app.get("/productoras/")
def productoras(productora:str):
    #df['production_companies'] = df['production_companies'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df['production_companies']
    conteo = df['production_companies'].apply(lambda x: x.count(productora) if x is not None else 0).sum()
        #print(f'La cadena "{productora}")# aparece {conteo} veces en la lista.')
    ganancia_total = df['revenue'].sum() - df['budget'].sum()
    print("Hola")
    return {'productora':productora, 'ganancia_total':ganancia_total, 'cantidad':conteo}

#productoras('Warner Bros.')'''
# Consulta 6: Ingresas la pelicula, retornando la inversion, la ganancia, el retorno y el año en el que se lanzo, return {'pelicula':pelicula, 'inversion':respuesta, 'ganacia':respuesta,'retorno':respuesta, 'anio':respuesta}
@app.get("/retorno/")
def retorno(pelicula:str):
    pelicula_data = df[df['title'] == pelicula]
    if len(pelicula_data) == 0:
        return f"No se encontró la película {pelicula}"
    inversion = pelicula_data['budget'].iloc[0]
    ganancia = pelicula_data['revenue'].iloc[0] - inversion
    retorno = ganancia / inversion if inversion > 0 else 0
    anio = int(pelicula_data['release_year'])
    return {'pelicula': pelicula, 'inversion': inversion, 'ganancia': ganancia, 'retorno': retorno, 'anio': anio}