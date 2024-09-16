from RpiMotorLib import RpiMotorLib
from threading import Thread
from gpiozero import Servo
import RPi.GPIO as GPIO
from time import sleep
import pickle
import math
import os


class Gate(Thread):
    def __init__(self, pin):
        super().__init__()
        self.servo = Servo(pin)
        self.position = 1

    def run(self):
        self.servo.value = self.position
        sleep(1)

class Motor:
    def __init__(self, direction_pin, step_pin, file_path, gate):
        GPIO.setmode(GPIO.BCM)

        self.direction_pin = direction_pin
        self.step_pin = step_pin

        self.stepper_motor = RpiMotorLib.A4988Nema(self.direction_pin, self.step_pin, (-1, -1, -1), "A4988")
        self.stepdelay = .0005

        self.file_path = file_path

        self.gate = gate 
        self.gate.start()

        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as f:
                self.current_bin = pickle.load(f)
        else:
            self.current_bin = 3

    def go(self, dir):
        if dir == 'backward':
            self.stepper_motor.motor_go(False, "Full" , 2550, .0005, False, .05)
        elif dir == 'forward': 
            self.stepper_motor.motor_go(True, "Full" , 2550, .0005, False, .05)

    def go_to_bin(self, bin_num=None, hold=False):
        if 0 <= bin_num <= 4:
            delta = bin_num - self.current_bin
            try:
                if delta:
                    self.stepper_motor.motor_go(math.copysign(1, delta) > 0, "Full" , abs(2550 * delta), .0005, False, .05)
                    self.current_bin = bin_num

                    if not hold:
                        self.gate.servo.value = self.gate.position = -1
                        sleep(1)
                        self.gate.servo.value = self.gate.position = 1
                        sleep(1)

                    with open(self.file_path, "wb") as f:
                        pickle.dump(self.current_bin, f)

            except:
                pass

def test_swap():
    servo = Servo(13)
    while(True):
        servo.min()
        sleep(1)
        servo.max()
        sleep(1)

def test_hold(position):
    servo = Servo(13)
    while(True):
        servo.value = position


if __name__ == '__main__':
    #GPIO.cleanup()
    #test_swap()
    #test_hold(1)
    #GPIO.cleanup()
    gate = Gate(13)
    motor = Motor(direction_pin=17, step_pin=18, file_path="./bin_position.pkl", gate=gate)

    #try:
    #motor.go_to_bin(-1)
    #motor.go_to_bin(4, hold=True)
    motor.go_to_bin(0, hold=True)
    motor.go_to_bin(2)
    #motor.stepper_motor.motor_go(True, "Full" , 2550*2, .0005, False, .05)
    #motor.go_to_bin(1)
    #motor.go_to_bin(2)
    #motor.go_to_bin(3)
    #motor.go_to_bin(2)

    #while(True):
    #    sleep(1)
    pass