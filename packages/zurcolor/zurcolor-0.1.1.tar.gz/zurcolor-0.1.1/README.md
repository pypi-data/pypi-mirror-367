
# zurcolor

A minimal Python library to print custom text in the terminal using ANSI escape codes (for example red or italic).

## Installation

```bash
pip install zurcolor
```

## Usage

```python
from zurcolor import (
    red, blue, green, yellow, purple, cyan, white, pink, black,
    red_bg, blue_bg, green_bg, yellow_bg, cyan_bg, purple_bg, pink_bg, white_bg,
    bright, dark,
    bold, italic, underline, invert, blink
)

print(red("Hello, Red!"))
print(blue("Hello, Blue!"))
print(green("Hello, Green!"))
print(yellow("Hello, Yellow!"))
print(purple("Hello, Purple!"))
print(cyan("Hello, Cyan!"))
print(white("Hello, White!"))
print(pink("Hello, Pink!"))
print(black("Hello, Black!"))

print(red_bg("Hello, Red BG!"))
print(blue_bg("Hello, Blue BG!"))
print(green_bg("Hello, Green BG!"))
print(yellow_bg("Hello, Yellow BG!"))
print(cyan_bg("Hello, Cyan BG!"))
print(purple_bg("Hello, Purple BG!"))
print(pink_bg("Hello, Pink BG!"))
print(white_bg("Hello, White BG!"))

print(bright(red("Hello, Bright Red!")))
print(dark(blue("Hello, Fade Blue!")))

print(italic("Hello, Italic!"))
print(underline("Hello, Underline!"))
print(invert("Hello, Invert!"))
print(blink("Hello, Blink!"))
print(bold("Hello, Bold!"))
```

## License

Apache 2.0

# Note

Not every terminal will support all of functions as well as have the same ANSI escape codes support!