# astrobarndoor
Software for a raspberry pi pico used in a project to make a barn-door camera mount for sidereal rate tracking of the night sky.

This uses a "Iverntech NEMA 17 Stepper Motor with Integrated 300mm T8 Lead Screw".

As the motor turns the lead screw, a brass threaded nut moves along the screw, which in turn opens the barn door.

To avoid the need of a bent lead screw, both motor and the threaded nut housing are connected to the barn door by hinges.

The motor has 200 steps per revolution, but by using the DRV8825 driver, which can provide 1/32 microstepping, the motor can be moved slow enough to avoid the need for any gears.


