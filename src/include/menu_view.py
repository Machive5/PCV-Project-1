from typing import Callable

import arcade
import include.shared as shared
from arcade.gui import UIFlatButton, UILabel, UIView


class MenuView(UIView):
    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        on_play: Callable[[], None],
        on_calibrate_camera: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_play = on_play
        self.on_calibrate_camera = on_calibrate_camera
        self.on_quit = on_quit

    def on_show_view(self):
        super().on_show_view()
        self.window.background_color = (18, 22, 28)
        self._build_ui()

    def _build_ui(self):
        self.ui.clear()

        center_x = self.screen_width / 2
        center_y = self.screen_height / 2

        self.ui.add(
            UILabel(
                text="AIR HOCKEY",
                x=center_x - 200,
                y=center_y + 180,
                width=400,
                font_size=32,
                bold=True,
                align="center",
                text_color=(240, 244, 248),
            )
        )

        self.ui.add(
            UILabel(
                text="Pilih menu",
                x=center_x - 200,
                y=center_y + 135,
                width=400,
                font_size=16,
                align="center",
                text_color=(170, 180, 192),
            )
        )

        button_width = 260
        button_height = 55
        button_x = center_x - button_width / 2
        gap = 18

        play_button = UIFlatButton(
            text="Play",
            x=button_x,
            y=center_y + 45,
            width=button_width,
            height=button_height,
        )

        calibrate_button = UIFlatButton(
            text="Calibrate Camera",
            x=button_x,
            y=center_y + 45 - button_height - gap,
            width=button_width,
            height=button_height,
        )

        quit_button = UIFlatButton(
            text="Quit",
            x=button_x,
            y=center_y + 45 - (button_height + gap) * 2,
            width=button_width,
            height=button_height,
        )

        self.ui.add(play_button)
        self.ui.add(calibrate_button)
        self.ui.add(quit_button)

        @play_button.event("on_click")
        def on_play_click(event):
            self.on_play()

        @calibrate_button.event("on_click")
        def on_calibrate_click(event):
            shared.is_calib = True
            self.on_calibrate_camera()

        @quit_button.event("on_click")
        def on_quit_click(event):
            self.on_quit()

    def on_draw(self):
        self.clear()
        super().on_draw()