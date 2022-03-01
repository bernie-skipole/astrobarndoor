
import time

def check_limit(step, sleep, direction, mode2, limit_switch):
    "If limit switch tripped, return True, or return False if no limit"
    # limit switch gpio pin is pulled high, and is grounded when the switch is closed
    if limit_switch.value():
        # value high, switch open, no problem
        return False
    # limit switch closed, only allow motion if direction is 1
    if direction.value():
        # direction is up, which is safe, no problem
        return False
    # Limit closed, and direction down, force stop
    mode2.value(1)  # 1/32 microstepping
    step.freq(12)
    sleep.value(0)
    return True


def set_led(on, ledup, leddown, direction):
    """If on is True, turn on led, if False, turn it off"""
    # two led's are available, ledup is active, if the direction of motion is up
    #                          leddown is active if the direction of motion is down
    if on:
        # request a turn on
        if direction.value():
            # going up, so the active led is ledup
            if leddown.value():
                leddown.value(0)  # turn off leddown
            if not ledup.value():
                ledup.value(1)    # turn on ledup
        else:
            # going down, so the active led is leddown
            if ledup.value():
                ledup.value(0)      # turn off ledup
            if not leddown.value():
                leddown.value(1)    # turn on leddown
    else:
        # request a turn off
        if ledup.value():
            ledup.value(0)    # turn off ledup
        if leddown.value():
            leddown.value(0)  # turn off leddown


def slow(status, step, sleep, direction, mode2, limit_switch):  # status = 0 for stopped, 1 for slow, 2 for fast
    "Sets to moving slow, returns new status"
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    # limit switch not set, so continue with setting speed to slow
    # which should result in a return status of 1
    if status == 1:
        # already slow, so no change to speed parameters
        return 1
    if not status:
        # system is asleep, set slow speed and awake
        mode2.value(1)  # 1/32 microstepping
        step.freq(12)
        # come out of sleep
        sleep.value(1)
        return 1
    # status is 2, so freq must be fast (500 1/8 microstepping), alter it to 400, 300, 200, 100, 50
    # then to 1/32 microstepping, frequency 12
    acc_t = 0.05   # each change in speed waits for 0.05 of a second
    step.freq(400)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(300)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(200)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(100)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(50)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    mode2.value(1)  # 1/32 microstepping
    step.freq(12)
    # so now running with a frequency of 12, return status 1
    return 1


def stop(status, step, sleep, direction, mode2, limit_switch):  # status = 0 for stopped, 1 for slow, 2 for fast
    "Sets to stop, returns new status of 0"
    if not status:
        # already stopped
        return 0
    if status == 1:
        # running slow, stop it, no need for deceleration
        sleep.value(0)
        return 0
    # must be running fast, so make it slow, then stop it
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    if slow(status, step, sleep, direction, mode2, limit_switch):
        # now running slow
        time.sleep(0.2)
        sleep.value(0)
    return 0


def fast(status, step, sleep, direction, mode2, limit_switch):  # status = 0 for stopped, 1 for slow, 2 for fast
    "Sets to fast, returns status"
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    # limit switch not set, so continue with setting speed to fast
    # which should result in a return status of 2
    if status == 2:
        # already fast, so no change to speed parameters
        return 2
    if not status:
        # stopped, so wake it up, starting from slow
        mode2.value(1)  # 1/32 microstepping
        step.freq(12)
        # come out of sleep
        sleep.value(1)
        time.sleep(0.2)
        if check_limit(step, sleep, direction, mode2, limit_switch):
            return 0
    # awake, and running slow, so accelerate
    acc_t = 0.05   # each change in speed waits for 0.05 of a second
    mode2.value(0) # 1/8th microstepping
    step.freq(50)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(100)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(200)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(300)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(400)
    time.sleep(acc_t)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    step.freq(500)
    # so now running with a frequency of 500, return status 2
    return 2



def direction(newdirection, status, step, sleep, direction, mode2, limit_switch):
    "Sets direction, returns the status"
    olddirection = direction.value()
    if newdirection == olddirection:
        # no change to direction, so after checking limit switch, return
        if check_limit(step, sleep, direction, mode2, limit_switch):
            return 0
        return status
    if status == 2:
        # going fast, slow down, change direction, speed up
        status = slow(status, step, sleep, direction, mode2, limit_switch)
        direction.value(newdirection)
        return fast(status, step, sleep, direction, mode2, limit_switch)
    # either stopped or slow
    direction.value(newdirection)
    if check_limit(step, sleep, direction, mode2, limit_switch):
        return 0
    return status

