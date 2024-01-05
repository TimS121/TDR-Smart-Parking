import RPi.GPIO as GPIO  # Library to control GPIO pins on Raspberry Pi
import paho.mqtt.client as paho  # Library for MQTT client
import time  # Library for time-related tasks
import ssl  # Library for handling SSL/TLS connections

# Set GPIO mode to use physical pin numbering and disable warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Define GPIO pins for sensors
slot1_Sensor = 13
slot2_Sensor = 15
slot3_Sensor = 29
slot4_Sensor = 31

# Setup GPIO pins as input for each sensor
GPIO.setup(slot1_Sensor, GPIO.IN)
GPIO.setup(slot2_Sensor, GPIO.IN)
GPIO.setup(slot3_Sensor, GPIO.IN)
GPIO.setup(slot4_Sensor, GPIO.IN)

# GPIO setup for SG90 Servo Motor
servo_pin = 33  # Define GPIO pin for servo motor
GPIO.setup(servo_pin, GPIO.OUT)  # Set servo pin as an output

# Initialize PWM (Pulse Width Modulation) on the servo pin with 50Hz frequency
servo = GPIO.PWM(servo_pin, 50)
servo.start(0)  # Start PWM with 0% duty cycle

def set_servo_angle(angle):
    """ Function to set the angle of the servo motor """
    duty_cycle = (angle / 18) + 2  # Calculate duty cycle for given angle
    GPIO.output(servo_pin, True)  # Enable the GPIO pin
    servo.ChangeDutyCycle(duty_cycle)  # Set the duty cycle
    time.sleep(1)  # Wait for the servo to move
    GPIO.output(servo_pin, False)  # Disable the GPIO pin
    servo.ChangeDutyCycle(0)  # Reset the duty cycle

# MQTT Client setup functions
def on_connect(client, userdata, flags, rc):
    """ Callback function for when the client connects to the broker """
    print("Connected with result code " + str(rc))
    # Subscribe to topics once connected
    if rc == 0:
        client.subscribe("Fan")
        client.subscribe("servo/control")

def on_message(client, userdata, msg):
    """ Callback function for when a message is received """
    if msg.topic == "servo/control":
        message = msg.payload.decode()
        if message == "ON":
            set_servo_angle(90)  # Set servo to 90 degrees
        elif message == "OFF":
            set_servo_angle(0)   # Set servo to 0 degrees

def on_publish(client, userdata, mid):
    """ Callback function for when a message is published """
    print("mid: " + str(mid))

# Initialize MQTT client
mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_publish = on_publish

# MQTT broker credentials 
mqtt_username = ""
mqtt_password = ""
mqttc.username_pw_set(mqtt_username, mqtt_password)

# Set TLS/SSL context for secure connection to MQTT broker
mqttc.tls_set_context(ssl.create_default_context())

# Connect to MQTT broker
broker_address = ""
port = 8883  # MQTT over TLS/SSL port
try:
    mqttc.connect(broker_address, port)
except Exception as e:
    print("Error connecting to MQTT broker: ", e)
    exit(1)

# Main loop
while True:
    mqttc.loop_start()  # Start network loop for asynchronous processing
    # Read status from each sensor
    slot1_status = GPIO.input(slot1_Sensor)
    slot2_status = GPIO.input(slot2_Sensor)
    slot3_status = GPIO.input(slot3_Sensor)
    slot4_status = GPIO.input(slot4_Sensor)
    time.sleep(0.2)

    # Publish status for each slot
    mqttc.publish("slot1", "1" if not slot1_status else "0")
    mqttc.publish("slot2", "1" if not slot2_status else "0")
    mqttc.publish("slot3", "1" if not slot3_status else "0")
    mqttc.publish("slot4", "1" if not slot4_status else "0")
    time.sleep(0.2)
    
    mqttc.loop_stop()  # Stop network loop
