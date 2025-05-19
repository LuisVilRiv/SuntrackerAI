# Importación de librerías y configuración GPIO
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import tensorflow as tf
import numpy as np
import time

# Pines del motor
MOTOR_IN1, MOTOR_IN2, MOTOR_EN = 18, 23, 24
GPIO.setmode(GPIO.BCM)
GPIO.setup([MOTOR_IN1, MOTOR_IN2, MOTOR_EN], GPIO.OUT)
pwm = GPIO.PWM(MOTOR_EN, 1000)
pwm.start(0)

# Configuración ADC ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ldr1, ldr2 = AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1)

# Clase del tracker solar con modelo TF
class SolarTracker(tf.Module):
    def __init__(self):
        self.angle = 90  # Posición inicial
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(8, activation='relu', input_shape=(4,)),
            tf.keras.layers.Dense(3, activation='softmax')
        ])

    def predict(self, ldr_values):
        # Preprocesado de datos para el modelo
        input_data = np.array([ldr_values])
        return self.model.predict(input_data)[0]

tracker = SolarTracker()

# Conversión a TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(tracker.model)
tflite_model = converter.convert()

interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def actualizar_posicion(direccion):
    # Lógica de actualización angular
    if direccion == 1 and tracker.angle < 180:
        tracker.angle += 1
    elif direccion == 2 and tracker.angle > 0:
        tracker.angle -= 1

def control_motor(direccion, velocidad=50):
    # Control PWM y direcciones
    pwm.ChangeDutyCycle(velocidad)
    if direccion == 1:
        GPIO.output(MOTOR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_IN2, GPIO.LOW)
    elif direccion == 2:
        GPIO.output(MOTOR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_IN2, GPIO.HIGH)

def decidir_movimiento(ldr1_val, ldr2_val):
    # Lógica de umbral para luz similar
    diferencia = abs(ldr1_val - ldr2_val) / max(ldr1_val, ldr2_val)
    if diferencia < 0.1:
        if tracker.angle > 90:
            return 2, (tracker.angle - 90) * 2
        elif tracker.angle < 90:
            return 1, (90 - tracker.angle) * 2

    # Inferencia con modelo TFLite
    input_data = np.array([[ldr1_val, ldr2_val, tracker.angle, diferencia]], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])
    return np.argmax(prediction[0]), 50

def main():
    while True:
        val1, val2 = ldr1.value, ldr2.value  # Lectura sensores
        direccion, velocidad = decidir_movimiento(val1, val2)
        control_motor(direccion, velocidad)  # Accionar motor
        actualizar_posicion(direccion)      # Actualizar ángulo
        print(f"Posición: {tracker.angle}°")  # Feedback
        recolectar_datos(val1, val2, direccion)
        time.sleep(0.1)

def recolectar_datos(val1, val2, direccion):
    # Guardar: timestamp, valores LDR, posición, acción
    with open('data.csv', 'a') as f:
        f.write(f"{time.time()},{val1},{val2},{tracker.angle},{direccion}\n")

def entrenar_modelo():
    # Cargar datos históricos y reentrenar
    data = np.loadtxt('data.csv', delimiter=',')
    tracker.model.fit(data[:, 1:-1], data[:, -1], epochs=10)

if __name__ == "__main__":
    main()
