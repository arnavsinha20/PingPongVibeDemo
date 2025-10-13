import pygame
from game.game_engine import GameEngine

# Screen dimensions and colors
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
FPS = 60

def main():
    # Initialize pygame and subsystems
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        # If mixer fails to init (no audio device), continue without sound
        pass
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ping Pong - Interactive")

    clock = pygame.time.Clock()

    # Create engine after pygame init
    engine = GameEngine(WIDTH, HEIGHT)

    running = True
    try:
        while running:
            # Cap framerate and get elapsed ms (dt)
            dt = clock.tick(FPS)

            # Event handling (quit, restart)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # ESC to quit
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # R to restart match when game over (also works while playing to reset)
                    elif event.key == pygame.K_r:
                        engine.reset_match()
                # Give engine a chance to react to lower-level events if needed
                engine.handle_event(event)

            # Per-frame input handling (continuous)
            engine.handle_input()

            # Game update/render
            engine.update()
            screen.fill(BLACK)
            engine.render(screen)

            pygame.display.flip()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()