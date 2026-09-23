import arcade
import math

class Paddle(arcade.Sprite):
    def __init__(self, x: float, y: float, radius: float, color: tuple[int, int, int]):
        super().__init__()
        self.radius = radius
        self.center_x = x
        self.center_y = y
        self.prev_x = x
        self.prev_y = y
        self.vx = 0.0
        self.vy = 0.0
        self.color_tint = color
        
        diameter = int(radius * 2)
        self.texture = arcade.make_circle_texture(diameter, color)

    def update_velocity(self, dt: float = 1/60):
        if dt > 0:
            self.vx = (self.center_x - self.prev_x) / dt
            self.vy = (self.center_y - self.prev_y) / dt
        self.prev_x = self.center_x
        self.prev_y = self.center_y

    def clamp_position(self, min_x: float, max_x: float, min_y: float, max_y: float):
        self.center_x = max(min_x, min(max_x, self.center_x))
        self.center_y = max(min_y, min(max_y, self.center_y))


class PlayerPaddle(Paddle):
    def __init__(self, x: float, y: float, radius: float = 38):
        super().__init__(x, y, radius, arcade.color.ELECTRIC_CYAN)

    def move_to(self, target_x: float, target_y: float, bounds: dict):
        self.center_x = target_x
        self.center_y = target_y
        self.clamp_position(
            bounds["left"] + self.radius,
            bounds["right"] - self.radius,
            bounds["bottom"] + self.radius,
            bounds["center_y"] - self.radius - 2
        )


class EnemyPaddle(Paddle):
    def __init__(self, x: float, y: float, radius: float = 38):
        super().__init__(x, y, radius, arcade.color.CRIMSON)
        self.max_speed = 3.0
        self.home_x = x
        self.home_y = y

    def ai_update(self, puck: "Puck", state: str, bounds: dict):
        target_x = self.home_x
        target_y = self.home_y

        if state == "SERVE_ENEMY":
            target_x = puck.center_x
            target_y = puck.center_y + self.radius * 0.5
        elif state == "SERVE_PLAYER":
            target_x = bounds["center_x"]
            target_y = self.home_y
        else:
            if puck.center_y > bounds["center_y"]:
                if puck.center_y > self.center_y:
                    target_x = bounds["center_x"]
                    target_y = bounds["top"] - self.radius - 30
                else:
                    target_x = puck.center_x
                    target_y = puck.center_y + self.radius * 0.6
            else:
                ratio = (puck.center_x - bounds["center_x"]) / (bounds["width"] / 2)
                target_x = bounds["center_x"] + ratio * 80
                target_y = self.home_y

        min_enemy_y = bounds["center_y"] + self.radius + 2
        if state == "SERVE_ENEMY":
            min_enemy_y = bounds["center_y"] + self.radius * 0.5

        target_x = max(bounds["left"] + self.radius, min(bounds["right"] - self.radius, target_x))
        target_y = max(min_enemy_y, min(bounds["top"] - self.radius, target_y))
        
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        dist = math.hypot(dx, dy)

        if dist > 0.1:
            speed = min(dist, self.max_speed)
            self.center_x += (dx / dist) * speed
            self.center_y += (dy / dist) * speed

        self.clamp_position(
            bounds["left"] + self.radius,
            bounds["right"] - self.radius,
            min_enemy_y,
            bounds["top"] - self.radius
        )


class Puck(arcade.Sprite):
    def __init__(self, x: float, y: float, radius: float = 20):
        super().__init__()
        self.radius = radius
        self.center_x = x
        self.center_y = y
        self.vx = 0.0
        self.vy = 0.0
        self.friction = 0.993
        self.max_speed = 22.0
        
        diameter = int(radius * 2)
        self.texture = arcade.make_circle_texture(diameter, arcade.color.YELLOW)

    def reset(self, x: float, y: float):
        self.center_x = x
        self.center_y = y
        self.vx = 0.0
        self.vy = 0.0

    def update_physics(self, bounds: dict) -> str | None:
        """
        Update posisi puck, pantulan dinding, dan cek gol.
        Return 'PLAYER_SCORED' jika masuk gawang atas (musuh),
        'ENEMY_SCORED' jika masuk gawang bawah (player),
        atau None jika permainan berlanjut.
        """
        
        self.vx *= self.friction
        self.vy *= self.friction
        
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed
        elif speed < 0.05:
            self.vx = 0.0
            self.vy = 0.0

        self.center_x += self.vx
        self.center_y += self.vy

        goal_left = bounds["goal_left"]
        goal_right = bounds["goal_right"]

        if self.center_x - self.radius < bounds["left"]:
            self.center_x = bounds["left"] + self.radius
            self.vx = abs(self.vx) * 0.95
        elif self.center_x + self.radius > bounds["right"]:
            self.center_x = bounds["right"] - self.radius
            self.vx = -abs(self.vx) * 0.95

        if self.center_y + self.radius > bounds["top"]:
            if goal_left < self.center_x < goal_right:
                if self.center_y > bounds["top"] + self.radius:
                    return "PLAYER_SCORED"
            else:
                self.center_y = bounds["top"] - self.radius
                self.vy = -abs(self.vy) * 0.95

        if self.center_y - self.radius < bounds["bottom"]:
            if goal_left < self.center_x < goal_right:
                if self.center_y < bounds["bottom"] - self.radius:
                    return "ENEMY_SCORED"
            else:
                self.center_y = bounds["bottom"] + self.radius
                self.vy = abs(self.vy) * 0.95

        return None

    def check_collision_with_paddle(self, paddle: Paddle) -> bool:
        dx = self.center_x - paddle.center_x
        dy = self.center_y - paddle.center_y
        dist = math.hypot(dx, dy)
        min_dist = self.radius + paddle.radius

        if dist < min_dist:
            if dist == 0:
                nx, ny = 0.0, 1.0
                dist = 0.01
            else:
                nx = dx / dist
                ny = dy / dist

            self.center_x = paddle.center_x + nx * min_dist
            self.center_y = paddle.center_y + ny * min_dist

            v_rel_x = self.vx - paddle.vx * 0.016
            v_rel_y = self.vy - paddle.vy * 0.016
            vel_along_normal = v_rel_x * nx + v_rel_y * ny

            restitution = 1.2
            impulse = -(1 + restitution) * vel_along_normal

            paddle_push = (paddle.vx * 0.016 * nx + paddle.vy * 0.016 * ny)
            if paddle_push > 0:
                impulse += paddle_push * 1.5

            if impulse < 4.0:
                impulse = 6.0

            self.vx = nx * impulse + (paddle.vx * 0.016 * 0.4)
            self.vy = ny * impulse + (paddle.vy * 0.016 * 0.4)

            hit_speed = math.hypot(self.vx, self.vy)
            if hit_speed < 5.0:
                self.vx = nx * 6.0
                self.vy = ny * 6.0

            return True
        return False