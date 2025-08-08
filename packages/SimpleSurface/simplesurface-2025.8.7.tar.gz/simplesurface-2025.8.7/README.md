# SimpleSurface
A simpler version of Pycairo's ImageSurface.

This library complements Pycairo's ImageSurface and Context classes by adding in some non-native functionality.

## Comparison Example

### Blue Ellipse using Pycairo
```
import cairo
import math

# Create 600x800 Surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 800)
context = cairo.Context(surface)

# Draw a blue ellipse with top-left corner at (50, 50) measuring 150x200 pixels
x = 50
y = 50
width = 150
height = 200

context.save()
context.translate(x + width / 2., y + height / 2.)
context.scale(width / 2., height / 2.)
context.set_source_rgb(0, 0, 1)
context.arc(0., 0., 1., 0., 2 * math.pi)
context.fill()
context.restore()

# Save as a PDF
pdf_surface = cairo.PDFSurface("example.pdf", 600, 800)
pdf_context = cairo.Context(pdf_surface)
pdf_context.set_source_surface(surface)
pdf_context.paint()
pdf_context.show_page()
```

### Blue Ellipse using SimpleSurface
```
from SimpleSurface import SimpleSurface

# Create 600x800 SimpleSurface
simple_surface = SimpleSurface(600, 800)

# Draw a blue ellipse with top-left corner at (50, 50) measuring 150x200 pixels
simple_surface.ellipse(50, 50, 150, 200, fill_color=(0, 0, 255))

# Save as a PDF
simple_surface.write_to_pdf("example.pdf")
```

## Installation
To install, simply open a terminal and type `pip install SimpleSurface`

## Functions
### \_\_init\_\_
`SimpleSurface(width, height [, format])`

Initialize the SimpleSurface object.

Keyword arguments:
* `width` -- the width of the image, in pixels.
* `height` -- the height of the image, in pixels.

Optional arguments:
* `format` -- the format of the image (default `cairo.FORMAT_ARGB32`).


### crop
`crop(x, y, width, height)`

Return a copy of the surface, cropped to a given width and height. The (x, y)-coordinates mark the top-left corner of the section to be cropped.

Keyword arguments:
* `x` -- the left side of the crop.
* `y` -- the top side of the crop.
* `width` -- the width of the crop.
* `height` -- the height of the crop.

### dot
`dot(x, y [, radius, fill_color, fill, line_width, line_color])`

Draw a dot centered at (x, y).

Keyword arguments:
* `x` -- the x-coordinate.
* `y` -- the y-coordinate.

Optional arguments:
* `radius` -- the radius of the dot (default `1`).
* `fill_color` -- the RGB(A) color of the dot (default `(0, 0, 0)` (black)).
* `fill` -- whether or not to fill the dot with color (default `True`).
* `line_width` -- the thickness of the dot's outline, in pixels (default `1`).
* `line_color` -- the RGB(A) color of the dot's outline (default `fill_color`).


### ellipse
`ellipse(x, y, width, height [, fill_color, fill, line_width, line_color])`

Draw an ellipse of a given width and height. The (x, y)-coordinates correspond to the top-left corner of the bounding box that would contain the ellipse.

Keyword arguments:
* `x` -- the x-coordinate of the ellipse.
* `y` -- the y-coordinate of the ellipse.
* `width` -- the width of the ellipse.
* `height` -- the height of the ellipse.

Optional arguments:
* `fill_color` -- the RGB(A) color of the ellipse (default `(0, 0, 0)` (black)).
* `fill` -- whether or not to fill the ellipse with color (default `True`).
* `line_width` -- the thickness of the ellipse's outline, in pixels (default `1`).
* `line_color` -- the RGB(A) color of the ellipse's outline (default `fill_color`).

### get_format
`get_format()`

Return the ImageSurface attribute's format.

### get_height
`get_height()`

Return the ImageSurface attribute's height.

### get_width
`get_width`

Return the ImageSurface attribute's width.

### gridlines
`gridlines( [color=(0, 0, 0)])`

Outline the surface, and draw vertical and horizontal center lines.

Optional arguments:
* `color` -- the RGB(A) color of the gridlines (default `(0, 0, 0)` (black)).

### line
`line(x1, y1, x2, y2 [, line_color, line_cap, line_width])`

Draw a line connecting two points at given sets of coordinates.

Keyword arguments:
* `x1` -- the x-coordinate of the first point.
* `y1` -- the y-coordinate of the first point.
* `x2` -- the x-coordinate of the second point.
* `y2` -- the y-coordinate of the second point.

Optional arguments:
* `line_color` -- the RGB(A) color of the line (default `(0, 0, 0)` (black)).
* `line_cap` -- the pycairo cap at the end of the line (default `cairo.LINE_CAP_SQUARE`).
* `line_width` -- the thickness of the line, in pixels (default `1`).

### outline
`outline( [color, width])`

Outline the surface.

Optional arguments:
* `color` -- the color of the outline (default `(0, 0, 0)` (black)).
* `width` -- the width of the outline, in pixels (default `1`).

### paste
`paste(origin, x, y [, width, height, scaling, rotate])`

Paste a given cairo.ImageSurface or SimpleSurface object at a given (x, y)-coordinate.

The x, y values specify the top-left corner of where to paste the image. These values can also be represented as one of a set of strings: "left", "center", or "right" for x, and "top", "center", or "bottom" for y.

If the width/height parameters are left as None, then they default to the width/height of the origin Surface.

The origin Surface is scaled no matter what. If the scaling parameter is set to "absolute", then the resulting pasted image will be exactly the width and height variables (e.g., 600, 800). If scaling is set to "ratio", then the origin Surface is scaled by the ratios set by the width and height variables (e.g., 2.0, 1.5).

The pasted image can also be rotated clockwise in radians (where 2\*pi is one full rotation). The rotation happens about the top-left corner (i.e., the (x, y)-coordinate).

Keyword arguments:
* `origin` -- the `cairo.ImageSurface` or `SimpleSurface` that's going to be pasted.
* `x` -- the x-coordinate of the image. It can be either a number, or one of "left", "center", or "right".
* `y` -- the y-coordinate of the image. It can be either a number, or one of "top", "center", or "bottom".

Optional arguments:
* `width` -- the desired width of the pasted image (default `None`).
* `height` -- the desired height of the pasted image (default `None`).
* `scaling` -- how to scale the pasted image, either "absolute" or "ratio" (default `"absolute"`).
* `rotate` -- how much to rotate the pasted imaged clockwise, in radians, where 2\*pi is one full rotation (default `0`).

### polygon
`polygon(points [, fill_color, fill, line_join, line_width, line_color])`

Draw a polygon that connects a series of (x, y)-coordinates.

Keyword arguments:
* `points` -- a list of (x, y)-coordinates as tuples, indicating the vertices of the polygon.

Optional arguments:
* `fill_color` -- the RGB(A) color of the polygon (default `(0, 0, 0)` (black)).
* `fill` -- whether or not to fill the polygon with color (default `True`).
* `line_join` -- the rendering between two joining lines (default `cairo.LINE_JOIN_MITER`).
* `line_width` -- the thickness of the polygon's outline, in pixels (default `1`).
* `line_color` -- the RGB(A) color of the polygon's outline (default `fill_color`).

### rectangle
`rectangle(x, y, width, height [, fill_color, fill, line_width, line_color])`

Draw a rectangle. The (x, y)-coordinates correspond to the top-left corner of the rectangle.

Keyword arguments:
* `x` -- the x-coordinate.
* `y` -- the y-coordinate.
* `width` -- the width of the rectangle.
* `height` -- the height of the rectangle.

Optional arguments:
* `fill_color` -- the RGB(A) color of the rectangle (default `(0, 0, 0)` (black)).
* `fill` -- whether or not to fill the rectangle with color (default `True`).
* `line_width` -- the thickness of the rectangle's outline, in pixels (default `1`).
* `line_color` -- the RGB(A) color of the rectangle's outline (default `fill_color`).

### rounded_rectangle
`rounded_rectangle(x, y, width, height, radius [, fill_color, fill, line_width, line_color])`

Draw a rectangle with rounded corners. The (x, y)-coordinates correspond to the top-left corner of the bounding box that would contain the rounded rectangle.

Keyword arguments:
* `x` -- the x-coordinate.
* `y` -- the y-coordinate.
* `width` -- the width of the rectangle.
* `height` -- the height of the rectangle.
* `radius` -- the radius of the rectangle's corners.

Optional arguments:
* `fill_color` -- the RGB(A) color of the rectangle (default `(0, 0, 0)` (black)).
* `fill` -- whether or not to fill the rectangle with color (default `True`).
* `line_width` -- the thickness of the rectangle's outline, in pixels (default `1`).
* `line_color` -- the RGB(A) color of the rectangle's outline (default `fill_color`).

### set_background
`set_background( [color])`

Set the surface background to a given color.

Optional arguments:
* `color` -- the RGB(A) color of the background (default `(255, 255, 255)` (white)).

### write
`write(text, x, y, font [, alignment, break_lines, color, font_size, justify_last_line, line_spacing, max_height, max_width, min_font_size, outline_width, outline_color, padding])`

Write text at given coordinates, with given attributes. Return the resulting width and height of the bounding box that includes the text and padding.

Keyword arguments:
* `text` -- the text to be written.
* `x` -- the x-coordinate of the text.
* `y` -- the y-coordinate of the text.
* `font` -- the filename of the font.

Optional arguments:
* `alignment` -- the alignment of the text. Can be "left", "center", "right", or "justified" (default `"left"`).
* `break_lines` -- whether to break text up into multiple lines if it's too long (default `True`).
* `color` -- the color of the text as an RGB(A) tuple (default `(0, 0, 0)` (black)).
* `font_size` -- the font size, in pts. If set to "fill", it will be the largest font size it can be (default `"fill"`).
* `justify_last_line` -- whether to justify the last line of text , if the text is justified. If set to False, the last line will be left-aligned (default `False`).
* `line_spacing` -- the line spacing multiplier (default `1.0`).
* `max_height` -- the maximum vertical space the text and padding will take up. If set to "fill", it will be the largest height needed/allowed (default `"fill"`).
* `max_width` -- the maximum horizontal space the text and padding will take up. If set to "fill", it will be the largest width needed/allowed (default `"fill"`).
* `min_font_size` -- the minimum font size, in pts (default `7`).
* `outline_width` -- the text outline width, in pixels (default `0`).
* `outline_color` -- the color of the text outline as an RGB(A) tuple (default `(0, 0, 0)` (black)).
* `padding` -- the padding around the text, in pixels. Any or all of the padding keys can be sent in. (default `{"top":0, "right":0, "bottom":0, "left":0}`).

### write_to_pdf
`write_to_pdf(target [, dpi])`

Write the SimpleSurface to a PDF file.

Keyword arguments:
* `target` -- the filepath of the PDF file to save to.

Optional arguments:
* `dpi` -- the DPI of the image (default `300`).

### write_to_png
`write_to_png(target)`

Write the SimpleSurface to a PNG file.

Keyword arguments:
* `target` -- the filepath of the PNG file to save to.

## A Note About Shape Outlines
When stroking a shape with Pycairo, the stroke line drawn straddles the outline of the shape. That means that the resulting size of the shape may be different than what's intended.

For example: a 50x50 square with an outline of 10 pixels would actually result in a shape 60x60 pixels in size.

In SimpleSurface, the thickness of the stroke line is accounted for, so the resulting shape will always fit within the width and height specified.

## Writing Text
SimpleSurface provides some pretty powerful ways of writing text. Here are just a few things you can do when writing text with SimpleSurface:
* Left-align, center-align, right-align, and justify text.
* Colour the text, outline the text, and give the outline its own colour.
* Specify padding around the text (in pixels).
* Send in any text along with the width (`max_width`) and height (`max_height`) you want it to occupy, and SimpleSurface will automatically fill that space as much as possible.
* Tell SimpleSurface to leave the text as one line (set `break_lines` to `False`) to get the largest text possible within one line, say for a title.
* Specify the font.
* Specify the font size.

Check out the examples to see some code.

## Positioning
The (x, y) positions in SimpleSurface will accept numbers as well as strings. For the `x` position, it will accept `left`, `center`, and `right`. For the `y` position, it will accept `top`, `center`, and `bottom`. These will position things based on the SimpleSurface you're drawing to.

Check out the examples folder to see examples of how this is done.

## Want to do something else?
SimpleSurface is meant to provide easy access to some much-needed functionality within Pycairo. If you want to do anything more Pycairo-specific, each SimpleSurface object contains an ImageSurface (`surface`) and Context (`context`) that you can access directly:

```
import cairo
from SimpleSurface import SimpleSurface

simple_surface = SimpleSurface(600, 800)
simple_surface.context.set_line_width(5)
simple_surface.surface.write_to_png("example.png")
```