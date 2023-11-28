# program by: tank king
# demonstration of flame particles

# requires pygame 2.0.0 for pygame.SCALED flag
# to use pygame 1.9.x remove the SCALED flag when initializing the display

import pygame
import sys
import random
import math
from numpy import sin, pi

pygame.init()

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.FULLSCREEN)
pygame.display.set_caption('Flame Sparks Testing')

clock = pygame.time.Clock()
FPS = 60

TARGET_FPS = 60

draw_circle = pygame.draw.circle
new_surface = pygame.Surface
randint = random.randint

color_rgb = [   
            [(20, 20, 20), (200, 200, 200), (255, 255, 255)],
            [(255, 255, 255), (255, 200, 100), (255, 250, 210)],
            [(250, 220, 55), (255, 170, 55), (255, 250, 220)],
            [(140, 170, 225), (100, 160, 250), (240, 240, 250)],
        ]

class Particle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 0.75

    def __init__(self, x=50, y=50, r=5, color=0):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.original_r = r
        self.alpha_layers = Particle.alpha_layer_qty
        self.alpha_glow = Particle.alpha_glow_difference_constant
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        self.burn_rate = 0.05 * randint(1, 8)

    def update(self, dt):
        self.y -= (7 - self.r) * dt / 4
        self.x += randint(-self.r, self.r) * dt * 0.33
        self.original_r -= self.burn_rate * dt
        self.r = int(self.original_r)
        if self.r <= 0:
            self.r = 1

    def draw(self):
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = new_surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - i * (255 // self.alpha_layers - 5)
            if alpha <= 0:
                alpha = 0
            radius = self.r * i * i * self.alpha_glow
            if self.r == 4 or self.r == 3:
                r, g, b = color_rgb[self.color][0]
            elif self.r == 2 or self.r == 1:
                r, g, b = color_rgb[self.color][1]
            else:
                r, g, b = color_rgb[self.color][2]
            color = (r, g, b, alpha)
            draw_circle(self.surf, color, (self.surf.get_width() * 0.5, self.surf.get_height() * 0.5), radius)
        screen.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))

class System:
    def __init__(self, x=50, y=50):
        self.x = x
        self.y = y
        self.flame_intensity = 1
        self.flame_particles = []
        self.generate_particles(0)

    def generate_particles(self, color):
        self.flame_particles.clear()
        for i in range(int(self.flame_intensity) * 1):
            self.flame_particles.append(Particle(self.x + randint(-1, -1), self.y, randint(1, 5), color))

    def draw_particle(self, dt):
        for i in self.flame_particles:
            if i.original_r <= 0:
                color = i.color
                self.flame_particles.remove(i)
                self.flame_particles.append(Particle(self.x + randint(-1, -1), self.y, randint(1, 5), color))
                del i
                continue
            i.update(dt)
            i.draw()

flames = []

color_ranges = {
    'white': '>225,>225>225',
    'red': '>100,<50,<50',
    'yellow': '>200,>200,<50',
    'black': '<20,<20,<20'
}

def check_color(color, condition: str):
    r, g, b = condition.split(',')
    r1, g1, b1 = color

    def compare(x, y, compare_type):
        x, y = int(x), int(y)
        if compare_type == '>':
            return x > y
        elif compare_type == '<':
            return x < y
        elif compare_type == '==':
            return x == y

    red_compare_results = compare(r1, r[1:], r[0])
    green_compare_results = compare(g1, g[1:], g[0])
    blue_compare_results = compare(b1, b[1:], b[0])

    if red_compare_results and green_compare_results and blue_compare_results:
        return True
    else:
        return False

def extract_points_from_img(image: pygame.Surface, image_color_range: dict, allowed_colors=('black')):
    extracted_points = []
    image.lock()
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            pixel_color = image.get_at([x, y])
            r, g, b, alpha = pixel_color
            if alpha > 127:
                for color in list(image_color_range.keys()):
                    if color in allowed_colors:
                        if check_color((r, g, b), image_color_range[color]):
                            extracted_points.append([x, y])
    image.unlock()
    return extracted_points

img = pygame.image.load('images/starry_night.jpg').convert()
show_img = pygame.image.load('images/starry_night_rendered.jpg').convert()
img = pygame.transform.scale(img, (1280, 720))
show_img = pygame.transform.scale(show_img, (1280, 720))
print('Loading Points...')
points = extract_points_from_img(img, color_ranges)
print('Points Loaded')
print(len(points))

def remove_point_cluttering(point_list):
    point_list.sort(key=lambda a: a[1])
    point_list = [i for i in point_list if point_list.index(i) % 10 == 0]
    return point_list


print('Removing Point Cluttering')
points = remove_point_cluttering(point_list=points)
print('Point Cluttering Reduced')

print('Shifting all points to center')
for p in points:
    p[0] += screen_width // 2 - img.get_width() // 2
print('All points shifted to center')

points1 = [[430 + 70 * math.cos(math.radians(i)), 400 + 70 * math.sin(math.radians(i))] for i in range(360)]
points1 += [[430 + 50 * math.cos(math.radians(i)), 400 + 50 * math.sin(math.radians(i))] for i in range(0, 360, 2)]
points1 += [[430 + 30 * math.cos(math.radians(i)), 400 + 30 * math.sin(math.radians(i))] for i in range(0, 360, 5)]
points1 += [[430 + 10 * math.cos(math.radians(i)), 400 + 10 * math.sin(math.radians(i))] for i in range(0, 360, 10)]

points2 = [[1150 + 45 * math.cos(math.radians(i)), 120 + 45 * math.sin(math.radians(i))] for i in range(360)]
points2 += [[1150 + 25 * math.cos(math.radians(i)), 120 + 25 * math.sin(math.radians(i))] for i in range(0, 360, 5)]
points2 += [[1150 + 5 * math.cos(math.radians(i)), 120 + 5 * math.sin(math.radians(i))] for i in range(0, 360, 10)]
points2 += [[290 + 30 * math.cos(math.radians(i)), 120 + 30 * math.sin(math.radians(i))] for i in range(0, 360, 5)]
points2 += [[290 + 10 * math.cos(math.radians(i)), 120 + 10 * math.sin(math.radians(i))] for i in range(0, 360, 10)]

points3 = []
for k in range(0, 100, 20):
    x = [0, 100, 500]
    y = [100, 300, 100]
    for i in range(50):
        t = i * 1. / 50.
        a = (int)((1-t) * (1-t) * x[0] + 2 * t * (1-t) * x[1] + t * t * x[2])
        b = (int)((1-t) * (1-t) * y[0] + 2 * t * (1-t) * y[1] + t * t * y[2]) + k
        points3 += [[a, b]]
    x = [500, 700, 800]
    y = [100, 80, 250]
    for i in range(50):
        t = i * 1. / 50.
        a = (int)((1-t) * (1-t) * x[0] + 2 * t * (1-t) * x[1] + t * t * x[2])
        b = (int)((1-t) * (1-t) * y[0] + 2 * t * (1-t) * y[1] + t * t * y[2]) + k
        points3 += [[a, b]]

for k in range(0, 100, 20):
    x = [0, 100, 250]
    y = [450, 380, 500]
    for i in range(30):
        t = i * 1. / 30.
        a = (int)((1-t) * (1-t) * x[0] + 2 * t * (1-t) * x[1] + t * t * x[2])
        b = (int)((1-t) * (1-t) * y[0] + 2 * t * (1-t) * y[1] + t * t * y[2]) + k
        points3 += [[a, b]]
    x = [250, 600, 700]
    y = [500, 400, 420]
    for i in range(30):
        t = i * 1. / 30.
        a = (int)((1-t) * (1-t) * x[0] + 2 * t * (1-t) * x[1] + t * t * x[2])
        b = (int)((1-t) * (1-t) * y[0] + 2 * t * (1-t) * y[1] + t * t * y[2]) + k
        points3 += [[a, b]]
    x = [700, 800, 950]
    y = [420, 380, 420]
    for i in range(30):
        t = i * 1. / 30.
        a = (int)((1-t) * (1-t) * x[0] + 2 * t * (1-t) * x[1] + t * t * x[2])
        b = (int)((1-t) * (1-t) * y[0] + 2 * t * (1-t) * y[1] + t * t * y[2]) + k
        points3 += [[a, b]]
    x = [950, 1050, 1280]
    y = [420, 300, 250]
    for i in range(30):
        t = i * 1. / 30.
        a = (int)((1-t) * (1-t) * x[0] + 2 * t * (1-t) * x[1] + t * t * x[2])
        b = (int)((1-t) * (1-t) * y[0] + 2 * t * (1-t) * y[1] + t * t * y[2]) + k
        points3 += [[a, b]]
        
if __name__ == "__main__":
    dt = 1
    surf = pygame.Surface(screen.get_size())
    surf.set_alpha(0)
    alpha = 0
    start = True
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                start = True
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
        screen.fill((0, 0, 0))
        # surf.set_alpha(170)
        screen.blit(show_img, (screen_width // 2 - img.get_width() // 2, 0))
        screen.blit(surf, (0, 0)) 
        if start:
            if len(flames) < len(points):
                qty = 5 if len(points) - len(flames) > 5 else len(points) - len(flames)
                for _ in range(qty):
                    flames.append(System(*points[len(flames)]))
            else:
                alpha += 1
        if alpha >= 1:
            if len(flames) < len(points) + len(points1):
                temp = System(*points1[len(flames) - len(points)])
                temp.flame_intensity = 10
                temp.generate_particles(1)
                flames.append(temp)
            elif len(flames) < len(points) + len(points1) + len(points2):
                temp = System(*points2[len(flames) - len(points) - len(points1)])
                temp.flame_intensity = 10
                temp.generate_particles(2)
                flames.append(temp)
            elif len(flames) < len(points) + len(points1) + len(points2) + len(points3):
                temp = System(*points3[len(flames) - len(points) - len(points1) - len(points2)])
                temp.flame_intensity = 10
                temp.generate_particles(3)
                flames.append(temp)

        for i in flames:
            i.draw_particle(dt)
        pygame.display.update()
        pygame.display.set_caption('Flame Particles Testing FPS = ' + str(int(clock.get_fps())))
        dt = TARGET_FPS * clock.tick(FPS) * 0.001