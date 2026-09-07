import pygame

import settings


MENU_OPTIONS = ["PLAY", "HOW TO PLAY", "QUIT"]


def draw_main_menu(surface, fonts, selected_index):
    surface.fill((30, 26, 40))

    for i in range(6):
        x = 120 + i * 190
        y = 90 + (i % 2) * 40
        pygame.draw.ellipse(surface, (255, 255, 255, 30), (x, y, 26, 32), width=2)

    title = fonts["title"].render(settings.GAME_TITLE, True, settings.CREAM)
    subtitle = fonts["small"].render("Operation Egg Delivery", True, settings.LIGHT_GRAY)

    surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 220)))
    surface.blit(subtitle, subtitle.get_rect(center=(settings.SCREEN_WIDTH // 2, 270)))

    start_y = 380
    for i, option in enumerate(MENU_OPTIONS):
        color = settings.YELLOW if i == selected_index else settings.WHITE
        label = fonts["medium"].render(option, True, color)
        rect = label.get_rect(center=(settings.SCREEN_WIDTH // 2, start_y + i * 60))
        if i == selected_index:
            marker = fonts["medium"].render(">", True, settings.YELLOW)
            surface.blit(marker, (rect.left - 40, rect.top))
        surface.blit(label, rect)

    hint = fonts["tiny"].render("Use UP/DOWN and ENTER, or click a menu item", True, settings.GRAY)
    surface.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, 620)))

    return [
        fonts["medium"].render(option, True, settings.WHITE).get_rect(
            center=(settings.SCREEN_WIDTH // 2, start_y + i * 60))
        for i, option in enumerate(MENU_OPTIONS)
    ]


def draw_how_to_play(surface, fonts):
    surface.fill((26, 30, 40))

    title = fonts["large"].render("HOW TO PLAY", True, settings.CREAM)
    surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 100)))

    lines = [
        "Your mission: carry one (1) egg across town without breaking it.",
        "",
        "WASD / Arrow Keys  -  Move",
        "E                  -  Pick up the egg",
        "SPACE              -  Drop the egg (causes damage)",
        "ESC                -  Pause",
        "R                  -  Restart after breaking the egg",
        "",
        "The egg cracks more as it takes damage - watch the condition bar.",
        "Hard bumps, hazards, and rough impacts all cost condition.",
        "If it hits 0%... the egg has left this world.",
        "",
        "Press ENTER or ESC to return to the menu.",
    ]

    y = 190
    for line in lines:
        label = fonts["small"].render(line, True, settings.WHITE)
        surface.blit(label, label.get_rect(center=(settings.SCREEN_WIDTH // 2, y)))
        y += 34


def _condition_color(condition):
    if condition > 75:
        return settings.CONDITION_GOOD_COLOR
    if condition > 50:
        return settings.CONDITION_OK_COLOR
    if condition > 25:
        return settings.CONDITION_BAD_COLOR
    return settings.CONDITION_CRITICAL_COLOR


def draw_hud(surface, fonts, level_num, level_name, objective, condition):
    backing = pygame.Surface((settings.SCREEN_WIDTH, 96), pygame.SRCALPHA)
    backing.fill((15, 15, 20, 150))
    surface.blit(backing, (0, 0))

    level_label = fonts["medium"].render(f"LEVEL {level_num} - {level_name}", True, settings.WHITE)
    surface.blit(level_label, (24, 10))

    objective_text = objective if len(objective) <= 60 else objective[:57] + "..."
    objective_label = fonts["small"].render(f"OBJECTIVE: {objective_text}", True, settings.LIGHT_GRAY)
    surface.blit(objective_label, (24, 62))

    bar_w, bar_h = 220, 22
    bar_x = settings.SCREEN_WIDTH - bar_w - 24
    bar_y = 40

    cond_label = fonts["small"].render("EGG CONDITION", True, settings.WHITE)
    surface.blit(cond_label, (bar_x, bar_y - 24))

    pygame.draw.rect(surface, settings.DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    fill_w = int(bar_w * max(0, condition) / 100)
    if fill_w > 0:
        pygame.draw.rect(surface, _condition_color(condition),
                         (bar_x, bar_y, fill_w, bar_h), border_radius=6)
    pygame.draw.rect(surface, settings.WHITE, (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=6)

    pct_label = fonts["small"].render(f"{int(condition)}%", True, settings.WHITE)
    pct_rect = pct_label.get_rect(midleft=(bar_x + bar_w + 10, bar_y + bar_h // 2))
    surface.blit(pct_label, pct_rect)

    controls_label = fonts["tiny"].render(settings.CONTROLS_TEXT, True, settings.GRAY)
    surface.blit(controls_label, (settings.SCREEN_WIDTH - controls_label.get_width() - 24, bar_y + bar_h + 6))