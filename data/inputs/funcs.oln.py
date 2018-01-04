"""
Project 1

Name: Mike Ryu
Instructor: Mike Ryu
Section: 13
"""

"""
CONTRACT | poundsToKG : float -> float
-------: | :-------------------------------------------------------------------
PURPOSE  | Converts weight in `pounds` to equivalent mass in `kilograms`.
IN/OUTS  | None/None
EXAMPLE  | 0.0 -> 0.0
         | 1.0 -> 0.453592
         | 5.5 -> 2.494756
         | 120.0 -> 54.43104
         | 213.0 -> 104.779752
"""
# calculate the result with given formula

"""
CONTRACT | getMassObject : char -> float
-------: | :-------------------------------------------------------------------
PURPOSE  | Takes a character representing an `object to throw` and returns `mass of the object` in kg.
IN/OUTS  | None/None
EXAMPLE  | x -> 0.0   # error case ... defaults to 0.0
         | t -> 0.1   # tomato
         | p -> 1.0   # banana cream pie
         | r -> 3.0   # rock
         | g -> 5.3   # lawn gnome
         | l -> 9.07  # light saber
"""
# use conditionals (if .. elif ...) to check for object to throw and return the mass of the object

"""
CONTRACT | getVelocityObject : float -> float
-------: | :-------------------------------------------------------------------
PURPOSE  | Given a `distance` of the professor in meters, returns `object's velocity` in m/s.
IN/OUTS  | None/None
EXAMPLE  | 0.0 -> 0.0   # we may assume velocity of the skater is greater than or equal to zero
         | 0.5 -> 1.5652475842
         | 2.72 -> 3.6507533469
         | 11.11 -> 7.3782789321
"""
# calculate the result with given formula

"""
CONTRACT | getVelocitySkater : float float float -> float
-------: | :-------------------------------------------------------------------
PURPOSE  | Takes in `skater's mass`, `object's mass`, and `object's velocity`, calculates `skater's velocity`.
IN/OUTS  | None/None
EXAMPLE  | 0.0 3.0 0.0 ->  0.0
         | 54.43104 5.3 7.3782789321 -> 0.7184297478
"""
# calculate the result with given formula

"""
CONTRACT | determineMassMessage : float float -> str
-------: | :-------------------------------------------------------------------
PURPOSE  | Given `object's mass` and `distance`, determines what `message` should be printed on screen.
IN/OUTS  | None/None
EXAMPLE  | 0.05 11.00 -> "You're going to get an F!"
         | 0.10 7.12 -> "You're going to get an F!"
         | 0.11 100.00 -> "Make sure your professor is OK."
         | 0.99 20.00 -> "Make sure your professor is OK."
         | 1.00 0.00 -> "Make sure your professor is OK."
         | 1.01 19.99 -> "How far away is the hospital?"
         | 1.01 20.00 -> "RIP Professor."
         | 2.00 30.00 -> "RIP Professor."
"""
# use conditional to check for mass and distance to determine the message

"""
CONTRACT | determineVelocityMessage : float -> str
-------: | :-------------------------------------------------------------------
PURPOSE  | Given `skater's velocity`, determines what `message` should be printed on screen.
IN/OUTS  | None/None
EXAMPLE  | 0.05 -> "My grandmother skates faster than you!"
         | 0.19 -> "My grandmother skates faster than you!"
         | 0.20 -> None
         | 0.99 -> None
         | 1.00 -> "Look out for that railing!!!"
         | 1.01 -> "Look out for that railing!!!"
         | 2.00 -> "Look out for that railing!!!"
"""
# use a conditional (if ... else ...) to determine the message based on velocity


"""
CONTRACT | getSkaterVelocityValueMessage : float -> str
-------: | :-------------------------------------------------------------------
PURPOSE  | Given `skater's velocity`, constructs a str that announces it.
IN/OUTS  | None/None
EXAMPLE  | 0.000 -> "Velocity of skater: 0.000 m/s"
         | 3.019 -> "Velocity of skater: 3.019 m/s"
         | 123.4567 -> "Velocity of skater: 123.457 m/s"
"""
# simply use python string formatting to construct the message


