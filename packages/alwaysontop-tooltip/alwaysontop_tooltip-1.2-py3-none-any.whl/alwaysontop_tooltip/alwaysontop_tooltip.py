import tkinter as tk

class AlwaysOnTopToolTip:
    """ A tooltip that appears when hovering over a widget, remains on top, and can be styled """
    def __init__(
            self,
            widget: tk.Widget,
            msg: str,
            delay: int = 500,
            bg: str = "#ffffe0",
            font: tuple = ( "Calibri", 10 ),
            wraplength: int = 300,
            borderstyle: str = 'solid',
            borderwidth: int = 1,
            stationary: bool = False,
            blink: dict | None = None ):
        """ Initialize the tooltip attached to widget

        * widget - The widget to attach the tooltip to
        * message (msg) - The text to display in the tooltip
        * delay - Delay in milliseconds before showing the tooltip
        * background color (bg) - Background color of the tooltip
        * font - Font used for the tooltip text
        * wraplength - Maximum width of the tooltip text before wrapping
        * borderstyle - Style of the tooltip border (e.g., 'solid', 'flat', 'raised', 'sunken', 'groove', 'ridge')
        * borderwidth - Width of the tooltip border
        * stationary - If True, the tooltip does not follow the mouse cursor
        * blink - Configuration for blinking effect, a dictionary with options:
            - enabled: bool, whether blinking is enabled
            - interval: int, time in milliseconds between blink updates
            - mode: str, 'visibility' or 'opacity' for blinking effect
            - min_alpha: float, minimum opacity for 'opacity' mode
            - max_alpha: float, maximum opacity for 'opacity' mode
            - step: float, change in opacity per blink for 'opacity' mode
            - duration: int, time in milliseconds after which blinking stops
        Raises:
            ValueError: If widget is None or msg is not a non-empty string
        """

        # Initial validation
        if widget is None:
            raise ValueError( "Tooltip requires a valid widget." )
        if not isinstance( msg, str ) or not msg.strip():
            raise ValueError("Tooltip requires a non-empty message string.")

        self.widget = widget
        self.text = msg
        self.delay = delay
        self.bg = bg
        self.font = font
        self.wraplength = wraplength
        self.borderwidth = borderwidth

        # Blink config
        self.blink_config = blink or {}
        self.blink_enabled = self.blink_config.get( "enabled", False )
        self.blink_interval = self.blink_config.get( "interval", 500 )
        self.blink_mode = self.blink_config.get( "mode", "solid" )
        self.blink_duration = self.blink_config.get( "duration", None )
        self.blink_timeout_job = None

        # Opacity mode settings
        self.min_alpha = self.blink_config.get( "min_alpha", 0.3 )
        self.max_alpha = self.blink_config.get( "max_alpha", 1.0 )
        self.alpha_step = self.blink_config.get( "step", 0.1 )
        self.current_alpha = self.max_alpha
        self.alpha_direction = -1  # fading out

        self.blink_job = None
        self.blink_state = True

        if borderstyle in ( 'solid', 'flat', 'raised', 'sunken', 'groove', 'ridge' ):
            self.border = borderstyle
            if borderstyle in ( 'groove', 'ridge', 'sunken', 'raised' ) and borderwidth < 3:
                # Use a minimum border width for the style to be visible
                self.borderwidth = 3
        else:
            self.border = 'solid'

        self.tooltip_window = None
        self.after_id = None

        self.widget.bind( "<Enter>", self.schedule )
        self.widget.bind( "<Leave>", self.hide )
        if not stationary:
            self.widget.bind( "<Motion>", self.move )

    def schedule( self, event = None ):
        """ Schedule the tooltip to show after a delay """

        self.unschedule()
        self.after_id = self.widget.after( self.delay, self.show )

    def unschedule( self ):
        """ Cancel the scheduled tooltip display if it exists """

        if self.after_id:
            self.widget.after_cancel( self.after_id )
            self.after_id = None

    def move( self, event ):
        """ Move the tooltip to follow the mouse cursor """

        if self.tooltip_window:
            x, y = event.x_root + 20, event.y_root + 10
            self.tooltip_window.geometry( f"+{ x }+{ y }" )

    def show( self ):
        """ Show the tooltip at the current mouse position """

        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_pointerx() + 20
        y = self.widget.winfo_pointery() + 10

        self.tooltip_window = tw = tk.Toplevel( self.widget )
        tw.wm_overrideredirect( True )
        tw.attributes( "-topmost", True )
        tw.geometry( f"+{ x }+{ y }" )

        label = tk.Label(
            tw,
            text = self.text,
            background = self.bg,
            font = self.font,
            justify = 'left',
            padx = 5,
            pady = 5,
            relief = self.border,
            borderwidth = self.borderwidth,
            wraplength = self.wraplength,
        )
        label.pack()

        if self.blink_enabled:
            self.start_blink()

    def start_blink( self ):
        """ Start the blinking effect for the tooltip """
        if not self.tooltip_window:
            return

        # Blinking behavior: either visibility toggle or opacity fade
        if self.blink_mode == "visibility":
            self.blink_state = not self.blink_state
            if self.blink_state:
                self.tooltip_window.deiconify()
            else:
                self.tooltip_window.withdraw()

        elif self.blink_mode == "opacity":
            self.current_alpha += self.alpha_step * self.alpha_direction
            if self.current_alpha <= self.min_alpha:
                self.current_alpha = self.min_alpha
                self.alpha_direction = 1
            elif self.current_alpha >= self.max_alpha:
                self.current_alpha = self.max_alpha
                self.alpha_direction = -1
            self.tooltip_window.attributes( "-alpha", self.current_alpha )

        # Reschedule blink
        self.blink_job = self.tooltip_window.after( self.blink_interval, self.start_blink )

        # Start the timer to stop blinking after a fixed duration
        if self.blink_duration and not self.blink_timeout_job:
            self.blink_timeout_job = self.tooltip_window.after(
                self.blink_duration, self.stop_blink
            )

    def stop_blink( self ):
        # Cancel the repeated blinking

        if self.blink_job and self.tooltip_window:
            self.tooltip_window.after_cancel( self.blink_job )
            self.blink_job = None

        # Cancel the timeout that would stop blinking
        if self.blink_timeout_job and self.tooltip_window:
            self.tooltip_window.after_cancel( self.blink_timeout_job )
            self.blink_timeout_job = None

        # Reset state based on mode
        if self.tooltip_window:
            if self.blink_mode == "visibility":
                self.tooltip_window.deiconify()
            elif self.blink_mode == "opacity":
                self.tooltip_window.attributes( "-alpha", self.max_alpha )

    def hide( self, event = None ):
        """ Hide the tooltip and clean up """

        self.unschedule()
        self.stop_blink()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
