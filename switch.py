# Tests if a switch is activated

from machine import Pin

import time


# if switch is open for two intervals 20 ms apart, switch is off
# if switch is closed for two intervals 20 ms apart, switch is on, but after being read stays off, until reset by an 'off' period


class Switch():

    def __init__(self, pin):
        # note, using pull up, so value and state are 1 for open, 0 for closed
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._value = self.pin.value()
        self._count = 0
        self._state = 1   # state is 1 for switch open
        self._first = time.ticks_ms()
        self._reset = False


    def _getstate(self):
        "Reads switch state, but once read, sets state to 1 until reset becomes False"
        if self._reset:
            # reset is True, so even if switch is closed, this returns 1
            # which indicates open
            return 1
        # reset is not set
        if not self._state:
            # state is 0, switch closed
            # 0 will be returned, but now reset will be set to True
            self._reset = True
            return 0
        # state is 1
        return 1


    def _check(self):
        "Monitor the switch"
   
        # if count is zero, record pin value, and start timer
        if not self._count:
            # state cannot change yet, as this is only first sample
            # of the pin. Record current value of pin, and the time
            self._value = self.pin.value()
            self._first = time.ticks_ms()
            self._count = 1
            return

        # self._count must be equal to 1, check if more than 20ms has passed since first check
        # if not - just return
        now = time.ticks_ms()   
        delta = time.ticks_diff(now, self._first) # compute time difference
        if delta < 20:
            # less than 20ms from last check, so ignore pin, go back to main loop
            return

        # so 20ms or more has passed since previous check, compare current value with previous
        newval = self.pin.value()
        if newval == self._value:
            # pin has been this value for 20ms, so this is the debounced value, and state can be updated
            self._state = self._value
            if self._state:
                # as state is now 1 (switch open), the reset can be set to False
                if self._reset:
                    self._reset = False
            # state is set, so for a change of state, restart with count 0
            self._count = 0
            return

        # newval is different to old value, could have just toggled, so state cannot be changed until
        # debounce period has passed
        self._value = newval
        self._first = now
        # and count remains at 1


    def pressed(self):
        "Called at frequent intervals from the main loop, returns True if the switch is closed"
        # monitor the switch
        self._check()
        state = self._getstate()
        if state:
            # state is 1 if switch is open
            return False
        # switch is closed
        return True

