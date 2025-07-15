import pygame


class InputBox:
    def __init__(self, x, y, width, height, font, placeholder):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode

    def draw(self, surface):
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        bg = (255, 255, 255) if self.active else (248, 249, 250)
        border = (52, 152, 219) if self.active else (189, 195, 199)

        pygame.draw.rect(surface, (0, 0, 0, 30), self.rect.move(2, 2), border_radius=8)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)

        txt_color = (60, 70, 90)
        if self.text:
            text_surface = self.font.render(self.text, True, txt_color)
        else:
            text_surface = self.font.render(self.placeholder, True, (149, 165, 166))

        text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        surface.blit(text_surface, text_rect)

        if self.active and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            pygame.draw.line(surface, txt_color,
                             (cursor_x, self.rect.y + 8),
                             (cursor_x, self.rect.y + self.rect.height - 8), 2)

    def get_text(self):
        return self.text