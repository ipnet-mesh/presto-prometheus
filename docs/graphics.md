# Presto Graphics API Reference

Derived from the official Pimoroni Presto examples:
https://github.com/pimoroni/presto/tree/main/examples

The Presto uses **PicoGraphics** (bitmap drawing) and **PicoVector** (vector/shape drawing) together.
Display is **320x240** pixels.

---

## Presto Setup

```python
from presto import Presto

presto = Presto()                          # Default (half-res, no ambient light)
presto = Presto(ambient_light=True)        # Enable ambient light sensor
presto = Presto(full_res=True)             # Full resolution mode
presto = Presto(full_res=True, ambient_light=False)

display = presto.display                   # PicoGraphics display instance
WIDTH, HEIGHT = display.get_bounds()       # Returns (320, 240)

touch = presto.touch                       # Touch controller
touch.poll()                               # Must be called each frame
touch.state                                # True if touching
touch.x, touch.y                           # Touch coordinates
```

### Networking

```python
wifi = presto.connect()                    # Connect to WiFi (uses secrets.py)
```

### Backlight & LEDs

```python
presto.set_backlight(0.5)                  # Set backlight brightness (0.0 - 1.0)
presto.set_led_rgb(index, r, g, b)         # Set LED colour (index 0-6)
presto.set_led_hsv(index, h, s, v)         # Set LED colour in HSV (h: 0.0-1.0)
```

### Display Update

```python
presto.update()                            # Push framebuffer to screen (REQUIRED each frame)
```

---

## Colour / Pen System

```python
# RGB pen (0-255 per channel)
PEN = display.create_pen(r, g, b)

# HSV pen (h: 0.0-1.0, s: 0.0-1.0, v: 0.0-1.0)
PEN = display.create_pen_hsv(h, s, v)

# Set current drawing pen
display.set_pen(PEN)
```

---

## PicoGraphics (Bitmap Drawing)

### Clear

```python
display.set_pen(BG_COLOUR)
display.clear()                            # Fill entire screen with current pen
```

### Text (Bitmap Font)

```python
display.set_font("bitmap8")               # Select built-in bitmap font
display.text("Hello", x, y, wrap_width, scale=1, spacing=1)
# Parameters:
#   text      - string to render
#   x, y      - top-left position
#   wrap      - word wrap width in pixels (use WIDTH for no wrap)
#   scale     - integer scale factor (1, 2, 3...)
#   spacing   - letter spacing multiplier
```

### Measure Text (Bitmap)

```python
width = display.measure_text("Hello", scale, spacing)
# Returns pixel width of rendered text
```

### Circle (Bitmap)

```python
display.circle(x, y, r)                   # Filled circle at (x,y) with radius r
```

### Layers

```python
display.set_layer(0)                      # Switch to background layer
display.set_layer(1)                      # Switch to foreground layer
# Layer 0 can hold a persistent background (e.g. decoded PNG)
```

### Images (PNG)

```python
import pngdec
p = pngdec.PNG(display)
p.open_file("image.png")
p.decode(0, 0)                            # Decode at position (x, y)
```

---

## PicoVector (Vector Drawing)

### Setup

```python
from picovector import ANTIALIAS_BEST, ANTIALIAS_FAST, ANTIALIAS_X16
from picovector import PicoVector, Polygon, Transform

vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)   # ANTIALIAS_FAST, ANTIALIAS_X16 also available
```

### Transform

```python
t = Transform()
vector.set_transform(t)                   # Apply transform to subsequent draws

t.reset()                                 # Reset to identity
t.rotate(angle_degrees, (cx, cy))         # Rotate around point
t.translate(dx, dy)                       # Translate
t.scale(sx, sy)                           # Scale
```

### Polygon Shapes

`Polygon` objects are reusable shapes. Create them once, draw many times.

```python
p = Polygon()
```

#### Circle

```python
p.circle(x, y, r)                         # Filled circle
p = Polygon().circle(x, y, r, stroke=2)   # Circle outline with stroke width
```

#### Rectangle

```python
p.rectangle(x, y, w, h)                   # Filled rectangle
p.rectangle(x, y, w, h, (r1, r2, r3, r4)) # Rounded corners (top-left, top-right, bottom-right, bottom-left)
p = Polygon().rectangle(x, y, w, h, radii, stroke=2)  # Rectangle outline with stroke
```

#### Arc

```python
p.arc(x, y, r, start_angle, end_angle)    # Arc from start to end angle (degrees)
p = Polygon().arc(x, y, r, start, end, stroke=2)  # Arc with stroke width
```

#### Path (Custom Polygons)

```python
# Define shape from coordinate tuples
p.path((x1, y1), (x2, y2), (x3, y3), ...)  # Filled polygon from vertices

# Can chain multiple paths into one Polygon
p.path(*points_list_1)
p.path(*points_list_2)                    # Adds another sub-path (e.g. for compound shapes)
```

#### Drawing Polygons

```python
display.set_pen(PEN_COLOUR)
vector.draw(polygon)                      # Render polygon with current pen/transform
```

### Vector Text

#### Font Setup

```python
# Load a custom font file (.af format)
vector.set_font("Roboto-Medium.af", 54)   # Load font at default size
vector.set_font("osansb.af", 50)          # Another example

# Set font size (overrides loaded size)
vector.set_font_size(32)

# Font metrics/spacing (percentage-based, 100 = default)
vector.set_font_letter_spacing(100)       # 100 = normal, 200 = double, etc.
vector.set_font_word_spacing(100)
vector.set_font_line_height(110)
```

#### Text Rendering

```python
display.set_pen(TEXT_COLOUR)
vector.set_font_size(32)
vector.text("Hello", x, y)                # Render text at position
vector.text("Wrapped", x, y, max_width=WIDTH)  # With max width constraint
```

#### Measure Text (Vector)

```python
bounds = vector.measure_text("Hello")
# Returns tuple including width: bounds[2]
text_width = int(vector.measure_text("Hello")[2])
```

---

## Touch Input

```python
touch = presto.touch
touch.poll()                              # REQUIRED - poll each frame before reading state

touch.state                               # bool - is screen being touched?
touch.x                                   # int - x coordinate of touch
touch.y                                   # int - y coordinate of touch
```

---

## Complete Draw Loop Pattern

```python
from presto import Presto
from picovector import ANTIALIAS_BEST, PicoVector, Polygon

presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

# Pre-build shapes outside the loop
my_circle = Polygon()
my_circle.circle(100, 100, 50)

while True:
    # 1. Clear
    display.set_pen(BLACK)
    display.clear()

    # 2. Draw shapes
    display.set_pen(WHITE)
    vector.draw(my_circle)

    # 3. Draw text
    vector.set_font_size(28)
    vector.text("Hello", 15, 35)

    # 4. Push to screen
    presto.update()
```

---

## Memory Considerations

The Presto runs on an RP2350 with limited RAM. Key tips from the examples:

- **Pre-build `Polygon` objects outside the loop** — don't create new polygons each frame
- **Minimise `vector.text()` calls** — vector text rendering is memory-intensive at large sizes
- **Use `display.text()` (bitmap font) for small text** — much lighter than vector text
- **Call `gc.collect()` periodically** in your main loop
- **Avoid creating new string objects in the draw loop** — pre-format strings
- **Keep font sizes moderate** — sizes above ~40 for vector text use significant memory per glyph
- **The 256-entry pen palette is shared** — creating more than ~256 pens will fail silently
