PePy statistics 
[![PyPI Downloads](https://static.pepy.tech/badge/alwaysontop-tooltip)](https://pepy.tech/projects/alwaysontop-tooltip)

Creates a tooltip that will be displayed on top of all windows.

The tooltip will be attached to the assigned Tkinter widget and follow the mouse as long as mouse stays within widget boundaries.

## Standard definition

The minimum definition of the tooltip uses these parameters:
  * widget - The widget to attach the tooltip to
  * msg - The text to display

## Styling and definition

Additionaly these parameters can be used for more styling.

### Display parameters
  * delay - Time to wait (in milliseconds) for the tooltip to be displayed
  * borderstyle - How is the border to be styled. Available values
    * solid **[Default]**
    * flat
    * raised
    * sunken
    * groove
    * ridge

    * groove, ridge, sunken, raised will need a border width of at least 3 to be visual. If borderwidth is not defined, or less than 3, it will be automatically adjusted.
  * borderwidth - Width of the border. Defaults to 1.
  * stationary - If set, the tooltip will be stationary, otherwise the tooltip will follow the mouses movements
  * blink - Settings for how the tooltip should blink. Defaults to not blink. Available parameters:
    * enabled: Boolean to set if blinking is enabled
    * interval: Time in milliseconds between blink updates
    * mode: In what way should the blinking be visible. Available values:
        * 'solid' **[Default]** The blinking will toggle between visible and not visible
        * 'opacity' The blinking will have a fading effect
    * min_alpha: Minimum opacity for 'opacity' mode
    * max_alpha: Maximum opacity for 'opacity' mode
    * step: Change in opacity per blink for 'opacity' mode
    * duration: Time in milliseconds after which blinking stops. When stopped, the tooltip will stay visible

### Visual parameters
  * bg - Background color of the tooltip
  * font - Font for the text of the tooltip
  * wraplength - At what length should the text be wrapped. This in effect also affects max width of the tooltip
