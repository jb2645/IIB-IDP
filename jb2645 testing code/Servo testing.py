from machine import Pin, PWM
from utime import sleep

def test_servo():
    pwm_pin_no = 15
    servo = PWM(Pin(pwm_pin_no))
    servo.freq(50)  # Can use 50-330Hz, 50Hz is safe default

    # At 50Hz, period = 20ms = 20,000us
    # duty_u16 maps 0-65535 to 0-100% of the period
    # So: duty = (pulse_us / 20000) * 65535

    MIN_DUTY = int((500  / 20000) * 65535)  # 500us  = 1638
    MID_DUTY = int((1500 / 20000) * 65535)  # 1500us = 4915
    MAX_DUTY = int((2500 / 20000) * 65535)  # 2500us = 8191

    step = 20
    duty = MIN_DUTY
    direction = 10

    while True:
        servo.duty_u16(duty)
        
        # Convert back to microseconds for readable output
        pulse_us = (duty / 65535) * 20000
        print(f"Duty: {duty}, Pulse: {pulse_us:.0f}us")

        duty += step * direction
        if duty >= MAX_DUTY:
            duty = MAX_DUTY
            direction = -10
        elif duty <= MIN_DUTY:
            duty = MIN_DUTY
            direction = 10

        sleep(0.05)

if __name__ == "__main__":
    test_servo()