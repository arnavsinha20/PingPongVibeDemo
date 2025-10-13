import pygame
from typing import Union

class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int, speed: Union[int, float] = 7):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.speed = float(speed)

        self._move_up = False
        self._move_down = False

    def set_move_up(self, val: bool):
        self._move_up = bool(val)

    def set_move_down(self, val: bool):
        self._move_down = bool(val)

    def move(self, dy: float, screen_height: int):
        self.y += dy
        self.y = max(0.0, min(self.y, float(screen_height - self.height)))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def auto_track(self, ball, screen_height: int):
        ball_center = ball.y + ball.height / 2.0
        paddle_center = self.y + self.height / 2.0
        delta = ball_center - paddle_center
        if abs(delta) < self.speed:
            self.move(delta, screen_height)
        else:
            step = self.speed if delta > 0 else -self.speed
            self.move(step, screen_height)