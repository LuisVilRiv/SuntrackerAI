import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración global de claves y destinatario
AEMET_API_KEY  = os.getenv('AEMET_API_KEY', 'eyJhbGci...')   # Clave API AEMET
POSTE_API_KEY  = os.getenv('POSTE_API_KEY', 'tu_poste_key')  # Clave API Poste.io
DESTINATARIO   = "tucorreo@gmail.com"                       # Email receptor
CONCEPTO       = "Informe de mantenimiento paneles solares - Granada"

def obtener_datos_aemet():
    """Obtiene datos de pronóstico diario para Granada desde la API AEMET."""
    url = (
        f"https://opendata.aemet.es/opendata/api/prediccion/"
        f"especifica/municipio/diaria/18087?api_key={AEMET_API_KEY}"
    )
    try:
        # 1. Solicitar URL de datos
        response = requests.get(url)
        response.raise_for_status()
        datos_url = response.json()['datos']

        # 2. Descarga de datos reales de pronóstico
        datos_response = requests.get(datos_url)
        datos_response.raise_for_status()
        return datos_response.json()

    except Exception as e:
        raise Exception(f"Error API AEMET: {str(e)}")

def analizar_riesgo(datos):
    """Evalúa condiciones meteorológicas y devuelve nivel de riesgo y recomendaciones."""
    try:
        # Extraer pronóstico del primer día
        dia = datos[0]['prediccion']['dia'][0]
        parametros = {
            'temperatura_max': dia['temperatura']['maxima'],        # °C
            'precipitacion':    dia['probPrecipitacion'][0]['value'],  # %
            'viento_velocidad': dia['viento'][0]['velocidad'],     # km/h
            'radiacion_uv':     dia['uvMax']                       # Índice UV
        }

        # Inicializar variables de puntuación
        riesgo = 0
        recomendaciones = []

        # Evaluar temperatura
        if parametros['temperatura_max'] > 40:
            riesgo += 2
        elif parametros['temperatura_max'] > 35:
            riesgo += 1

        # Evaluar precipitación
        if parametros['precipitacion'] > 30:
            riesgo += 2
            recomendaciones.append("Posible limpieza natural de paneles")
        elif parametros['precipitacion'] > 5:
            riesgo += 1

        # Evaluar viento
        if parametros['viento_velocidad'] > 40:
            riesgo += 2
            recomendaciones.append("Verificar anclajes y estructuras")
        elif parametros['viento_velocidad'] > 25:
            riesgo += 1

        # Evaluar radiación UV
        if parametros['radiacion_uv'] > 8:
            riesgo += 1
            recomendaciones.append("Verificar degradación de materiales")

        # Determinar nivel de riesgo a partir de la puntuación
        niveles_riesgo = [
            (2,         "Bajo"),
            (4,         "Moderado"),
            (6,         "Alto"),
            (float('inf'), "Crítico"),
        ]
        nivel = next(label for lim, label in niveles_riesgo if riesgo <= lim)

        return {
            'fecha_analisis': datetime.now().isoformat(),  # Marca temporal ISO
            'nivel_riesgo':   nivel,
            'parametros':     parametros,
            'recomendaciones': recomendaciones
        }

    except KeyError as e:
        raise Exception(f"Datos API incompletos: {str(e)}")

def generar_cuerpo_email(data):
    """Construye el cuerpo HTML del email con resultados del análisis."""
    return f"""
    <h1>Informe de mantenimiento</h1>
    <p><strong>Nivel de riesgo:</strong> {data['nivel_riesgo']}</p>
    <h3>Recomendaciones:</h3>
    <ul>
        {"".join(f"<li>{r}</li>" for r in data['recomendaciones'])}
    </ul>
    <pre>{json.dumps(data, indent=2)}</pre>
    """

def enviar_por_poste(data_json):
    """Envía el informe por email usando la API de Poste.io."""
    url = "http://localhost:8080/api/v1/send"
    headers = {
        "Content-Type":     "application/json",
        "X-Postie-API-Key": POSTE_API_KEY
    }
    payload = {
        "to":      DESTINATARIO,
        "subject": CONCEPTO,
        "body":    generar_cuerpo_email(data_json)
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        raise Exception(f"Error enviando email: {str(e)}")

def main():
    """Orquestador principal: obtiene datos, analiza riesgo y envía informe."""
    try:
        datos_crudos    = obtener_datos_aemet()      # Paso 1: datos meteorológicos
        analisis       = analizar_riesgo(datos_crudos)  # Paso 2: análisis de riesgo
        informe_final  = {
            "destinatario": DESTINATARIO,
            "concepto":     CONCEPTO,
            **analisis
        }

        # Paso 3: envío y log de resultado
        if enviar_por_poste(informe_final):
            print("Informe generado y enviado:")
            print(json.dumps(informe_final, indent=2))

    except Exception as e:
        print(f"Error crítico: {str(e)}")

if __name__ == "__main__":
    main()
