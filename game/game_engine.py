import pygame
import random
from .paddle import Paddle
from .ball import Ball
from typing import Optional

WHITE = (255, 255, 255)

def make_beep(freq=440, duration_ms=100, volume=0.2):
    """
    Return a pygame.mixer.Sound object of a simple tone.
    If mixer isn't available this will raise; caller should handle exceptions.
    """
    import math
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000.0)
    buffer = []
    for s in range(n_samples):
        t = float(s) / sample_rate
        sample = 32767 * 0.5 * math.sin(2.0 * math.pi * freq * t)
        buffer.append(int(sample))
    import array
    arr = array.array('h', buffer)
    sound = pygame.mixer.Sound(arr)
    sound.set_volume(volume)
    return sound

class GameEngine:
    def __init__(self, width: int, height: int, winning_score: int = 5):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - self.paddle_height // 2,
                            self.paddle_width, self.paddle_height, speed=7)
        self.ai = Paddle(width - 10 - self.paddle_width, height // 2 - self.paddle_height // 2,
                        self.paddle_width, self.paddle_height, speed=6.0)

        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.winning_score = winning_score

        self.game_over = False
        self.awaiting_replay_choice = False

        self.keys_down = set()

        self.font = pygame.font.SysFont("Arial", 30)

        self.sounds = {}
        try:
            self.sounds['paddle'] = make_beep(freq=800, duration_ms=60, volume=0.15)
            self.sounds['wall'] = make_beep(freq=400, duration_ms=60, volume=0.12)
            self.sounds['score'] = make_beep(freq=1200, duration_ms=200, volume=0.2)
        except Exception:
            self.sounds = {'paddle': None, 'wall': None, 'score': None}

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            # Handle replay choices when game is over
            if self.awaiting_replay_choice:
                if event.key == pygame.K_3:
                    self.start_new_match(3)
                elif event.key == pygame.K_5:
                    self.start_new_match(5)
                elif event.key == pygame.K_7:
                    self.start_new_match(7)
                return
            
            # Normal gameplay controls
            if event.key == pygame.K_w:
                self.player.set_move_up(True)
            elif event.key == pygame.K_s:
                self.player.set_move_down(True)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.player.set_move_up(False)
            elif event.key == pygame.K_s:
                self.player.set_move_down(False)

    def handle_input(self):
        if self.player._move_up:
            self.player.move(-self.player.speed, self.height)
        if self.player._move_down:
            self.player.move(self.player.speed, self.height)

    def update(self):
        if self.game_over:
            return

        evt = self.ball.move()
        if evt == "wall":
            self._play_sound('wall')

        col_evt = self.ball.check_collision(self.player, self.ai)
        if col_evt == "paddle":
            self._play_sound('paddle')

        ball_rect = self.ball.rect()
        scored = False
        if ball_rect.right < 0:
            self.ai_score += 1
            self._play_sound('score')
            scored = True
            self.ball.reset(direction=1.0)
        elif ball_rect.left > self.width:
            self.player_score += 1
            self._play_sound('score')
            scored = True
            self.ball.reset(direction=-1.0)

        if scored:
            if self.player_score >= self.winning_score or self.ai_score >= self.winning_score:
                self.game_over = True
                self.awaiting_replay_choice = True

        if not self.game_over:
            self.ai.auto_track(self.ball, self.height)

    def _play_sound(self, name: str):
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def render(self, screen: pygame.Surface):
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4 - player_text.get_width() // 2, 20))
        screen.blit(ai_text, (self.width * 3 // 4 - ai_text.get_width() // 2, 20))

        if self.game_over:
            overlay_font = pygame.font.SysFont("Arial", 36)
            small_font = pygame.font.SysFont("Arial", 24)
            
            if self.player_score > self.ai_score:
                winner_msg = "Player Wins!"
            else:
                winner_msg = "AI Wins!"
            
            if self.awaiting_replay_choice:
                msg = winner_msg
                options_msg = "Choose Match Format:"
                option_lines = [
                    "Press 3 for Best of 3",
                    "Press 5 for Best of 5",
                    "Press 7 for Best of 7",
                    "Press ESC to Exit"
                ]
                
                # Render winner message
                text = overlay_font.render(msg, True, WHITE)
                rect = text.get_rect(center=(self.width // 2, self.height // 2 - 80))
                
                # Render options
                options_text = small_font.render(options_msg, True, WHITE)
                options_rect = options_text.get_rect(center=(self.width // 2, self.height // 2 - 20))
                
                # Calculate background size
                max_width = max(rect.width, options_rect.width, 400)
                total_height = rect.height + options_rect.height + len(option_lines) * 30 + 60
                
                # Draw semi-transparent background
                s = pygame.Surface((max_width + 40, total_height))
                s.set_alpha(180)
                s.fill((0, 0, 0))
                screen.blit(s, (self.width // 2 - max_width // 2 - 20, rect.y - 20))
                
                # Draw all text
                screen.blit(text, rect)
                screen.blit(options_text, options_rect)
                
                y_offset = options_rect.bottom + 15
                for line in option_lines:
                    line_text = small_font.render(line, True, WHITE)
                    line_rect = line_text.get_rect(center=(self.width // 2, y_offset))
                    screen.blit(line_text, line_rect)
                    y_offset += 30
            else:
                msg = winner_msg + " Press R to Restart or ESC to Quit"
                text = overlay_font.render(msg, True, WHITE)
                rect = text.get_rect(center=(self.width // 2, self.height // 2))
                s = pygame.Surface((rect.width + 20, rect.height + 20))
                s.set_alpha(160)
                s.fill((0, 0, 0))
                screen.blit(s, (rect.x - 10, rect.y - 10))
                screen.blit(text, rect)

    def reset_match(self):
        """Reset scores and ball to start a new match."""
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.awaiting_replay_choice = False
        self.ball.reset(direction=random.choice([-1.0, 1.0]))
    
    def start_new_match(self, best_of: int):
        """Start a new match with specified format (best of N)."""
        self.winning_score = (best_of + 1) // 2  # Best of 3 = 2 wins, Best of 5 = 3 wins, Best of 7 = 4 wins
        self.reset_match()
