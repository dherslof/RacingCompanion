# This file is part of the Racing-Companion project.
#
# Description: GUI support functionality for the Racing Companion application tabs.
# License: TBD

def enable_mousewheel_scrolling(scrollable_frame):
    """Enable mousewheel scrolling for a CTkScrollableFrame only when hovered."""

    canvas = scrollable_frame._parent_canvas  # internal canvas

    def _on_mousewheel(event):
        if event.delta:  # Windows & MacOS
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:  # Linux scroll up
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            canvas.yview_scroll(1, "units")

    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    # Bind when mouse enters the scrollable frame, unbind when it leaves
    scrollable_frame.bind("<Enter>", _bind_mousewheel)
    scrollable_frame.bind("<Leave>", _unbind_mousewheel)