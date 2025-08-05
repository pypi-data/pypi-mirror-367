import RPi.GPIO as GPIO
import time

class WLGamepad:
    # define name of buttons
    BUTTONS = [
        "Select", "L3", "R3", "Start",
        "Up", "Right", "Down", "Left",
        "L2", "R2", "L1", "R1",
        "Triangle", "Circle", "Cross", "Square"
    ]

    def __init__(self, ATT = 17, CLK = 18 , CMD = 27 , DATA = 22 ):
        """
        method to initilize controller with default pins
        """
        # set pins with the communication
        self.ATT = ATT
        self.CLK = CLK
        self.CMD = CMD
        self.DATA = DATA

        # initilize pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ATT, GPIO.OUT, initial=1)
        GPIO.setup(CLK, GPIO.OUT, initial=1)
        GPIO.setup(CMD, GPIO.OUT, initial=1)
        GPIO.setup(DATA, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _transfer(self,data):
        """
        method to transfer data to controller
        """
        value = 0
        for i in range(8):
            GPIO.output(self.CMD, (data >> i) & 1)
            GPIO.output(self.CLK, 0)
            if GPIO.input(self.DATA) == 1:
                value |= (1 << i)
            GPIO.output(self.CLK, 1)
        return value
    
    def _enter_config_mode(self):
        """
        method to enter configuration mode of controller
        """
        GPIO.output(self.ATT, 0)
        for b in [0x01, 0x43, 0x00, 0x01, 0x00]:
            self._transfer(b)
        GPIO.output(self.ATT, 1)
        time.sleep(0.01)
    
    def _enable_analog(self):
        """
        method to enable analog keys (joysticks)
        """
        GPIO.output(self.ATT, 0)
        for b in [0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00]:
            self._transfer(b)
        GPIO.output(self.ATT, 1)
        time.sleep(0.01)
    
    def _exit_config_mode(self):
        """
        method to exit configuration mode of controller
        """
        GPIO.output(self.ATT, 0)
        for b in [0x01, 0x43, 0x00, 0x00, 0x5A]:
            self._transfer(b)
        GPIO.output(self.ATT, 1)
        time.sleep(0.05)

    def read_controller(self):
        """
        method which returns all controller values
        """
        # setup reading of controller
        GPIO.output(self.ATT, 0)
        resp = [self._transfer(0x01), self._transfer(0x42), self._transfer(0x00)]
        btn_low = self._transfer(0x00)
        btn_high = self._transfer(0x00)
        axes = [self._transfer(0x00) for _ in range(4)]
        GPIO.output(self.ATT, 1)

        # read which buttons are pressed
        buttons = []
        btn_word = (btn_high << 8) | btn_low
        for i in range(16):
            if not (btn_word & (1 << i)):
                buttons.append(self.BUTTONS[i])

        return {
            "id": resp[1], # Controller ID
            "buttons": buttons, # pressed buttons
            "sticks": {
                "LX": axes[2],
                "LY": axes[3],
                "RX": axes[0],
                "RY": axes[1] # analog values 0-255 of joystick axes
            },
            "raw": [f"{b:02X}" for b in resp + [btn_low, btn_high] + axes] # raw values
        }

    def setup_controller(self):
        """
        method to setup communication with controller
        """
        self._enter_config_mode()
        self._enable_analog()
        self._exit_config_mode()
