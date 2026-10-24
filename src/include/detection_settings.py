from typing import Callable

import arcade
from arcade.gui import (
    UIFlatButton,
    UILabel,
    UISlider,
    UIOnChangeEvent,
    UIView,
)

from include.image_processing import ObjectDetection
import include.shared as shared


class DetectionSettings(UIView):
    COLOR_SPACES = ("BGR", "HLS", "HSV", "YUV", "YCrCb")
    CHANNEL_NAMES = ("Channel 1", "Channel 2", "Channel 3")

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        object_detection: ObjectDetection,
        on_save: Callable[[], None] | None = None,
    ):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.object_detection = object_detection
        self.on_save = on_save
        self.status_label: UILabel | None = None
        self.value_labels: list[UILabel] = []
        self.sliders: list[tuple[UISlider, UISlider]] = []
        self._updating_sliders = False

        self.margin = 25
        self.bounds = {
            "left": self.margin,
            "right": self.screen_width - self.margin,
            "bottom": self.margin,
            "top": self.screen_height - self.margin,
            "width": self.screen_width,
            "height": self.screen_height,
            "center_x": self.screen_width / 2,
            "center_y": self.screen_height / 2,
        }

    def on_show_view(self):
        super().on_show_view()
        self.window.background_color = (18, 22, 28)
        self._build_ui()

    def _build_ui(self):
        left = self.bounds["left"]
        width = self.bounds["width"] - self.margin * 2
        self.ui.clear()
        self.value_labels.clear()
        self.sliders.clear()

        self.ui.add(
            UILabel(
                text="Detection Threshold",
                x=left,
                y=self.bounds["top"] - 55,
                width=width,
                font_size=26,
                bold=True,
                text_color=(240, 244, 248),
            )
        )
        self.ui.add(
            UILabel(
                text="Pilih ruang warna dan batas nilai setiap channel.",
                x=left,
                y=self.bounds["top"] - 85,
                width=width,
                font_size=13,
                text_color=(170, 180, 192),
            )
        )

        self._build_color_space_buttons(left, self.bounds["top"] - 155)

        header_y = self.bounds["top"] - 225
        self.ui.add(UILabel("Channel", x=left, y=header_y, width=100, bold=True))
        self.ui.add(UILabel("Minimum", x=left + 115, y=header_y, width=180, bold=True))
        self.ui.add(UILabel("Maximum", x=left + 325, y=header_y, width=180, bold=True))

        initial_min = list(shared.min_ch)
        initial_max = list(shared.max_ch)
        for index, channel_name in enumerate(self.CHANNEL_NAMES):
            y = header_y - 70 - index * 85
            self.ui.add(UILabel(channel_name, x=left, y=y + 5, width=105))

            min_slider = UISlider(
                value=self._channel_value(initial_min, index, 0),
                min_value=0,
                max_value=255,
                step=1,
                x=left + 110,
                y=y,
                width=175,
            )
            max_slider = UISlider(
                value=self._channel_value(initial_max, index, 255),
                min_value=0,
                max_value=255,
                step=1,
                x=left + 320,
                y=y,
                width=175,
            )
            self.sliders.append((min_slider, max_slider))
            value_label = UILabel("", x=left + 500, y=y + 5, width=65, align="right")
            self.value_labels.append(value_label)
            self.ui.add(min_slider)
            self.ui.add(max_slider)
            self.ui.add(value_label)

            @min_slider.event("on_change")
            def on_min_change(event: UIOnChangeEvent, channel=index):
                self._handle_slider_change(channel, changed="min")


            @max_slider.event("on_change")
            def on_max_change(event: UIOnChangeEvent, channel=index):
                self._handle_slider_change(channel, changed="max")

            self._update_value_label(index)

        button_y = self.bounds["bottom"] + 40
        auto_button = UIFlatButton(text="Auto Threshold", x=left, y=button_y, width=180, height=48)
        save_button = UIFlatButton(
            text="Save",
            x=self.bounds["right"] - 150,
            y=button_y,
            width=150,
            height=48,
        )
        self.ui.add(auto_button)
        self.ui.add(save_button)
        self.status_label = UILabel(
            "",
            x=left,
            y=button_y + 58,
            width=width,
            font_size=13,
            text_color=(120, 210, 160),
        )
        self.ui.add(self.status_label)

        @auto_button.event("on_click")
        def on_auto_threshold(event):
            self.object_detection.auto_threshold = True
            self.object_detection.ROI_calib = [None, None, None, None]
            self.object_detection.mouse_pos = (None, None)

        @save_button.event("on_click")
        def on_save(event):
            self._save_thresholds()
            if self.on_save is not None:
                self.on_save()
            self._set_status("Pengaturan threshold tersimpan.", (120, 210, 160))

    def _build_color_space_buttons(self, x: float, y: float):
        button_width = 98
        for index, color_space in enumerate(self.COLOR_SPACES):
            button = UIFlatButton(
                text=color_space,
                x=x + index * (button_width + 8),
                y=y,
                width=button_width,
                height=42,
            )
            self.ui.add(button)

            @button.event("on_click")
            def on_color_space_click(event, selected=color_space):
                shared.color_space = selected
                self._set_status(f"Color space {selected} dipilih.", (120, 190, 235))

    @staticmethod
    def _channel_value(values: list, index: int, fallback: int) -> int:
        try:
            return max(0, min(255, int(values[index])))
        except (IndexError, TypeError, ValueError):
            return fallback
        
    def _handle_slider_change(self, channel: int, changed: str):
        if self._updating_sliders:
            return

        minimum, maximum = self.sliders[channel]

        self._updating_sliders = True
        try:
            if changed == "min" and minimum.value > maximum.value:
                minimum.value = maximum.value

            elif changed == "max" and maximum.value < minimum.value:
                maximum.value = minimum.value

            self._update_value_label(channel)

            shared.min_ch[channel] = int(minimum.value)
            shared.max_ch[channel] = int(maximum.value)
        finally:
            self._updating_sliders = False

    def _save_thresholds(self):
        self._set_status("Menyimpan pengaturan threshold...", (200, 200, 200))
        
    def _update_value_label(self, channel: int):
        minimum, maximum = self.sliders[channel]
        # Pastikan format teks sesuai yang Anda inginkan
        new_text = f"{int(minimum.value)} - {int(maximum.value)}" 
        
        # HANYA update jika teks benar-benar berubah untuk menghindari lag render
        if self.value_labels[channel].text != new_text:
            self.value_labels[channel].text = new_text

    def _sync_sliders_from_detection(self):
        self._updating_sliders = True
        try:
            for index, (minimum, maximum) in enumerate(self.sliders):
                new_min = self._channel_value(shared.min_ch, index, 0)
                new_max = self._channel_value(shared.max_ch, index, 255)
                
                # Hanya update value UI jika ada perubahan angka
                if minimum.value != new_min:
                    minimum.value = new_min
                if maximum.value != new_max:
                    maximum.value = new_max
                
                if minimum.value > maximum.value:
                    minimum.value = maximum.value
                
                self._update_value_label(index)
        finally:
            self._updating_sliders = False

    def _set_status(self, message: str, color: tuple[int, int, int]):
        if self.status_label is not None:
            self.status_label.text = message
            self.status_label.text_color = color
            
    def on_update(self, delta_time: float):
        if not shared.is_slider_sync and not self._updating_sliders:
            self._sync_sliders_from_detection()
            shared.is_slider_sync = True

    def on_draw(self):
        self.clear()
        super().on_draw()
