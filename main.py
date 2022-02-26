from machine import Pin, PWM

import time

import motions, switch

# set ledup, initially set to 1 to show power on,
# motor stopped and direction up
ledup = Pin(14, Pin.OUT)  # future will be pin 28
ledup.value(1)

leddown = Pin(15, Pin.OUT)
leddown.value(0)

# DRV8825 control

# high to disable, 0 to enable
# initially start with disabled
enable = Pin(26, Pin.OUT)
enable.value(1)

# limit switch, stop motion if closed
limit_switch = Pin(0, Pin.IN, Pin.PULL_UP)

# all modes 0 is full step
# all modes 1 is 1/32 step

mode0 = Pin(22, Pin.OUT)
mode0.value(1)

mode1 = Pin(21, Pin.OUT)
mode1.value(1)

mode2 = Pin(20, Pin.OUT)
mode2.value(1)

# reset 0 to reset, needs to be 1 to run
reset = Pin(19, Pin.OUT)
reset.value(1)

# sleep 0 to set low power sleep mode, needs to be 1 to run
sleep = Pin(18, Pin.OUT)
# initially set to sleep, so the motor starts in stopped mode
sleep.value(0)

step = PWM(Pin(17))
step.freq(12)    # 12 for slow, 500 for fast
step.duty_u16(32768)
# 65536 is full on
# 32768 is 50%

# 0 is down, 1 is up
direction = Pin(16, Pin.OUT)
direction.value(1)

# set up the switch inputs, the switch.Switch class sets
# the given pin as an input and the method Switch.pressed() returns
# True if the switch is pressed. The class takes care of debounce and
# only returns True on the initial press, i.e. subsequent calls to
# pressed do not return True if the switch is held closed and not released.

# stop switch
stopswitch = switch.Switch(5)

# direction switch
dswitch = switch.Switch(7)

# fast switch
fastswitch = switch.Switch(9)

# slowswitch
slowswitch = switch.Switch(10)

# enable the controller
enable.value(0)

# initial condition, start with motor stopped
status = 0       # status = 0 for stopped, 1 for slow, 2 for fast

# start_time and count are used to control LED flashes,
# when running slow the led only flashes 3 times, then goes off
# so count is used to count the number of flashes
start_time = time.ticks_ms() # get millisecond counter
count = 0

while True:

    now = time.ticks_ms()

    if motions.check_limit(step, sleep, direction, limit_switch):
        # limit switch activated, rotation stopped
        status = 0
        count = 0

    ########################################################
    # check other switch inputs
    # and call motions functions slow, stop, fast, direction
    ########################################################

    # check direction switch
    if dswitch.pressed():
        # toggle direction
        if direction.value():
            status = motions.direction(0, status, step, sleep, direction, limit_switch)
        else:
            status = motions.direction(1, status, step, sleep, direction, limit_switch)
        # after any button pressed, set count to zero to ensure three flashes if motor set to slow
        count = 0

    if fastswitch.pressed():
        # set the motor at the fast turning rate
        status = motions.fast(status, step, sleep, direction, limit_switch)
        count = 0

    if slowswitch.pressed():
        # set the motor at the slow turning rate
        status = motions.slow(status, step, sleep, direction, limit_switch)
        count = 0

    if stopswitch.pressed():
        # stop the motor
        status = motions.stop(status, step, sleep, direction, limit_switch)
        count = 0


    ########################################################
    #
    # handle led indications depending on status
    # led on = stopped
    # led continuous flash = fast motion
    # led 3 rapid flashes, then off = sideral speed
    #
    ########################################################

    if not status:
        # stopped, so ensure led is on
        motions.set_led(True, ledup, leddown, direction)
        continue

    delta = time.ticks_diff(now, start_time) # compute time difference
    if status == 1:
        # running slow, so flash three times rapidly, then stop led
        if count < 3:
            if delta < 200:
                # if not already on, turn on led
                motions.set_led(True, ledup, leddown, direction)
            elif delta < 400:
                # if not already off, turn off led, and keep a count of every on to off transition
                if ledup.value() or leddown.value():
                    # increment count on every on to off transition
                    count += 1
                motions.set_led(False, ledup, leddown, direction)
            else:
                # greater than 400 msec, so start timer again
                start_time = now

    if status == 2:
        # running fast, so flash led continuously
        if delta < 500:
            motions.set_led(True, ledup, leddown, direction)
        elif delta < 1000:
            motions.set_led(False, ledup, leddown, direction)
        else:
            start_time = now   
        
        




