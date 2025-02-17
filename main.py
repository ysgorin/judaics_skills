import pygame
import pandas as pd
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)
LIGHT_BLUE = (173, 216, 230)
FONT_PATH = "assets/PressStart2P-Regular.ttf"
BACKGROUND_PATH = "assets/background.png"
CSV_PATH = "data.csv"

# Load CSV
data = pd.read_csv(CSV_PATH)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chumash Vocabulary Quiz")

# Load background image
background = pygame.image.load(BACKGROUND_PATH)

# Load font
font = pygame.font.Font(FONT_PATH, 12)

# Button class
class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = BLUE

    def draw(self, screen):
        # Change color on hover
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = LIGHT_BLUE
        else:
            color = self.color

        pygame.draw.rect(screen, color, self.rect)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

class Quiz:
    def __init__(self):
        self.questions = data.to_dict(orient="records")
        self.index = 0
        self.correct_count = 0
        self.show_result = False
        self.wrong_message = ""  # Store wrong answer message
        self.message_timer = 0  # Timer for message display
        self.load_question()

    def load_question(self):
        """Load current question from CSV data"""
        self.current_question = self.questions[self.index]
        self.image = pygame.image.load(self.current_question["image_path"])
        self.correct_answer = self.current_question["answer"]
        choices = [
            self.correct_answer,
            self.current_question["wrong1"],
            self.current_question["wrong2"],
            self.current_question["wrong3"],
        ]
        random.shuffle(choices)  # Randomize answers
        self.choices = choices
        self.answered_correctly = False  # Reset flag for this question
        self.first_attempt = True  # Reset first attempt flag for new question
        self.wrong_message = ""  # Clear wrong message


    def check_answer(self, selected_answer):
        """Handle answer selection"""
        if not self.answered_correctly:
            if selected_answer == self.correct_answer:
                if self.first_attempt:
                    self.correct_count += 1  # Only count if correct on first try
                self.answered_correctly = True
                self.wrong_message = ""  # Clear wrong message
                self.next_question()
            else:
                self.wrong_message = "Wrong answer, try again."
                self.message_timer = pygame.time.get_ticks()  # Start timer
                self.first_attempt = False  # Mark that the first attempt was incorrect

    def next_question(self):
        """Move to next question or show results"""
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.load_question()
        else:
            self.show_result = True  # End of quiz

    def restart_quiz(self):
        """Restart the quiz"""
        self.index = 0
        self.correct_count = 0
        self.show_result = False
        self.wrong_message = ""
        self.load_question()

    def draw(self, screen):
        """Draw question or results on the screen"""
        screen.blit(background, (0, 0))  # Draw background

        if self.show_result:
            # Show final score
            result_text = f"Score: {self.correct_count}/{len(self.questions)}"
            percentage = f"{(self.correct_count / len(self.questions)) * 100:.1f}%"
            text_surface = font.render(result_text, True, WHITE)
            percentage_surface = font.render(percentage, True, WHITE)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 3))
            screen.blit(percentage_surface, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 3 + 30))
            retry_button.draw(screen)
        else:
            # Draw word image (top 2/3 of screen)
            img_rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(self.image, img_rect)

            # Draw answer choices in four quadrants (bottom 1/3 of screen)
            btn_width, btn_height = 300, 50
            positions = [
                (100, 420),
                (400, 420),
                (100, 500),
                (400, 500),
            ]
            for i, choice in enumerate(self.choices):
                button = Button(positions[i][0], positions[i][1], btn_width, btn_height, choice,
                                lambda c=choice: self.check_answer(c))
                button.draw(screen)

            # Display wrong answer message in red
            if self.wrong_message:
                error_font = pygame.font.Font(FONT_PATH, 18)
                error_surface = error_font.render(self.wrong_message, True, (255, 0, 0))
                error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
                screen.blit(error_surface, error_rect)

                # Hide message after 1.5 seconds
                if pygame.time.get_ticks() - self.message_timer > 1500:
                    self.wrong_message = ""

# Start screen
def start_screen():
    screen.blit(background, (0, 0))
    title_text = font.render("Hebrew Grammar Quiz", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3))
    start_button.draw(screen)
    pygame.display.flip()

# Game loop
def main():
    global start_button, retry_button
    running = True
    quiz = None
    game_started = False

    # Create buttons
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "Start", lambda: start_quiz())
    retry_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, "Retry", lambda: quiz.restart_quiz())

    def start_quiz():
        nonlocal quiz, game_started
        quiz = Quiz()
        game_started = True

    while running:
        screen.fill(WHITE)
        if not game_started:
            start_screen()
        else:
            quiz.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_started:
                    start_button.check_click(event)
                elif quiz.show_result:
                    retry_button.check_click(event)
                else:
                    for i, choice in enumerate(quiz.choices):
                        x, y = (100 if i % 2 == 0 else 400), (420 if i < 2 else 500)
                        btn_rect = pygame.Rect(x, y, 300, 50)
                        if btn_rect.collidepoint(event.pos):
                            quiz.check_answer(choice)
                            if quiz.answered_correctly:
                                quiz.next_question()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()