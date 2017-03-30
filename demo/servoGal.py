import time, logging, sys
log = logging.getLogger("servoGal")
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


def main(argv):

    log.info("Mode: %s" % argv[1] )
    from wiringx86 import GPIOGalileo as GPIO
    gpio = GPIO(debug=True)
    pin = 13
    state = gpio.HIGH
    servo_pin = 9
    gpio.pinMode(pin, gpio.OUTPUT)
    gpio.pinMode(servo_pin, gpio.PWM)

    #TODO
    pwm_period = 3000000
    gpio.setPWMPeriod(servo_pin, pwm_period)

    gpio.digitalWrite(pin, gpio.HIGH)

    adc_l = 14 # A0

    gpio.pinMode(adc_l, gpio.ANALOG_INPUT)

    # With a 100 Ohm resistor and 3.3K resistor and 10k Pot the min max vals
    # read from the ADC are around
    # TODO try real values with my 25k pot
    min_val = 204
    max_val = 994
    val_range = float(max_val - min_val)

    min_pulse = 500000
    max_pulse = 2500000
    pulse_range = float(max_pulse - min_pulse)

    print 'Analog reading from pin %d now ...' % adc_l

    try:
        old_pulse_length = 0

        while(True):
            value_l = gpio.analogRead(adc_l)

            print value_l
            print ""

            norm_val = float(value_l - min_val) / val_range
            norm_val = min( max(0.0, norm_val), 1.0)

            print norm_val

            pulse_length = (norm_val * pulse_range) + min_pulse
            pulse_pct = float(abs(pulse_length - old_pulse_length)) / \
            float(pulse_length)

            if pulse_pct > 0.02:
                gpio.analogWrite(servo_pin, \
                int(float(pulse_length) / pwm_period * 255.0))
            else:
                pass

            old_pulse_length = pulse_length

            time.sleep(0.2)

    except KeyboardInterrupt:
        gpio.analogWrite(servo_pin, 0)

        gpi.digitalWrite(pin, gpio.LOW)

        print '\Cleaning up....'
        gpio.cleanup()


if __name__ == "__main__":
    main(sys.argv)
