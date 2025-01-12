import cv2
import mediapipe as mp
import pygame
import random
import threading
import time

# Inisialisasi Pygame
pygame.init()

# Ukuran layar
screen_width, screen_height = 640, 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game with Hand Detection")

# Warna
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Pemain
player_size = 50
player_x = screen_width // 2 - player_size // 2
player_y = screen_height - player_size - 10
player_speed = 5

# Peluru
bullet_width = 5
bullet_height = 10
bullet_speed = 10
bullets = []

# Target
target_size = 40
target_x = random.randint(0, screen_width - target_size)
target_y = random.randint(0, screen_height // 2)

# Skor dan Nyawa
score = 0
lives = 5
font = pygame.font.Font(None, 36)

# Inisialisasi Kamera
cap = cv2.VideoCapture(0)

# Ubah resolusi kamera agar lebih cepat
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Inisialisasi MediaPipe untuk deteksi tangan
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Variabel global untuk posisi tangan
hand_position = None

# Fungsi untuk mendeteksi posisi tangan
def detect_hand_gesture():
    global hand_position
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                x = int(hand_landmarks.landmark[8].x * screen_width)  # Jari telunjuk
                y = int(hand_landmarks.landmark[8].y * screen_height)
                hand_position = (x, y)

# Fungsi untuk menggambar elemen game
def draw_game_elements():
    screen.fill(WHITE)

    # Gambar pemain
    pygame.draw.rect(screen, BLUE, pygame.Rect(player_x, player_y, player_size, player_size))

    # Gambar peluru
    for bullet in bullets:
        pygame.draw.rect(screen, RED, pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height))

    # Gambar target
    pygame.draw.rect(screen, BLACK, pygame.Rect(target_x, target_y, target_size, target_size))

    # Gambar skor dan nyawa
    score_text = font.render(f"Score: {score}", True, BLACK)
    lives_text = font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))

    pygame.display.update()

# Fungsi untuk memperbarui peluru
def update_bullets():
    global target_x, target_y, score, lives
    new_bullets = []
    for bullet in bullets:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            continue
        if (bullet[0] > target_x and bullet[0] < target_x + target_size) and \
           (bullet[1] > target_y and bullet[1] < target_y + target_size):
            score += 10
            target_x = random.randint(0, screen_width - target_size)
            target_y = random.randint(0, screen_height // 2)
        else:
            new_bullets.append(bullet)
    return new_bullets

# Fungsi untuk memperbarui target
def update_target():
    global target_y, lives
    target_y += 2  # Kecepatan target
    if target_y > screen_height:
        target_y = random.randint(0, screen_height // 2)
        target_x = random.randint(0, screen_width - target_size)
        lives -= 1

# Fungsi untuk menembakkan peluru
def shoot_bullet():
    bullets.append([player_x + player_size // 2 - bullet_width // 2, player_y])

# Loop utama game
running = True
clock = pygame.time.Clock()  # Membuat clock untuk mengatur frame rate

# Mulai thread untuk deteksi tangan
hand_thread = threading.Thread(target=detect_hand_gesture, daemon=True)
hand_thread.start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if hand_position:
        x, y = hand_position

        # Membalikkan koordinat X agar sesuai dengan posisi tangan yang sebenarnya
        x = screen_width - x  # Membalikkan posisi horizontal agar karakter mengikuti arah tangan

        # Gerakkan pemain berdasarkan posisi tangan
        player_x = x - player_size // 2  # Agar karakter mengikuti posisi horizontal tangan

        # Pastikan pemain tetap di layar
        player_x = max(0, min(player_x, screen_width - player_size))

        # Gerakan peluru jika tangan di atas (tembakan)
        if y < screen_height // 2 and len(bullets) == 0:
            shoot_bullet()

    # Update peluru
    bullets = update_bullets()
    update_target()

    if lives <= 0:
        print("Game Over!")
        running = False

    draw_game_elements()

    # Batasi frame rate ke 30 fps agar game tidak terlalu lambat
    clock.tick(30)

cap.release()
pygame.quit()
