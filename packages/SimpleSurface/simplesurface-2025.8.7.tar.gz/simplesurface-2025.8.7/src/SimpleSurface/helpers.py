def parse_x(x, origin_width, dest_width, outline_width=0):
    """
    Parse the x-coordinate, either as a number or a string.

    String values available are: left, center, right.

    Keyword arguments:
        x (int/str) -- the x-coordinate to parse.
        origin_width (int) -- the width of the thing being positioned.
        dest_width (int) -- the width of the surface onto which the
            thing is being positioned.
        outline_width (int) -- the width of the thing's outline, if
            applicable (default 0).
    """
    positions = ["left", "center", "right"]

    # If the x-position is a string,
    # make sure it's one of the values available
    if isinstance(x, str):
        assert x in positions, (
            f"parameter 'x' cannot be '{x}', must be either a number "
            f"or one of: {', '.join([position for position in positions])}"
        )

    # Parse the x-coordinate, adjusting for any potential outline
    if x == positions[0]:
        x = outline_width / 2
    elif x == positions[1]:
        x = (dest_width - origin_width) / 2
    elif x == positions[2]:
        x = dest_width - (origin_width + outline_width / 2)
    else:
        x += outline_width / 2

    return x


def parse_y(y, origin_height, dest_height, outline_height=0):
    """
    Parse the y-coordinate, either as a number or a string.

    String values available are: top, center, bottom.

    Keyword arguments:
        y (int/str) -- the y-coordinate to parse.
        origin_height (int) -- the height of the thing being positioned.
        dest_height (int) -- the height of the surface onto which the
            thing is being positioned.
        outline_height (int) -- the height of the thing's outline, if
            applicable (default 0).
    """
    positions = ["top", "center", "bottom"]

    # If the y-position is a string,
    # make sure it's one of the values available
    if isinstance(y, str):
        assert y in positions, (
            f"parameter 'y' cannot be '{y}', must be either a number "
            f"or one of: {', '.join([position for position in positions])}"
        )

    # Parse the y-coordinate, adjusting for any potential outline
    if y == positions[0]:
        y = outline_height / 2
    elif y == positions[1]:
        y = (dest_height - origin_height) / 2
    elif y == positions[2]:
        y = dest_height - (origin_height + outline_height / 2)
    else:
        y += outline_height / 2

    return y
