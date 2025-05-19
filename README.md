# Proyecto: Sistema de Monitorización y Control de Paneles Solares

Este repositorio incluye dos componentes principales:

1. **Generación de Informes de Mantenimiento**

   * Script en Python que consume la API de AEMET para obtener el pronóstico meteorológico diario de Granada.
   * Analiza parámetros como temperatura, precipitación, viento y radiación UV para evaluar el nivel de riesgo sobre paneles solares.
   * Envía un informe por correo electrónico usando Poste.io.

2. **Tracker Solar Automatizado**

   * Aplicación en Python para Raspberry Pi con un ADC ADS1115 y dos sensores LDR.
   * Control de motor DC mediante GPIO para orientar los paneles hacia la luz.
   * Incluye un modelo TensorFlow Lite para la toma de decisiones de movimiento.

---

## Índice

* [Requisitos](#requisitos)
* [Instalación](#instalaci%C3%B3n)
* [Configuración](#configuraci%C3%B3n)
* [Uso](#uso)

  * [Informe de Mantenimiento](#informe-de-mantenimiento)
  * [Tracker Solar](#tracker-solar)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Licencia](#licencia)

---

## Requisitos

* Python 3.7+
* Raspberry Pi (para el tracker solar)
* Sensor ADC ADS1115 y dos LDR
* Motor DC con driver compatible (por ejemplo, puente H)
* Credenciales API:

  * AEMET\_API\_KEY
  * POSTE\_API\_KEY

Librerías Python:

```bash
pip install requests python-dotenv adafruit-circuitpython-ads1x15 RPi.GPIO tensorflow numpy
```

---

## Instalación

1. Clona el repositorio:

   ```bash
   ```

git clone [https://github.com/tu\_usuario/solar-monitoring.git](https://github.com/tu_usuario/solar-monitoring.git)
cd solar-monitoring

````
2. Crea un entorno virtual y actívalo:
   ```bash
python3 -m venv venv
source venv/bin/activate
````

3. Instala dependencias:

   ```bash
   ```

pip install -r requirements.txt

````

---

## Configuración

1. Crea un fichero `.env` en la raíz con tus claves:
   ```env
AEMET_API_KEY=tu_api_key_aemet
POSTE_API_KEY=tu_api_key_poste
````

2. Conecta el hardware (solo para el tracker):

   * **ADS1115**: SDA → GPIO2 (SDA), SCL → GPIO3 (SCL), VCC → 3.3V, GND → GND.
   * **LDRs**: Conecta cada LDR a P0 y P1 del ADS1115 con la resistencia de pull-down.
   * **Motor**: IN1 → GPIO18, IN2 → GPIO23, EN → GPIO24 (PWM).

---

## Uso

### Informe de Mantenimiento

1. Define destinatario y asunto en el código o variable de entorno.
2. Ejecuta el script:

   ```bash
   ```

python informe\_mantenimiento.py

````
3. El script mostrará en consola el informe y enviará el correo.

### Tracker Solar

1. Asegúrate de tener las conexiones GPIO y ADC correctamente montadas.  
2. Ejecuta el tracker:
   ```bash
python tracker_solar.py
````

3. El sistema leerá los sensores LDR, decidirá movimiento y ajustará la orientación del panel.

Para recopilar datos en `data.csv` y reentrenar el modelo:

```bash
# Durante la ejecución el archivo data.csv se irá llenando
python -c "from tracker_solar import entrenar_modelo; entrenar_modelo()"
```

---

## Estructura del Proyecto

```plaintext
├── datos/
│   └── data.csv                # Datos recolectados por el tracker
├── informe_mantenimiento.py    # Script de generación y envío de informes
├── tracker_solar.py            # Script del tracker automático
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Esta documentación
```

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
