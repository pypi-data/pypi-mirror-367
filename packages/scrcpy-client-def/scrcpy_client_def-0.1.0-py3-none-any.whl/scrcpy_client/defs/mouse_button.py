from enum import Enum

class MouseButton(Enum):
    """The various buttons.

    The actual values for these items differ between platforms. Some
    platforms may have additional buttons, but these are guaranteed to be
    present everywhere.
    """
    #: An unknown button was pressed
    unknown = 0

    #: The left button
    left = 1

    #: The middle button
    middle = 2

    #: The right button
    right = 3

    #: Side button 1
    x1 = 4

    #: Side button 2
    x2 = 5
