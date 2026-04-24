import pygame
import random
import sys
import cv2
import numpy as np
import hand_tracking

WIDTH = 400
HEIGHT = 600

BIRD_SIZE = 40
GRAVITY = 0.25
JUMP_VELOCITY = -6
MAX_FALL_SPEED = 6

PIPE_WIDTH = 70
PIPE_GAP = 180
PIPE_DISTANCE = 220

FONT_SIZE = 32
CAM_WIDTH = 150
CAM_HEIGHT = 200

VIDEO_PATH = "7730220595419.mp4"
# ===== VIDEO CAMPAIGN INTRO =====

# ===== HIGH SCORE =====
def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# ===== PIPE =====
def create_pipe(x):
    return {
        "x": x,
        "gap_center": random.randint(150, HEIGHT - 150),
        "scored": False
    }

def move_pipes(pipes, speed):
    for pipe in pipes:
        pipe["x"] -= speed

    if pipes and pipes[0]["x"] < -PIPE_WIDTH:
        pipes.pop(0)

    return pipes

def draw_pipes(screen, pipes, pipe_head, pipe_body):
    HEAD_H = pipe_head.get_height()

    for pipe in pipes:
        x = pipe["x"]
        gap_center = pipe["gap_center"]

        # TOP
        top_height = gap_center - PIPE_GAP // 2
        body_height = max(0, top_height - HEAD_H)

        if body_height > 0:
            body = pygame.transform.scale(pipe_body, (PIPE_WIDTH, body_height))
            body = pygame.transform.flip(body, False, True)
            screen.blit(body, (x, 0))

        head = pygame.transform.flip(pipe_head, False, True)
        screen.blit(head, (x, body_height))

        # BOTTOM
        bottom_y = gap_center + PIPE_GAP // 2
        bottom_height = HEIGHT - bottom_y

        if bottom_height > HEAD_H:
            body = pygame.transform.scale(pipe_body, (PIPE_WIDTH, bottom_height - HEAD_H))
            screen.blit(body, (x, bottom_y + HEAD_H))

        screen.blit(pipe_head, (x, bottom_y))

# ===== COLLISION =====
def check_collision(bird_rect, pipes):
    if bird_rect.top < 0 or bird_rect.bottom > HEIGHT:
        return True

    margin = 8

    for pipe in pipes:
        x = pipe["x"]
        gap = pipe["gap_center"]

        top_rect = pygame.Rect(x + margin, 0, PIPE_WIDTH - margin * 2, gap - PIPE_GAP // 2)
        bottom_rect = pygame.Rect(x + margin, gap + PIPE_GAP // 2, PIPE_WIDTH - margin * 2, HEIGHT)

        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True

    return False

# ===== TEXT =====
def draw_text_center(screen, text, y, size=FONT_SIZE, color=(255,255,255)):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    x = WIDTH//2 - surf.get_width()//2
    screen.blit(surf, (x, y))

# cv2 to pygame surface
def cv2_to_pygame(cv_img):
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    cv_img_rgb = np.ascontiguousarray(cv_img_rgb)
    pygame_surf = pygame.surfarray.make_surface(cv_img_rgb.swapaxes(0,1))
    return pygame.transform.flip(pygame_surf, True, False)

# ===== SCREENS =====
def show_menu(screen, bg):
    while True:
        screen.blit(bg, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(80)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_text_center(screen, "FLAP OR DIE", 150, 60)
        draw_text_center(screen, "1 - Campaign", 280)
        draw_text_center(screen, "2 - Endless", 330)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return "campaign"
                if e.key == pygame.K_2:
                    return "endless"

def show_game_over(screen, score, high_score, bg):
    while True:
        screen.blit(bg, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_text_center(screen, "GAME OVER", 200, 60, (255,50,50))
        draw_text_center(screen, f"Score: {score}", 280, 36)
        draw_text_center(screen, f"High: {high_score}", 320, 30)
        draw_text_center(screen, "SPACE: Retry", 380, 28)
        draw_text_center(screen, "ESC: Menu", 420, 28)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    return "retry"
                if e.key == pygame.K_ESCAPE:
                    return "menu"

def show_level_complete(screen, level, bg):
    while True:
        screen.blit(bg, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_text_center(screen, f"LEVEL {level} COMPLETE!", 250, 50, (50,255,100))
        draw_text_center(screen, "SPACE: Next", 320)
        draw_text_center(screen, "ESC: Menu", 360)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    return "next"
                if e.key == pygame.K_ESCAPE:
                    return "menu"

def play_campaign_intro(screen):
    """
    PHÁT VIDEO GIỚI THIỆU CAMPAIGN MODE SAU KHI NHẤN PHÍM 1.
    - Video: assets/videos/intro_campaign.mp4 (MP4)
    - ESC/Enter: Skip sớm
    - Không có file: Skip tự động
    """
    import os
    if not os.path.exists(VIDEO_PATH):
        print(f"CẢNH BÁO: Không tìm video '{VIDEO_PATH}'. Skip intro.")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"LỖI: Không mở được video '{VIDEO_PATH}'.")
        return

    clock = pygame.time.Clock()
    playing = True

    while playing:
        ret, frame = cap.read()
        if not ret:
            break  # Video kết thúc

        # Resize frame to screen
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        # Convert to pygame surface
        video_surf = cv2_to_pygame(frame)
        video_surf = pygame.transform.flip(video_surf, True, False)  # Fix upside down cho video

        # Dark overlay cho cinematic (nhẹ hơn)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(20)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(video_surf, (0, 0))

        # Hiển thị hướng dẫn skip (trắng, to)
        draw_text_center(screen, "NHẤN ESC ĐỂ SKIP VIDEO", HEIGHT - 80, 36, (255, 255, 255))
        draw_text_center(screen, "Campaign Mode sắp bắt đầu!", HEIGHT - 40, 28, (200, 255, 200))

        pygame.display.flip()
        clock.tick(60)  # Match game FPS

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    playing = False
                    break

    cap.release()
    print("Video intro kết thúc. Bắt đầu Campaign!")


# ===== MAIN =====
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flap or Die")
    clock = pygame.time.Clock()

    # Init camera hand tracking
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    if not cap.isOpened():
        print("Không thể mở camera.")
        pygame.quit()
        return

    tracker = hand_tracking.HandTracker(show_camera=False)
    tracker.prev_gesture = "OPEN"

    # LOAD assets
    menu_bg = pygame.transform.scale(pygame.image.load("assets/menu.png"), (WIDTH, HEIGHT))
    game_bg = pygame.transform.scale(pygame.image.load("assets/game.png"), (WIDTH, HEIGHT))
    gameover_bg = pygame.transform.scale(pygame.image.load("assets/gameover.png"), (WIDTH, HEIGHT))

    pipe_head = pygame.transform.scale(pygame.image.load("assets/pipe/pipe_head.png"), (PIPE_WIDTH, 70))
    pipe_body = pygame.transform.scale(pygame.image.load("assets/pipe/pipe_body.png"), (PIPE_WIDTH, 200))

    bird_frames = []
    for i in range(1, 9):
        img = pygame.image.load(f"assets/bird/bird{i}.png").convert_alpha()
        bird_frames.append(pygame.transform.scale(img, (40, 40)))

    frame_index = 0
    frame_speed = 0.2

# ============== ÂM THANH (tiếng Việt hướng dẫn) ==============
# NHẠC NỀN: Đặt file nhạc của bạn tại assets/sounds/bg_music.mp3 (MP3/WAV/OGG)
# ÂM THANH QUA ỐNG (pass obstacle): Đặt tại assets/sounds/point.wav (WAV/MP3, phát khi score +1)
# Thay tên file dưới đây nếu dùng tên khác. Nếu thiếu file, game chạy im lặng.
    pygame.mixer.music.load("Theme For FlappyBird - Original Track (mp3cut.net).mp3")
    point_sound = pygame.mixer.Sound("Flappy Bird - Sound Effect [HD] (mp3cut.net).mp3")
# ====================================================================

    high_score = load_high_score()

    while True:
        mode = show_menu(screen, menu_bg)
        
        # PHÁT VIDEO INTRO NẾU CHỌN CAMPAIGN (SAU PHÍM 1)
        if mode == "campaign":
            play_campaign_intro(screen)


        level = 1
        target = 5

        while True:
            bird = pygame.Rect(100, HEIGHT//2, BIRD_SIZE, BIRD_SIZE)
            vel = 0
            pipes = [create_pipe(WIDTH + i*PIPE_DISTANCE) for i in range(3)]
            score = 0
            try:
                pygame.mixer.music.play(-1)
            except:
                pass

            speed = 3 + (level-1)

            running = True
            action = None

            while running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        cap.release()
                        cv2.destroyAllWindows()
                        pygame.quit()
                        sys.exit()

                cam_surf = None

                # Nhảy khi cử chỉ chuyển từ OPEN sang FIST
                ret, frame = cap.read()
                if ret:
                    frame_vis = tracker.process(frame)

                    if frame_vis is not None:
                        small_vis = cv2.resize(frame_vis, (CAM_WIDTH, CAM_HEIGHT))
                        cam_surf = cv2_to_pygame(small_vis)

                    current_gesture = tracker.get_gesture()
                    if tracker.prev_gesture == "OPEN" and current_gesture == "FIST":
                        vel = JUMP_VELOCITY
                    tracker.prev_gesture = current_gesture
                else:
                    tracker.prev_gesture = "OPEN"

                vel += GRAVITY
                vel = min(vel, MAX_FALL_SPEED)
                bird.y += int(vel)

                pipes = move_pipes(pipes, speed)
                if len(pipes) < 3:
                    pipes.append(create_pipe(WIDTH + PIPE_DISTANCE))

                if check_collision(bird, pipes):
                    action = show_game_over(screen, score, high_score, gameover_bg)
                    if action == "menu":
                        break
                    else:
                        running = False

                for p in pipes:
                    if not p["scored"] and p["x"] + PIPE_WIDTH < bird.x:
                        score += 1
                        p["scored"] = True
                        if point_sound is not None:
                            point_sound.play()

                if mode == "endless" and score > high_score:
                    high_score = score
                    save_high_score(high_score)

                # animation
                frame_index += frame_speed
                if frame_index >= len(bird_frames):
                    frame_index = 0

                bird_img = bird_frames[int(frame_index)]
                bird_rot = pygame.transform.rotate(bird_img, -vel*4)

                # draw game
                screen.blit(game_bg, (0, 0))
                draw_pipes(screen, pipes, pipe_head, pipe_body)
                screen.blit(bird_rot, (bird.x, bird.y))

                if cam_surf is not None:
                    screen.blit(cam_surf, (WIDTH - CAM_WIDTH - 10, 10))

                draw_text_center(screen, f"Score: {score}", 20)
                if mode == "campaign":
                    draw_text_center(screen, f"Level: {level}", 50)

                gesture_text = tracker.get_gesture() if ret else "NO CAMERA"
                draw_text_center(screen, f"Gesture: {gesture_text}", HEIGHT - 40, 24)

                pygame.display.flip()
                clock.tick(60)

                # campaign win
                if mode == "campaign" and score >= target:
                    action = show_level_complete(screen, level, game_bg)

                    if action == "menu":
                        break

                    level += 1
                    target += 5
                    running = False

            if mode == "campaign" and level > 3:
                show_game_over(screen, score, high_score, gameover_bg)
                break

            if action == "menu":
                break

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


if __name__ == "__main__":
    main()
