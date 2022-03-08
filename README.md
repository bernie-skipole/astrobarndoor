# astrobarndoor
Software for a raspberry pi pico used in a project to make a barn-door camera mount for sidereal rate tracking of the night sky.

This uses an "Iverntech NEMA 17 Stepper Motor with Integrated 150mm T8 Lead Screw".

A brass threaded nut moves along the screw as it is turned, which in turn opens the barn door.

As the integrated lead screw is straight, and cannot follow the arc formed by the leaves of the barn door, both motor and the threaded nut housing are connected to the barn door by hinges.

The motor has 200 steps per revolution, and a single revolution moves the threaded nut by 8mm. By using the DRV8825 driver, which can provide 1/32 microstepping, the motor can be moved slow enough to avoid the need for any gears.

The unit should be fed from a 12 Volt supply, such as a car battery.

A Raspberry Pi pico takes push button inputs, controls two LED's and sends appropriate signals to the DRV8825. The software consists of three micropython files:

main.py

Sets up the pico pins, and runs a loop calling functions depending on inputs.

motions.py

Defines functions which toggle LED's, runs the motor either fast, slow (sidereal) or stop and controls direction.

switch.py

Defines a class, Switch() which is used in the loop to check the state of momentary push buttons, it provides a pressed() method returning True if a button is pressed. It only returns True once per button press, so if called in a loop, will not continuously return True for each pass of the loop.

The pressed method takes care of debounce (the button is checked twice, 20ms apart - so should be called continuosly from a loop), and ensures the momentary button close has to be released before pressed() is reset and will return True again on another button press.

The Switch class takes a GPIO pin number in its initialiser:

myswitch = switch.Switch(5)

while True:

...if myswitch.pressed():

...... do something


The class initialiser sets up the pin as an input with pull up, so the push button switch should connect it to 0V when pressed.

The switches used are:

Fast - runs the motor at a fast rate, for camera positioning

Slow - runs at the tracking sidereal rate

Stop - stops the motor

Direction - toggles the motor direction, Up or Down.

A further switch input is connected to a microswitch which closes as the barn door leaf closes, this stops any further motor motion in the 'Down' direction.

The pico drives two LED's, only one being active at a time, depending on direction, so one LED indicates 'Up' and one 'Down'.

Solid light = Motor stopped

Steady flashing = Motor running fast

Three quick flashes then off = Motor running slow (sidereal)

There could be confusion between motor running slow and no power provided to the unit, however LED off is felt to be best when tracking to avoid any light getting to the camera.


