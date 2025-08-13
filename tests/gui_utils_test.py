# This file is part of the Racing-Companion project.
#
# Description: Unit test for GUI utils functionality for the Racing Companion application.
# License: TBD

import pytest
import customtkinter as ctk

from rcfunc.gui_utils import enable_mousewheel_scrolling

@pytest.fixture(scope="module")
def tk_root():
    root = ctk.CTk()
    yield root
    root.destroy()

def test_enable_mousewheel_scrolling_binds_and_unbinds(tk_root):
    # Create a scrollable frame
    frame = ctk.CTkScrollableFrame(tk_root, width=200, height=200)
    frame.pack()

    # Enable scrolling
    enable_mousewheel_scrolling(frame)

    canvas = frame._parent_canvas

    # Initially there should be no bindings
    assert not canvas.bind("<MouseWheel>")

    # Simulate mouse entering the frame
    frame.event_generate("<Enter>")
    tk_root.update_idletasks()

    # Now the binding should exist
    assert canvas.bind_all("<MouseWheel>") is not None

    # Simulate mouse leaving the frame
    frame.event_generate("<Leave>")
    tk_root.update_idletasks()

    # Binding should be gone
    assert not canvas.bind_all("<MouseWheel>")