import pygame
import random
import math
import pyttsx3
import threading
import queue

# Initialize Pygame
pygame.init()

# Initialize pyttsx3 for speech generation
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Set speaking rate

# Screen dimensions (smaller 9:16 aspect ratio for vertical phone-like screen)
WIDTH, HEIGHT = 400, 711
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Confetti Simulation and 3D Wiggle Subtitle Animation")

# Colors for the confetti
COLORS = [
    (255, 0, 255),    # Pink
    (0, 234, 255),    # Light Blue
    (255, 140, 0),    # Orange
    (0, 255, 153),    # Greenish
    (255, 255, 0),    # Yellow
    (173, 216, 230)   # Light Cyan
]

# Confetti piece class
class ConfettiPiece:
    def __init__(self):
        self.width = random.randint(5, 15)
        self.height = random.randint(10, 30)
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.color = random.choice(COLORS)
        self.speed = random.uniform(2, 5)
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.swing_amplitude = random.uniform(10, 50)
        self.swing_frequency = random.uniform(0.005, 0.02)
        self.start_x = self.x

    def fall(self):
        # Move the piece down and rotate it
        self.y += self.speed
        self.angle += self.rotation_speed
        self.x = self.start_x + math.sin(self.y * self.swing_frequency) * self.swing_amplitude
        if self.y > HEIGHT:
            # Reset the piece to the top after it falls off screen
            self.y = random.randint(-HEIGHT, 0)
            self.x = random.randint(0, WIDTH)
            self.start_x = self.x
            self.speed = random.uniform(2, 5)
            self.swing_amplitude = random.uniform(10, 50)
            self.swing_frequency = random.uniform(0.005, 0.02)
            self.angle = random.uniform(0, 360)
            self.rotation_speed = random.uniform(-5, 5)

    def draw(self, screen):
        # Draw the confetti piece with rotation
        rect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(rect, self.color, [0, 0, self.width, self.height])
        rotated_surface = pygame.transform.rotate(rect, self.angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rotated_rect.topleft)

# Generate multiple confetti pieces
confetti_pieces = [ConfettiPiece() for _ in range(150)]  # Increased to 150 for more visual effect

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Subtitle settings
subtitles = [
    "Hi, my name is Dante",
    "Yes I live in Colorado",
    "I don't actually love you",
    "I really hate you"
]
current_subtitle_index = 0
subtitle_timer = 0
SUBTITLE_DURATION = 3000  # Milliseconds per subtitle

# Speech Queue
speech_queue = queue.Queue()

# Function to draw extruded 3D subtitles with dynamic wiggle and rotation effects
def render_3d_subtitle(text, depth, base_color, extrusion_color, rotation_angle, wiggle_offset):
    font_size = 50
    font = pygame.font.SysFont('comicsansms', font_size, bold=True)
    text_surface = font.render(text, True, base_color)
    
    # Create a surface for extrusion
    extruded_surface = pygame.Surface((text_surface.get_width() + depth, text_surface.get_height() + depth), pygame.SRCALPHA)
    
    # Draw extrusion layers
    for i in range(depth):
        offset_x = i * math.cos(math.radians(rotation_angle)) + wiggle_offset
        offset_y = i * math.sin(math.radians(rotation_angle)) + wiggle_offset
        extrusion_layer = font.render(text, True, extrusion_color)
        rotated_extrusion = pygame.transform.rotate(extrusion_layer, rotation_angle)
        extruded_surface.blit(rotated_extrusion, (offset_x, offset_y))
    
    # Draw the top layer of text
    top_layer = font.render(text, True, base_color)
    rotated_top = pygame.transform.rotate(top_layer, rotation_angle)
    extruded_surface.blit(rotated_top, (depth * math.cos(math.radians(rotation_angle)) + wiggle_offset,
                                       depth * math.sin(math.radians(rotation_angle)) + wiggle_offset))
    
    return extruded_surface

# Function to play subtitles using pyttsx3 asynchronously using a speech queue
def speech_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break  # Exit signal
        engine.say(text)
        engine.runAndWait()
        speech_queue.task_done()

# Start the speech worker thread
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

# Initialize subtitle properties
subtitle_rotation = 0
subtitle_wiggle_phase = 0

# Function to update the subtitle
def update_subtitle(index):
    global subtitle_surface
    subtitle_surface = render_3d_subtitle(
        subtitles[index],
        depth=10,
        base_color=(255, 255, 255),
        extrusion_color=(50, 50, 50),  # Darker color for better contrast
        rotation_angle=subtitle_rotation,
        wiggle_offset=math.sin(subtitle_wiggle_phase) * 5  # Wiggle amplitude
    )
    speech_queue.put(subtitles[index])  # Add subtitle to the speech queue

# Initially add the first subtitle to the speech queue
update_subtitle(current_subtitle_index)

# Main loop
running = True

while running:
    dt = clock.tick(60)  # Limit to 60 FPS and get the time since last tick
    screen.fill((30, 30, 30))  # Dark background for better contrast

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw confetti pieces
    for piece in confetti_pieces:
        piece.fall()
        piece.draw(screen)

    # Update subtitle timer
    subtitle_timer += dt
    if subtitle_timer > SUBTITLE_DURATION:
        subtitle_timer = 0
        current_subtitle_index += 1
        if current_subtitle_index < len(subtitles):
            update_subtitle(current_subtitle_index)
        else:
            current_subtitle_index = len(subtitles) - 1  # Stay on the last subtitle

    # Update subtitle animation parameters
    subtitle_rotation = (subtitle_rotation + 1) % 360  # Rotate continuously
    subtitle_wiggle_phase += 0.05  # Increment phase for wiggle

    # Render the current subtitle with updated rotation and wiggle
    subtitle_surface = render_3d_subtitle(
        subtitles[current_subtitle_index],
        depth=10,
        base_color=(255, 255, 255),
        extrusion_color=(50, 50, 50),
        rotation_angle=subtitle_rotation,
        wiggle_offset=math.sin(subtitle_wiggle_phase) * 5
    )

    # Draw the current subtitle with pre-rendered surface
    if subtitle_surface:
        subtitle_rect = subtitle_surface.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(subtitle_surface, subtitle_rect.topleft)

    # Update the display
    pygame.display.flip()

# Signal the speech thread to exit
speech_queue.put(None)
speech_thread.join()

# Quit Pygame
pygame.quit()
