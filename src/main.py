import arcade
import include.shared as shared
import json
import os
from include.game_view import GameView
from include.image_processing import ObjectDetection
from include.detection_settings_view import DetectionSettings
from threading import Thread

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Hockey"

shared.player_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.25)
shared.is_calib = True

window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/60)
game_view = GameView(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
object_detection = ObjectDetection()
detection_settings_view = DetectionSettings(
    screen_width=SCREEN_WIDTH,
    screen_height=SCREEN_HEIGHT,
    object_detection=object_detection,
)

def thread_pcv_loop():
    object_detection.run()

def main():
    # load save
    path = "./config/saved_setting.json"
    
    if os.path.exists(path):
        with open(path, "r") as f:
            saved_data = json.load(f)
            shared.min_ch = saved_data.get("min_ch", [0, 0, 0])
            shared.max_ch = saved_data.get("max_ch", [255, 255, 255])
            shared.color_space = saved_data.get("color_space", "RGB")
    
    pcv_thread = Thread(target=thread_pcv_loop)
    pcv_thread.start()
    window.show_view(game_view)
    # window.show_view(detection_settings_view)
    arcade.run()
    pcv_thread.join()


if __name__ == "__main__":
    main()