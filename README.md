# Proyecto Solar Monitoring

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Este repositorio contiene dos herramientas para optimizar la operación de instalaciones solares fotovoltaicas:

1. **Informe de Mantenimiento Meteorológico**
   Obtiene datos de pronóstico diario de AEMET para Granada, evalúa riesgos asociados (temperatura, precipitación, viento, radiación UV) y genera un informe automático por correo.

2. **Tracker Solar Automático**
   Sistema embebido en Raspberry Pi que, mediante dos sensores LDR y un ADC ADS1115, orienta paneles solares hacia la luz óptima usando un motor DC y un modelo TFLite.

---

## Índice

* [Requisitos](#requisitos)
* [Instalación](#instalación)
* [Configuración](#configuración)
* [Uso](#uso)

  * [Informe de Mantenimiento](#informe-de-mantenimiento)
  * [Sistema Tracker Solar](#sistema-tracker-solar)
* [Ejemplos de Salida](#ejemplos-de-salida)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Licencia](#licencia)

---

## Requisitos

* **Hardware**

  * (Solo Tracker) Raspberry Pi con pines GPIO libres.
  * ADC ADS1115 y dos LDR (Light Dependent Resistors).
  * Motor DC + driver (p. ej. puente H) compatible con PWM.

* **Software**

  * Python 3.7+
  * Paquetes Python:

    ```bash
    pip install requests python-dotenv adafruit-circuitpython-ads1x15 RPi.GPIO tensorflow numpy
    ```

* **APIs**

  * Clave AEMET: para acceso a pronóstico meteorológico.
  * Clave Poste.io: para envío de emails.

---

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu_usuario/solar-monitoring.git
cd solar-monitoring

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración

1. **Variables de entorno**
   En la raíz, crea un archivo `.env` con:

   ```env
   AEMET_API_KEY=TU_API_KEY_AEMET
   POSTE_API_KEY=TU_API_KEY_POSTE
   ```

2. **Conexiones eléctricas**

   * **ADS1115 ↔ Raspberry Pi**:

     * SDA → GPIO2 (SDA)
     * SCL → GPIO3 (SCL)
     * VCC → 3.3 V
     * GND → GND

   * **Sensores LDR**:

     * LDR1 → ADS1115 canal P0 (serie con resistencia pull-down de 10 kΩ a GND)
     * LDR2 → ADS1115 canal P1 (serie con resistencia pull-down similar)

   * **Motor DC**:

     * IN1 → GPIO18
     * IN2 → GPIO23
     * EN  → GPIO24 (PWM)

---

## Uso

### Informe de Mantenimiento

1. Ajusta `DESTINATARIO` y `CONCEPTO` en `informe_mantenimiento.py` (o via variables de entorno en el script).
2. Ejecuta:

   ```bash
   python informe_mantenimiento.py
   ```
3. El script mostrará por consola:

   * Fecha y hora de análisis.
   * Nivel de riesgo (Bajo, Moderado, Alto, Crítico).
   * Parámetros medidos y recomendaciones.

   Y enviará un email con el informe en HTML.

### Sistema Tracker Solar

1. Verifica las conexiones GPIO y sensores.
2. Ejecuta el tracker:

   ```bash
   python tracker_solar.py
   ```
3. En pantalla verás:

   * Ángulo actual del panel.
   * Acción tomada (girar izquierda/derecha/esperar).

Para recopilar datos y reentrenar el modelo TFLite:

```bash
# Ejecuta el tracker durante al menos 30 min.
# Luego, reentrena:
python -c "from tracker_solar import entrenar_modelo; entrenar_modelo()"
```

---

## Ejemplos de Salida

**Informe de Mantenimiento**:

```json
{
  "fecha_analisis": "2025-05-19T10:00:00",
  "nivel_riesgo": "Moderado",
  "parametros": {
    "temperatura_max": 37,
    "precipitacion": 10,
    "viento_velocidad": 15,
    "radiacion_uv": 9
  },
  "recomendaciones": [
    "Posible limpieza natural de paneles",
    "Verificar degradación materiales"
  ]
}
```

**Tracker Solar (consola)**:

```
Posición: 91° → Girando izquierda, PWM=50%
Posición: 90° → En posición óptima, PWM=0%
...
```

---

## Estructura del Proyecto

```
solar-monitoring/
├── datos/                    # Datos históricos (data.csv)
├── informe_mantenimiento.py  # Script de análisis y envío de email
├── tracker_solar.py          # Lógica del tracker y recopilación de datos
├── requirements.txt          # Dependencias Python
├── README.md                 # Documentación (este archivo)
└── LICENSE                   # Licencia MIT
```

---

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulta `LICENSE` para más detalles.
