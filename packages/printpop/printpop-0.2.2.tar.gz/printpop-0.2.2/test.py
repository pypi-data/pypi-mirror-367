from printpop import print_bold, print_rgb, print_formatted, print_red, print_color, print_hyperlink

print()
print()
print()

# Emphasize with bold
print_bold("This text is bold.")

# Custom RGB
print_rgb("This text is soft purple", r=150, g=120, b=180)

# Combine styles
print_formatted("This text is bold, italic, salmon colored with lightcoral background", bold=True, italic=True, color="salmon", back_color="lightcoral")

# Print color name
print_red("This text is red")

# Use named HTML-safe foreground/background colors
print_color("This text is fuchsia", color = "fuchsia" )

# Use any rgb color
print_rgb("This text is one of 16,777,216 possible colors", r = 101, g = 201, b = 113)

# Use any rgb color for background
print_rgb("This text has one of 16,777,216 possible background colors", r = 37, g = 249, b = 201, background = True)

# Combine multiple text styles and colors
print_formatted("This text is bold, underlined, red with yellow background and it is blinking.",
    bold=True,
    dim=False,
    italic=False,
    underline=True,
    blink=True,
    inverse=False,
    hidden=False,
    strikethrough=False,
    color="red",
    back_color="yellow"
)

# Print clickable hyperlink
print_hyperlink(text="This is a blue, clickable hyperlink", hyperlink="https://github.com/rlapine", color="cyan")


print()
print()
print()
