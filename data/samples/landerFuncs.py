"""
Project 2 - Moonlander

Name: Mike Ryu
Instructor: Mike Ryu
"""


def showWelcome():
    """
    CONTRACT | showWelcome : None -> None
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Displays the welcome message for the lunar lander.
    IN/OUTS  | None/string
    EXAMPLE  | N/A
    """
    # print the welcome message
    msg = "Welcome aboard the Lunar Module Flight Simulator\n\n" \
          "   To begin you must specify the LM's initial altitude\n" \
          "   and fuel level.  To simulate the actual LM use\n" \
          "   values of 1300 meters and 500 liters, respectively.\n\n" \
          "   Good luck and may the force be with you!\n"
    print(msg)


def getFuel():
    """
    CONTRACT | getFuel : None -> int
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Prompts the user for a positive integer value and returns it; show error and re-prompt for invalid values.
    IN/OUTS  | int/string  # console I/O, expects integer input and outputs error message if out of bounds.
    EXAMPLE  | N/A
    """
    # prompt user for `fuel` value
    prompt_msg = "Enter the initial amount of fuel on board the LM (in liters): "
    fuel = int(input(prompt_msg))

    # as long as the answer is negative or zero, display error and re-prompt
    while fuel <= 0:
        print("ERROR: Amount of fuel must be positive, please try again")
        fuel = int(input(prompt_msg))

    # return the positive `fuel` value
    return fuel


def getAltitude():
    """
    CONTRACT | getAltitude : None -> float
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Prompts the user for a real value in [1, 9999]; show error nad re-prompt if value given is out of range.
    IN/OUTS  | float/string  # console I/O, expects real value input and outputs error message if out of range.
    EXAMPLE  | N/A
    """
    # prompt user for `altitude` value
    prompt_msg = "Enter the initial altitude of the LM (in meters): "
    altitude = float(input(prompt_msg))

    # while the answer keeps coming back outside of [1 9999], display error and re-prompt
    while altitude < 1 or altitude > 9999:
        print("ERROR: Altitude must be between 1 and 9999, inclusive, please try again")
        altitude = float(input(prompt_msg))

    # return the valid `altitude` value
    return altitude


def displayLMState(elapsed_time, altitude, velocity, fuel_amount, fuel_rate):
    """
    CONTRACT | displayLMState : int float float int int -> None
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given `elapsed time`, `altitude`, `velocity`, `fuel amount`, and `fuel rate`, displays it to the console.
    IN/OUTS  | None/string # console output of LM state.
    EXAMPLE  | N/A
    """
    # format the numbers and display the message to the console
    state_msg = "{:>12}: {:4d} s\n" \
                "{:>12}: {:4d} l\n" \
                "{:>12}: {:4d} l/s\n" \
                "{:>12}: {:7.2f} m\n" \
                "{:>12}: {:7.2f} m/s" \
                "".format("Elapsed Time", elapsed_time,
                          "Fuel", fuel_amount,
                          "Rate", fuel_rate,
                          "Altitude", altitude,
                          "Velocity", velocity)
    print(state_msg)


def getFuelRate(current_fuel):
    """
    CONTRACT | getFuelRate : int -> float
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given the `current fuel` amount, returns the lesser of user-given fuel rate or the remaining fuel amount.
    IN/OUTS  | int/None   # console I/O
    EXAMPLE  | N/A
    """
    # prompt the user for a `fuel rate`
    prompt_msg = "Enter fuel rate (0-9, 0=freefall, 5=constant velocity, 9=max thrust): "
    fuel_rate = int(input(prompt_msg))

    # while given `fuel rate` is not in [0 9], keep prompting
    while fuel_rate < 0 or fuel_rate > 9:
        print("ERROR: Fuel rate must be between 0 and 9, inclusive")
        fuel_rate = int(input(prompt_msg))

    # check if the given `fuel rate` to the `current fuel` amount
    if fuel_rate > current_fuel:
        #  if `current fuel` is less, return `current fuel`
        return current_fuel
    else:
        # if `fuel rate` is less, return `fuel rate`
        return fuel_rate


def displayLMLandingStatus(velocity):
    """
    CONTRACT | displayLandingStatus : float -> None
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given `velocity`, displays the landing status to the console.
    IN/OUTS  | None/string # Landing status to console
    EXAMPLE  | N/A
    """
    msg = ''

    if velocity >= -1 and velocity <= 0:
        # if `velocity` is in [-1 0], then display "Status at Landing - The eagle has landed!"
        msg = "Status at landing - The eagle has landed!"
    elif velocity > -10:
        # if `velocity` is in (-10 -1), then display "Status at Landing - Enjoy your oxygen while it lasts!"
        msg = "Status at landing - Enjoy your oxygen while it lasts!"
    else:
        # if `velocity` is in (-inf -10], then display "Status at Landing - Ouch - that hurt!"
        msg = "Status at landing - Ouch - that hurt!"

    print(msg)


def updateAcceleration(gravity, fuel_rate):
    """
    CONTRACT | updateAcceleration : float int -> float
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given `gravity` and `fuel rate`, calculates the acceleration of the lunar module.
    IN/OUTS  | None/None
    EXAMPLE  | 1.62 5 -> 0     # constant velocity on the moon
             | 1.62 0 -> -1.62 # free fall on the moon
             | 1.62 9 -> 1.296 # max thrust on the moon
             | 9.82 7 -> 3.928 # strong thrust on the Earth
    """
    # calculate `acceleration` based on the given formula: acceleration = gravity * ((fuel rate / 5) - 1)
    acceleration = gravity * ((fuel_rate / 5) - 1)

    # return `acceleration`
    return acceleration


def updateAltitude(altitude, velocity, acceleration):
    """
    CONTRACT | updateAltitude : float float float -> float
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given `altitude`, `velocity`, and `acceleration`, computes and returns the resulting altitude (positive).
    IN/OUTS  | None/None
    EXAMPLE  | 500.0 -30.3 1.62 -> 470.51
             | 123.5 -11.3 5.2 -> 114.8
             | 0.0 -11.3 5.2 -> 0.0 # altitude must not be negative
    """
    # calculate `new altitude` based on the given formula: new altitude = altitude + velocity + (acceleration / 2)
    new_altitude = altitude + velocity + (acceleration / 2)

    # if the new altitude is negative, set it to 0
    if new_altitude < 0:
        new_altitude = 0

    # return new altitude
    return new_altitude


def updateVelocity(velocity, acceleration):
    """
    CONTRACT | updateVelocity : float float -> float
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given `velocity` and `acceleration`, calculates and returns the resultant velocity.
    IN/OUTS  | None/None
    EXAMPLE  | 11.0 -1.62 -> 9.38
             | 0.32 -3.24 -> -2.92
             | -9.82 9.82 -> 0.0
    """
    # calculate `new velocity` based on the given formula: new velocity = velocity + acceleration
    new_velocity = velocity + acceleration

    # return new velocity
    return new_velocity


def updateFuel(fuel_amount, fuel_rate):
    """
    CONTRACT | updateFuel : int int -> int
    -------: | :-------------------------------------------------------------------
    PURPOSE  | Given remaining `fuel amount` and current `fuel rate`, calculates the new remaining fuel amount
    IN/OUTS  | None/None
    EXAMPLE  | 500 9 -> 491
             | 12 10 -> 2
             | 3 3 -> 0
    """
    # calculate `new fuel amount` based on the given formula: new fuel amount = fuel amount - fuel rate
    new_fuel_amount = fuel_amount - fuel_rate

    # return the new fuel amount
    return new_fuel_amount

# def showWelcome():
#    pass
#
# def getFuel():
#    pass
#
# def getAltitude():
#    pass
#
# def displayLMState(elapsedTime, altitude, velocity, fuelAmount, fuelRate):
#    pass
#
# def getFuelRate(currentFuel):
#    pass
#
# def updateAcceleration(gravity, fuelRate):
#    pass
#
# def updateAltitude(altitude, velocity, acceleration):
#    pass
#
# def updateVelocity(velocity, acceleration):
#    pass
#
# def updateFuel(fuel, fuelRate):
#    pass
#
# def displayLMLandingStatus(velocity):
#    pass
