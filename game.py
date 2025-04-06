import sys
import time
import pygame
import logging

# Константы
WIDTH, HEIGHT = 1440, 1024
LEFT_PANEL_WIDTH = 416
GAME_AREA_WIDTH = 1024
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
FONT_COLOR = (50, 50, 200)
LEADERBOARD_FILE = "leaderboard.txt"
CHECKMARK_Y_OFFSET = 120
PANEL_TOP_OFFSET = 120
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
INPUT_BOX_WIDTH = 400
INPUT_BOX_HEIGHT = 50
CURSOR_BLINK_SPEED = 500

# Инициализация PyGame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Аптечный квест")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


def load_image(path, size=None):
    """Загружает и масштабирует изображение.

    Args:
        path (str): Путь к файлу изображения
        size (tuple, optional): Кортеж (ширина, высота) для масштабирования

    Returns:
        pygame.Surface: Загруженное изображение
    """
    image = pygame.image.load(path)
    return pygame.transform.scale(image, size) if size else image


# Загрузка изображений
background = load_image("images/scene.png", (GAME_AREA_WIDTH, HEIGHT))
checkmark_img = load_image("images/checkmark.png", (32, 32))
menu_background = load_image("images/start.png", (WIDTH, HEIGHT))
end_background = load_image("images/end.png", (WIDTH, HEIGHT))

request_images = {
    f"lvl-{i}": load_image(f"images/lvl-{i}.png", (LEFT_PANEL_WIDTH, 904))
    for i in range(1, 4)
}

# Конфигурация уровней
LEVELS = {
    1: {
        "items": ["aspirin", "thermometer", "bandage", "iodine", "antibiotic"],
        "positions": {
            "aspirin": (120, 140),
            "thermometer": (130, 640),
            "bandage": (50, 950),
            "iodine": (980, 300),
            "antibiotic": (375, 815),
        }
    },
    2: {
        "items": [
            "aspirin", "thermometer", "bandage", "iodine", "antibiotic",
            "syringe", "mask", "pills", "vitamins", "ointment"
        ],
        "positions": {
            "aspirin": (120, 140),
            "thermometer": (130, 640),
            "bandage": (50, 950),
            "iodine": (980, 300),
            "antibiotic": (375, 815),
            "syringe": (520, 480),
            "mask": (800, 650),
            "pills": (415, 300),
            "vitamins": (700, 640),
            "ointment": (410, 470),
        }
    },
    3: {
        "items": [
            "aspirin", "thermometer", "bandage", "iodine", "antibiotic",
            "syringe", "mask", "pills", "vitamins", "ointment",
            "scissors", "alcohol", "cough_syrup", "eye_drops", "first_aid_kit"
        ],
        "positions": {
            "aspirin": (120, 140),
            "thermometer": (130, 640),
            "bandage": (50, 950),
            "iodine": (980, 300),
            "antibiotic": (375, 815),
            "syringe": (520, 480),
            "mask": (800, 650),
            "pills": (415, 300),
            "vitamins": (700, 640),
            "ointment": (410, 470),
            "scissors": (650, 640),
            "alcohol": (880, 950),
            "cough_syrup": (245, 950),
            "eye_drops": (990, 120),
            "first_aid_kit": (750, 140),
        }
    }
}

checkmark_positions = {
    "lvl-1": {
        "aspirin": (80, 600),
        "thermometer": (150, 600),
        "bandage": (210, 600),
        "iodine": (270, 600),
        "antibiotic": (350, 600),
    },
    "lvl-2": {
        "aspirin": (40, 600),
        "thermometer": (80, 600),
        "bandage": (120, 600),
        "iodine": (155, 600),
        "antibiotic": (195, 600),
        "syringe": (230, 600),
        "mask": (265, 600),
        "pills": (300, 600),
        "vitamins": (335, 600),
        "ointment": (370, 600),
    },
    "lvl-3": {
        "aspirin": (25, 600),
        "thermometer": (60, 600),
        "bandage": (100, 600),
        "iodine": (130, 600),
        "antibiotic": (165, 600),
        "syringe": (200, 600),
        "mask": (230, 600),
        "pills": (260, 600),
        "vitamins": (295, 600),
        "ointment": (325, 600),
        "scissors": (365, 600),
        "alcohol": (125, 730),
        "cough_syrup": (200, 730),
        "eye_drops": (240, 730),
        "first_aid_kit": (300, 730),
    }
}


def draw_timer_and_score(start_time, score):
    """Отрисовывает таймер и счет в верхней части экрана.

    Args:
        start_time (float): Время начала игры от time.time()
        score (int): Текущее количество очков
    """
    elapsed = int(time.time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_text = font.render(f"Время: {minutes:02}:{seconds:02}", True, BLACK)
    score_text = font.render(f"Очки: {score}", True, BLACK)
    screen.blit(timer_text, (20, 20))
    screen.blit(score_text, (20, 60))


def draw_checkmarks(level_key, found_items):
    """Отрисовывает галочки на найденных предметах в интерфейсе.

    Args:
        level_key (str): Идентификатор уровня (например, 'lvl-1')
        found_items (list): Список найденных предметов
    """
    if level_key not in checkmark_positions:
        return

    for item in found_items:
        pos = checkmark_positions[level_key].get(item)
        if pos:
            x, y = pos
            screen.blit(checkmark_img, (x, y + CHECKMARK_Y_OFFSET))


def game_scene(level, score, start_time):
    """Управляет основным игровым процессом для конкретного уровня.

    Args:
        level (int): Номер уровня (1-3)
        score (int): Текущее количество очков
        start_time (float): Время начала игры от time.time()

    Returns:
        int: Новое значение очков после завершения уровня
    """
    found_items = []
    level_data = LEVELS[level]
    level_key = f"lvl-{level}"

    running = True
    while running:
        screen.fill(WHITE)

        # Левая панель с заданием
        if level_key in request_images:
            screen.blit(request_images[level_key], (0, PANEL_TOP_OFFSET))

        draw_timer_and_score(start_time, score)
        draw_checkmarks(level_key, found_items)

        # Игровое поле
        screen.blit(background, (LEFT_PANEL_WIDTH, 0))
        pygame.display.flip()
        clock.tick(FPS)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos, level_data["positions"], found_items)

        # Проверка завершения уровня
        if len(found_items) == len(level_data["items"]):
            pygame.time.delay(500)
            return score + len(found_items) * 100

    return score


def handle_click(mouse_pos, item_positions, found_items):
    """Обрабатывает клики по предметам на игровом поле.

    Args:
        mouse_pos (tuple): Координаты (x, y) клика
        item_positions (dict): Позиции предметов уровня
        found_items (list): Список для добавления найденных предметов
    """
    mouse_x, mouse_y = mouse_pos
    for item, (x, y) in item_positions.items():
        if item in found_items:
            continue

        item_rect = pygame.Rect(
            x + LEFT_PANEL_WIDTH - 25,
            y - 25,
            50,
            50
        )
        if item_rect.collidepoint(mouse_x, mouse_y):
            found_items.append(item)


def show_leaderboard():
    """Отображает экран таблицы лидеров с лучшими результатами."""
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-10:]
    except FileNotFoundError:
        lines = []

    back_button = pygame.Rect((WIDTH - 200) // 2, HEIGHT - 100, 200, 50)

    while True:
        screen.fill(WHITE)
        title = font.render("Таблица лидеров", True, BLACK)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 100))

        # Отображение записей
        for i, line in enumerate(lines):
            entry = font.render(line.strip(), True, BLACK)
            screen.blit(entry, (WIDTH // 2 - 200, 180 + i * 40))

        # Кнопка назад
        pygame.draw.rect(screen, BLUE, back_button)
        back_text = font.render("Назад", True, WHITE)
        text_x = back_button.x + (back_button.width - back_text.get_width()) // 2
        screen.blit(back_text, (text_x, back_button.y + 10))

        pygame.display.flip()

        # Обработка ввода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def leaderboard_screen(score, start_time):
    """Управляет экраном сохранения результата после завершения игры."""
    name = ""
    input_active = True
    elapsed = int(time.time() - start_time)
    minutes, seconds = elapsed // 60, elapsed % 60

    input_box = pygame.Rect((WIDTH - INPUT_BOX_WIDTH) // 2, 470, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
    save_button = pygame.Rect((WIDTH - 200) // 2, 550, 200, 50)

    cursor_visible = True
    cursor_timer = 0

    while input_active:
        current_time = pygame.time.get_ticks()
        if current_time - cursor_timer > CURSOR_BLINK_SPEED:
            cursor_visible = not cursor_visible
            cursor_timer = current_time

        screen.blit(end_background, (0, 0))

        # Отображение элементов интерфейса
        render_text("Игра завершена!", 300)
        render_text(f"Очки: {score} | Время: {minutes:02}:{seconds:02}", 360)
        render_text("Введите имя:", 420)

        # Поле ввода
        draw_input_box(input_box, name, cursor_visible, cursor_timer, CURSOR_BLINK_SPEED)

        # Кнопка сохранения
        pygame.draw.rect(screen, BLUE, save_button, border_radius=5)
        render_button_text("Сохранить", save_button)

        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    save_result(name, score, minutes, seconds)
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 20 and event.unicode.isprintable():
                        name += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_button.collidepoint(event.pos) and name:
                    save_result(name, score, minutes, seconds)
                    input_active = False


def render_text(text, y_pos, color=WHITE):
    """Рендерит текст по центру экрана на заданной вертикальной позиции.

    Args:
        text (str): Текст для отображения
        y_pos (int): Вертикальная позиция (Y-координата)
        color (tuple, optional): Цвет текста в формате RGB
    """
    surface = font.render(text, True, color)
    screen.blit(surface, ((WIDTH - surface.get_width()) // 2, y_pos))


def draw_input_box(box, text, cursor_visible, cursor_timer, blink_speed):
    """Отрисовывает поле ввода с текстом и мигающим курсором.

    Args:
        box (pygame.Rect): Область для отрисовки поля ввода
        text (str): Текущий текст в поле
        cursor_visible (bool): Флаг видимости курсора
        cursor_timer (int): Время последнего изменения состояния курсора
        blink_speed (int): Частота мигания курсора в миллисекундах
    """
    pygame.draw.rect(screen, WHITE, box, border_radius=5)
    pygame.draw.rect(screen, BLUE, box, 2, border_radius=5)

    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (box.x + 10, box.y + 10))

    # Мигающий курсор
    current_time = pygame.time.get_ticks()
    if current_time - cursor_timer > blink_speed:
        cursor_visible = not cursor_visible
        cursor_timer = current_time

    if cursor_visible:
        cursor_x = box.x + 10 + text_surface.get_width() + 2
        pygame.draw.line(
            screen, BLACK,
            (cursor_x, box.y + 10),
            (cursor_x, box.y + box.height - 10),
            2
        )


def render_button_text(text, button):
    """Рендерит текст по центру кнопки.

    Args:
        text (str): Текст для отображения
        button (pygame.Rect): Область кнопки
    """
    surface = font.render(text, True, WHITE)
    x_pos = button.x + (button.width - surface.get_width()) // 2
    screen.blit(surface, (x_pos, button.y + 10))


def save_result(name, score, minutes, seconds):
    """Сохраняет результат игрока в файл лидерборда."""
    # Проверяем, что name является строкой и не состоит только из пробелов
    if not isinstance(name, str) or not name.strip():
        return

    try:
        cleaned_name = name.strip()
        entry = f"{cleaned_name}: {score} очков, {minutes:02}:{seconds:02}\n"
        with open("leaderboard.txt", "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logging.error(f"Ошибка сохранения: {str(e)}")

def main_menu():
    """Управляет главным меню игры и обработкой навигации."""
    buttons = [
        pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        for y in [300, 400, 500]
    ]
    labels = ["Новая игра", "Таблица лидеров", "Выход"]

    while True:
        screen.blit(menu_background, (0, 0))
        render_text("Аптечный Квест", 150, BLACK)

        # Отрисовка кнопок
        for btn, label in zip(buttons, labels):
            pygame.draw.rect(screen, BLUE, btn)
            render_button_text(label, btn)

        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_menu_click(event.pos, buttons)


def handle_menu_click(pos, buttons):
    """Обрабатывает клики по кнопкам в главном меню.

    Args:
        pos (tuple): Координаты клика (x, y)
        buttons (list): Список кнопок меню
    """
    if buttons[0].collidepoint(pos):
        start_game()
    elif buttons[1].collidepoint(pos):
        show_leaderboard()
    elif buttons[2].collidepoint(pos):
        pygame.quit()
        sys.exit()


def start_game():
    """Запускает новую игровую сессию с последовательным прохождением уровней."""
    score = 0
    start_time = time.time()
    for level in range(1, 4):
        score = game_scene(level, score, start_time)
    leaderboard_screen(score, start_time)


def main():
    """Главная функция приложения, запускающая основной цикл программы."""
    while True:
        main_menu()


if __name__ == "__main__":
    main()
    pygame.quit()