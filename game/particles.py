import pygame
import random

class Particle:
    def __init__(self, x, y, color, size, speed_x, speed_y, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.lifetime = lifetime
        self.age = 0

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.age += 1
        # Fade out particles
        self.color = (self.color[0], self.color[1], self.color[2], max(0, 255 - int(255 * (self.age / self.lifetime))))

    def draw(self, screen):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (self.size, self.size), self.size)
        screen.blit(s, (self.x - self.size, self.y - self.size))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_explosion(self, x, y, base_color, num_particles=10, spread=2, speed_min=1, speed_max=3, size_min=2, size_max=5, lifetime_min=20, lifetime_max=40):
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(speed_min, speed_max)
            speed_x = speed * random.uniform(-spread, spread)
            speed_y = speed * random.uniform(-spread, spread)
            size = random.randint(size_min, size_max)
            lifetime = random.randint(lifetime_min, lifetime_max)
            color = (base_color[0], base_color[1], base_color[2], 255) # Start fully opaque
            self.particles.append(Particle(x, y, color, size, speed_x, speed_y, lifetime))

    def update(self):
        self.particles = [p for p in self.particles if p.age < p.lifetime]
        for p in self.particles:
            p.update()

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
