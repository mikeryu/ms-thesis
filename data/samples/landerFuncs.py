"""
Project _

Name: Boaty MacBoatface
Instructor: Mike Ryu
Section: __
"""

from math import sqrt

def showWelcome():
    """
    CONTRACT | showWelcome : None -> None
    PURPOSE  | Displays the welcome message for the lunar lander.
    IN/OUTS  | None/str
    EXAMPLE  | N/A
    """
    pass    # delete "pass" once you have real code for this function!

    # print the welcome message


def getFuel():
    """
    CONTRACT | getFuel : None -> int
    PURPOSE  | Prompts the user for a positive integer value and returns it; show error and re-prompt for invalid values.
    IN/OUTS  | int/str  # console I/O, expects integer input and outputs error message if out of bounds.
    EXAMPLE  | N/A
    """
    pass    # delete "pass" once you have real code for this function!

    # prompt user for `fuel` value

    # as long as the answer is negative, display error and re-prompt

    # return the positive `fuel` value


def getAltitude():
    """
    CONTRACT | getAltitude : None -> float
    PURPOSE  | Prompts the user for a real value in [1, 9999]; show error nad re-prompt if value given is out of range.
    IN/OUTS  | float/str  # console I/O, expects real value input and outputs error message if out of range.
    EXAMPLE  | N/A
    """
    pass    # delete "pass" once you have real code for this function!

    # prompt user for `altitude` value

    # while the answer keeps coming back outside of [1 9999], display error and re-prompt

    # return the valid `altitude` value


def displayLMState(elapsed_time, altitude, velocity, fuel_amount, fuel_rate):
    """
    CONTRACT | displayLMState : int float float int int -> None
    PURPOSE  | Given elapsed time, altitude, velocity, fuel amount, and fuel rate, displays it to the console.
    IN/OUTS  | None/str # console output of LM state.
    EXAMPLE  | N/A
    """
    pass    # delete "pass" once you have real code for this function!

    # format the numbers and display the message to the console


def getFuelRate(current_fuel):
    """
    CONTRACT | getFuelRate : int -> float
    PURPOSE  | Given the current fuel amount, returns the lesser of user-given fuel rate or the remaining fuel amount.
    IN/OUTS  | int/None   # console I/O
    EXAMPLE  | N/A
    """
    pass    # delete "pass" once you have real code for this function!

    # prompt the user for a `fuel rate`

    # while given `fuel rate` is not in [0 9], keep prompting

    # check if the given `fuel rate` to the `current fuel` amount

    # if `current fuel` is less, return `current fuel`

    # if `fuel rate` is less, return `fuel rate`


def displayLandingStatus(velocity):
    """
    CONTRACT | displayLandingStatus : float -> None
    PURPOSE  | Given velocity, displays the landing status to the console.
    IN/OUTS  | None/str # Landing status to console
    EXAMPLE  | N/A
    """
    pass    # delete "pass" once you have real code for this function!

    # if `velocity` is in [-1 0], then display "Status at Landing - The eagle has landed!"

    # if `velocity` is in (-10 -1), then display "Status at Landing - Enjoy your oxygen while it lasts!"

    # if `velocity` is in [-inf -10], then display "Status at Landing - Ouch - that hurt!"


def updateAcceleration(gravity, fuel_rate):
    """
    CONTRACT | updateAcceleration : float int -> float
    PURPOSE  | Given gravity and fuel rate, calculates the acceleration of the lunar module.
    IN/OUTS  | None/None
    EXAMPLE  | 1.62 5 -> 0     # constant velocity on the moon
             | 1.62 0 -> -1.62 # free fall on the moon
             | 1.62 9 -> 1.296 # max thrust on the moon
             | 9.82 7 -> 3.928 # strong thrust on the Earth
    """
    pass    # delete "pass" once you have real code for this function!

    # calculate `acceleration` based on the given formula: acceleration = gravity * ((fuel rate / 5) - 1)

    # return `acceleration`


def updateAltitude(altitude, velocity, acceleration):
    """
    CONTRACT | updateAltitude : float float float -> float
    PURPOSE  | Given altitude, velocity, and acceleration, computes and returns the resulting altitude (positive).
    IN/OUTS  | None/None
    EXAMPLE  | 500.0 -30.3 1.62 -> 470.51
             | 123.5 -11.3 5.2 -> 114.8
             | 0.0 -11.3 5.2 -> 0.0 # altitude must not be negative
    """
    pass    # delete "pass" once you have real code for this function!

    # calculate `new altitude` based on the given formula: new altitude = altitude + velocity + (acceleration / 2)

    # if the new altitude is negative, set it to 0

    # return new altitude


def updateVelocity(velocity, acceleration):
    """
    CONTRACT | updateVelocity : float float -> float
    PURPOSE  | Given velocity and acceleration, calculates and returns the resultant velocity.
    IN/OUTS  | None/None
    EXAMPLE  | 11.0 -1.62 -> 9.38
             | 0.32 -3.24 -> -2.92
             | -9.82 9.82 -> 0.0
    """
    pass    # delete "pass" once you have real code for this function!

    # calculate `new velocity` based on the given formula: new velocity = velocity + acceleration

    # return new velocity


def updateFuel(fuel_amount, fuel_rate):
    """
    CONTRACT | updateFuel : int int -> int
    PURPOSE  | Given remaining fuel amount and current fuel rate, calculates the new remaining fuel amount
    IN/OUTS  | None/None
    EXAMPLE  | 500 9 -> 491
             | 12 10 -> 2
             | 3 3 -> 0
    """
    pass    # delete "pass" once you have real code for this function!

    # calculate `new fuel amount` based on the given formula: new fuel amount = fuel amount - fuel rate

    # return the new fuel amount


