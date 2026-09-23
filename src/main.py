import arcade
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from include.entity import PlayerPaddle, EnemyPaddle, Puck

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Air Hockey Arcade"

# State permainan
STATE_SERVE_PLAYER = "SERVE_PLAYER"  # Giliran player memukul bola di tengah
STATE_SERVE_ENEMY = "SERVE_ENEMY"    # Giliran musuh memukul bola di tengah
STATE_PLAYING = "PLAYING"            # Bola aktif dalam permainan
STATE_GOAL = "GOAL"                  # Sesaat setelah gol dicetak

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window.background_color = (18, 22, 28)

        # game area
        self.margin = 25
        self.goal_width = 180
        self.bounds = {
            "left": self.margin,
            "right": SCREEN_WIDTH - self.margin,
            "bottom": self.margin,
            "top": SCREEN_HEIGHT - self.margin,
            "width": SCREEN_WIDTH,
            "height": SCREEN_HEIGHT,
            "center_x": SCREEN_WIDTH / 2,
            "center_y": SCREEN_HEIGHT / 2,
            "goal_left": (SCREEN_WIDTH - self.goal_width) / 2,
            "goal_right": (SCREEN_WIDTH + self.goal_width) / 2,
        }

        # Skor
        self.player_score = 0
        self.enemy_score = 0

        # State dan timer
        self.state = STATE_SERVE_PLAYER
        self.last_scorer = None
        self.goal_timer = 0.0

        # Entity
        self.player = PlayerPaddle(self.bounds["center_x"], self.bounds["bottom"] + 120, radius=38)
        self.enemy = EnemyPaddle(self.bounds["center_x"], self.bounds["top"] - 120, radius=38)
        self.puck = Puck(self.bounds["center_x"], self.bounds["center_y"], radius=20)

        # Sprite list
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.player)
        self.sprite_list.append(self.enemy)
        self.sprite_list.append(self.puck)

        self.mouse_x = self.player.center_x
        self.mouse_y = self.player.center_y

    def reset_round(self, next_state: str):
        """Mereset posisi puck dan paddle ke posisi siap serve."""
        self.state = next_state
        self.puck.reset(self.bounds["center_x"], self.bounds["center_y"])
        
        self.enemy.center_x = self.bounds["center_x"]
        self.enemy.center_y = self.bounds["top"] - 120
        self.enemy.prev_x = self.enemy.center_x
        self.enemy.prev_y = self.enemy.center_y
        self.enemy.vx = 0.0
        self.enemy.vy = 0.0

    def on_draw(self):
        self.window.clear()
        self.draw_arena()
        self.sprite_list.draw()
        self.draw_paddle_accents()
        self.draw_ui()

    def draw_arena(self):
        b = self.bounds

        # Color
        table_border_color = (40, 80, 120)
        center_line_color = (180, 50, 60, 200)
        center_circle_color = (180, 50, 60, 160)

        # center
        arcade.draw_line(b["left"], b["center_y"], b["right"], b["center_y"], center_line_color, line_width=3)
        arcade.draw_circle_outline(b["center_x"], b["center_y"], 65, center_circle_color, border_width=3)
        arcade.draw_circle_filled(b["center_x"], b["center_y"], 6, arcade.color.DARK_RED)

        # enemy goal area
        enemy_goal_rect = arcade.rect.LRBT(b["goal_left"], b["goal_right"], b["top"], b["top"] + 15)
        arcade.draw_rect_filled(enemy_goal_rect, (220, 50, 50, 120))
        arcade.draw_rect_outline(enemy_goal_rect, arcade.color.CRIMSON, border_width=2)

        # player goal area
        player_goal_rect = arcade.rect.LRBT(b["goal_left"], b["goal_right"], b["bottom"] - 15, b["bottom"])
        arcade.draw_rect_filled(player_goal_rect, (50, 150, 255, 120))
        arcade.draw_rect_outline(player_goal_rect, arcade.color.ELECTRIC_CYAN, border_width=2)

        # walls
        arcade.draw_line(b["left"], b["bottom"], b["left"], b["top"], table_border_color, line_width=4)
        arcade.draw_line(b["right"], b["bottom"], b["right"], b["top"], table_border_color, line_width=4)
        arcade.draw_line(b["left"], b["top"], b["goal_left"], b["top"], table_border_color, line_width=4)
        arcade.draw_line(b["goal_right"], b["top"], b["right"], b["top"], table_border_color, line_width=4)
        arcade.draw_line(b["left"], b["bottom"], b["goal_left"], b["bottom"], table_border_color, line_width=4)
        arcade.draw_line(b["goal_right"], b["bottom"], b["right"], b["bottom"], table_border_color, line_width=4)

        # Tiang gawang (goal posts) kecil
        arcade.draw_circle_filled(b["goal_left"], b["top"], 5, arcade.color.WHITE)
        arcade.draw_circle_filled(b["goal_right"], b["top"], 5, arcade.color.WHITE)
        arcade.draw_circle_filled(b["goal_left"], b["bottom"], 5, arcade.color.WHITE)
        arcade.draw_circle_filled(b["goal_right"], b["bottom"], 5, arcade.color.WHITE)

    def draw_paddle_accents(self):
        # Aksen cincin dalam untuk mallet player & enemy agar tampak seperti pemukul air hockey
        arcade.draw_circle_outline(self.player.center_x, self.player.center_y, self.player.radius * 0.5, arcade.color.WHITE, border_width=2)
        arcade.draw_circle_filled(self.player.center_x, self.player.center_y, self.player.radius * 0.25, arcade.color.NAVY_BLUE)

        arcade.draw_circle_outline(self.enemy.center_x, self.enemy.center_y, self.enemy.radius * 0.5, arcade.color.WHITE, border_width=2)
        arcade.draw_circle_filled(self.enemy.center_x, self.enemy.center_y, self.enemy.radius * 0.25, arcade.color.DARK_RED)

        # Aksen puck
        arcade.draw_circle_outline(self.puck.center_x, self.puck.center_y, self.puck.radius * 0.65, arcade.color.ORANGE, border_width=2)

    def draw_ui(self):
        # Papan Skor
        arcade.draw_text(
            f"ENEMY: {self.enemy_score}",
            self.bounds["left"] + 15,
            SCREEN_HEIGHT - 48,
            arcade.color.RED,
            font_size=15,
            bold=True,
            anchor_x="left",
            anchor_y="center"
        )

        arcade.draw_text(
            f"PLAYER: {self.player_score}",
            self.bounds["left"] + 15,
            50,
            arcade.color.CYAN,
            font_size=15,
            bold=True,
            anchor_x="left",
            anchor_y="center"
        )

        # Status Permainan / Petunjuk
        if self.state == STATE_SERVE_PLAYER:
            msg = "GILIRAN PLAYER: Pukul bola di tengah untuk memulai!"
            col = arcade.color.CYAN
            arcade.draw_text(msg, SCREEN_WIDTH / 2, self.bounds["center_y"] - 100, col, font_size=12, bold=True, anchor_x="center", anchor_y="center")
        elif self.state == STATE_SERVE_ENEMY:
            msg = "GILIRAN MUSUH: Musuh memulai lemparan pertama..."
            col = arcade.color.ORANGE
            arcade.draw_text(msg, SCREEN_WIDTH / 2, self.bounds["center_y"] + 100, col, font_size=12, bold=True, anchor_x="center", anchor_y="center")
        elif self.state == STATE_GOAL:
            scorer_text = "PLAYER MENCETAK GOL!" if self.last_scorer == "PLAYER" else "MUSUH MENCETAK GOL!"
            col = arcade.color.GOLD if self.last_scorer == "PLAYER" else arcade.color.CRIMSON
            arcade.draw_text("GOAL!!!", SCREEN_WIDTH / 2, self.bounds["center_y"] + 25, col, font_size=28, bold=True, anchor_x="center", anchor_y="center")
            arcade.draw_text(scorer_text, SCREEN_WIDTH / 2, self.bounds["center_y"] - 20, arcade.color.WHITE, font_size=14, bold=True, anchor_x="center", anchor_y="center")

        # Petunjuk tombol di pojok kanan bawah
        arcade.draw_text(
            "[R] Reset Skor | [ESC] Keluar",
            self.bounds["right"] - 15,
            15,
            (120, 140, 160),
            font_size=10,
            anchor_x="right",
            anchor_y="baseline"
        )

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        print(f"Mouse moved to ({x}, {y})")
        self.mouse_x = x
        self.mouse_y = y

    def on_update(self, delta_time: float):
        # 1. Update Player Paddle mengikuti mouse (tetap di separuh bawah)
        self.player.move_to(self.mouse_x, self.mouse_y, self.bounds)
        self.player.update_velocity(delta_time)

        # 2. Update Enemy Paddle menggunakan AI
        self.enemy.ai_update(self.puck, self.state, self.bounds)
        self.enemy.update_velocity(delta_time)

        # 3. Penanganan State Permainan
        if self.state == STATE_GOAL:
            self.goal_timer -= delta_time
            if self.goal_timer <= 0:
                # Sesuai aturan: ketika player menang/skor, bola pertama ronde baru diberikan kepada musuh
                if self.last_scorer == "PLAYER":
                    self.reset_round(STATE_SERVE_ENEMY)
                else:
                    self.reset_round(STATE_SERVE_PLAYER)
            return

        # Cek tumbukan Player dengan Puck
        player_hit = self.puck.check_collision_with_paddle(self.player)
        # Cek tumbukan Enemy dengan Puck
        enemy_hit = self.puck.check_collision_with_paddle(self.enemy)

        # Transisi dari SERVE ke PLAYING saat bola terpukul
        if self.state == STATE_SERVE_PLAYER:
            if player_hit or math.hypot(self.puck.vx, self.puck.vy) > 1.0:
                self.state = STATE_PLAYING
        elif self.state == STATE_SERVE_ENEMY:
            if enemy_hit or self.puck.center_y < self.bounds["center_y"] - 10:
                self.state = STATE_PLAYING

        # 4. Update Fisika Puck & Cek Gol
        goal_result = self.puck.update_physics(self.bounds)
        if goal_result == "PLAYER_SCORED":
            self.player_score += 1
            self.last_scorer = "PLAYER"
            self.state = STATE_GOAL
            self.goal_timer = 1.3
        elif goal_result == "ENEMY_SCORED":
            self.enemy_score += 1
            self.last_scorer = "ENEMY"
            self.state = STATE_GOAL
            self.goal_timer = 1.3

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        elif symbol == arcade.key.R:
            # Reset total skor dan mulai serve awal dari player
            self.player_score = 0
            self.enemy_score = 0
            self.reset_round(STATE_SERVE_PLAYER)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/60, vsync=True)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()