import arcade
import include.shared as shared
from include.game_view import GameView
from include.image_processing import ObjectDetection
from include.detection_settings import DetectionSettings
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
    pcv_thread = Thread(target=thread_pcv_loop)
    pcv_thread.start()
    # window.show_view(game_view)
    window.show_view(detection_settings_view)
    arcade.run()
    pcv_thread.join()


if __name__ == "__main__":
    main()