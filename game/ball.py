import pygame
import random
from typing import Tuple

# Default speeds (per-frame at 60 FPS)
DEFAULT_SPEED_X = 5.0
DEFAULT_SPEED_Y = 3.0

class Ball:
    def __init__(self, x: int, y: int, width: int, height: int, screen_width: int, screen_height: int,
                speed_x: float = DEFAULT_SPEED_X, speed_y: float = DEFAULT_SPEED_Y):
        self.original_x = float(x)
        self.original_y = float(y)

        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.base_speed_x = float(speed_x)
        self.base_speed_y = float(speed_y)
        self.velocity_x = random.choice([-1.0, 1.0]) * self.base_speed_x
        self.velocity_y = random.choice([-1.0, 1.0]) * self.base_speed_y

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Vertical bounce
        if self.y <= 0:
            self.y = 0
            self.velocity_y *= -1
            return "wall"
        elif self.y + self.height >= self.screen_height:
            self.y = self.screen_height - self.height
            self.velocity_y *= -1
            return "wall"
        return None

    def check_collision(self, player, ai):
        ball_rect = self.rect()
        # Player collision (left)
        if ball_rect.colliderect(player.rect()):
            if self.velocity_x < 0:
                self.x = player.x + player.width
                self.velocity_x = abs(self.velocity_x)
                self._add_spin(player)
                return "paddle"
        # AI collision (right)
        elif ball_rect.colliderect(ai.rect()):
            if self.velocity_x > 0:
                self.x = ai.x - self.width
                self.velocity_x = -abs(self.velocity_x)
                self._add_spin(ai)
                return "paddle"
        return None

    def _add_spin(self, paddle):
        paddle_center = paddle.y + paddle.height / 2.0
        ball_center = self.y + self.height / 2.0
        offset = (ball_center - paddle_center) / (paddle.height / 2.0)
        max_spin = self.base_speed_y * 1.25
        self.velocity_y += offset * max_spin
        max_vy = max_spin * 2.0
        if self.velocity_y > max_vy:
            self.velocity_y = max_vy
        elif self.velocity_y < -max_vy:
            self.velocity_y = -max_vy

    def reset(self, direction: float = None):
        self.x = float(self.original_x)
        self.y = float(self.original_y)
        if direction is None:
            direction = random.choice([-1.0, 1.0])
        self.velocity_x = direction * self.base_speed_x
        self.velocity_y = random.choice([-1.0, 1.0]) * self.base_speed_y

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)