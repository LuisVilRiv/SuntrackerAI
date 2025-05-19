# Importación de librerías necesarias
import RPi.GPIO as GPIO            # Control de pines GPIO de la Raspberry Pi
import board                      # Definición de pines de la placa
import busio                      # Comunicación I²C
import adafruit_ads1x15.ads1115 as ADS    # Driver del ADC ADS1115
from adafruit_ads1x15.analog_in import AnalogIn  # Lectura de canales analógicos
import tensorflow as tf           # TensorFlow para modelo de IA
import numpy as np                # Numpy para manejo de arrays
import time                       # Gestión de tiempos y delays

# Configuración de pines del motor DC
MOTOR_IN1, MOTOR_IN2, MOTOR_EN = 18, 23, 24
GPIO.setmode(GPIO.BCM)           # Modo de numeración Broadcom
GPIO.setup([MOTOR_IN1, MOTOR_IN2, MOTOR_EN], GPIO.OUT)
pwm = GPIO.PWM(MOTOR_EN, 1000)   # PWM a 1 kHz
pwm.start(0)                     # Iniciar con 0% de ciclo de trabajo

# Inicialización del ADC ADS1115 para LDRs
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ldr1 = AnalogIn(ads, ADS.P0)     # Sensor LDR en canal P0
ldr2 = AnalogIn(ads, ADS.P1)     # Sensor LDR en canal P1

# Clase que encapsula el tracker solar y su modelo de IA
class SolarTracker(tf.Module):
    def __init__(self):
        self.angle = 90  # Ángulo inicial (grado medio)
        # Modelo secuencial simple: 4 entradas → 8 neuronas → 3 salidas (mover izquierda/derecha/reposo)
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(8, activation='relu', input_shape=(4,)),
            tf.keras.layers.Dense(3, activation='softmax')
        ])

    def predict(self, ldr_values):
        """Inferencia directa con el modelo Keras (no usado, pero disponible)"""
        input_data = np.array([ldr_values])
        return self.model.predict(input_data)[0]

# Instancia del tracker y conversión a TFLite
tracker = SolarTracker()
converter = tf.lite.TFLiteConverter.from_keras_model(tracker.model)
tflite_model = converter.convert()
interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def actualizar_posicion(direccion):
    """Ajusta el atributo angle según la dirección recibida"""
    if direccion == 1 and tracker.angle < 180:
        tracker.angle += 1
    elif direccion == 2 and tracker.angle > 0:
        tracker.angle -= 1

def control_motor(direccion, velocidad=50):
    """Activa el motor en la dirección y velocidad indicadas"""
    pwm.ChangeDutyCycle(velocidad)
    if direccion == 1:
        GPIO.output(MOTOR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
    elif direccion == 2:
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.HIGH)

def decidir_movimiento(ldr1_val, ldr2_val):
    """
    Decide si mover el panel basándose en:
      1) Diferencia de iluminación (umbral 10%)
      2) Inferencia con modelo TFLite si la diferencia es significativa
    """
    diferencia = abs(ldr1_val - ldr2_val) / max(ldr1_val, ldr2_val)
    # Caso de iluminación casi igual: reposicionar hacia 90°
    if diferencia < 0.1:
        if tracker.angle > 90:
            return 2, (tracker.angle - 90) * 2
        elif tracker.angle < 90:
            return 1, (90 - tracker.angle) * 2

    # Inferencia TFLite: prepara el tensor de entrada y ejecuta
    input_data = np.array([[ldr1_val, ldr2_val, tracker.angle, diferencia]], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])
    # Devuelve la dirección con mayor probabilidad y velocidad fija
    return np.argmax(prediction[0]), 50

def recolectar_datos(val1, val2, direccion):
    """Registra timestamp, lecturas LDR, ángulo y acción en CSV para entrenamiento"""
    with open('data.csv', 'a') as f:
        f.write(f"{time.time()},{val1},{val2},{tracker.angle},{direccion}\n")

def entrenar_modelo():
    """Reentrena el modelo Keras con los datos históricos almacenados"""
    data = np.loadtxt('data.csv', delimiter=',')
    # Features: columnas 1 a n-1, Label: última columna
    tracker.model.fit(data[:, 1:-1], data[:, -1], epochs=10)

def main():
    """Bucle principal: lee sensores, decide, acciona motor y registra datos"""
    while True:
        v1, v2 = ldr1.value, ldr2.value
        direccion, velocidad = decidir_movimiento(v1, v2)
        control_motor(direccion, velocidad)
        actualizar_posicion(direccion)
        print(f"Posición: {tracker.angle}°")
        recolectar_datos(v1, v2, direccion)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
