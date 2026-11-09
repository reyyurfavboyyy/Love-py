# -*- coding: utf-8 -*-
"""Heart Game - Animasi Partikel Teks Hati (Heart) Persis Seperti Video TikTok.

Fitur & Karakteristik:
1. Config dataclass dengan parameter persis:
   - Resolusi: 1000x1000, 120 FPS
   - Partikel: 160 outline (gap 22), 130 fill (gap 30), 1000 floating
   - Skala 20, y_offset -45
   - Gradasi 5 warna merah & crimson
   - Kata-kata hati: "i love you", "I LOVE YOU", "love you"
   - Kata-kata melayang: "love", "♥", "love you", "❤"
2. Animasi kemunculan:
   - Outline melingkari hati secara searah jarum jam (clockwise) dari lekukan atas.
   - Fill mengisi bagian dalam hati dari ujung bawah ke atas (bottom-up).
   - Floating melayang pelan ke atas di latar belakang dengan kedipan lembut.
   - Teks tengah " I Love you" berukuran 54 fade-in anggun setelah hati terbentuk sempurna.
3. Pre-rendered text surface caching (convert_alpha()) untuk performa mulus 120 FPS.
"""

from dataclasses import dataclass
import math
import random
import sys
import pygame


@dataclass(frozen=True)
class Config:
    width: int = 1000
    height: int = 1000
    fps: int = 120
    bg_color: tuple[int, int, int] = (12, 0, 8)
    center_color: tuple[int, int, int] = (255, 235, 240)
    caption: str = "I love you <3"

    scale: int = 20
    y_offset: int = -45

    n_outline: int = 160
    n_fill: int = 130
    n_floating: int = 1000

    outline_gap: int = 22
    fill_gap: int = 30

    frames_per_step: float = 0.075
    fill_delay_offset: int = 18
    center_delay: int = 40
    fade_speed_min: int = 15
    fade_speed_rand: int = 8

    heart_words: tuple[str, ...] = ("i love you", "I LOVE YOU", "love you")
    center_text: str = " I Love you"
    float_words: tuple[str, ...] = ("love", "♥", "love you", "❤")

    colors: tuple[tuple[int, int, int], ...] = (
        (255, 20, 20),
        (220, 20, 60),
        (255, 0, 0),
        (178, 34, 34),
        (255, 60, 60),
    )

    @property
    def center(self) -> tuple[float, float]:
        return self.width / 2.0, self.height / 2.0


CFG = Config()


def heart_parametric(t: float) -> tuple[float, float]:
    """Rumus kurva parametrik hati."""
    x = 16.0 * (math.sin(t) ** 3)
    y = 13.0 * math.cos(t) - 5.0 * math.cos(2.0 * t) - 2.0 * math.cos(3.0 * t) - math.cos(4.0 * t)
    return x, -y


def heart_to_screen(hx: float, hy: float) -> tuple[float, float]:
    """Mengonversi koordinat parametrik ke koordinat layar."""
    sx = hx * CFG.scale + CFG.center[0]
    sy = hy * CFG.scale + CFG.center[1] + CFG.y_offset
    return sx, sy


class HeartParticle:
    """Kelas partikel teks dengan optimasi __slots__."""

    __slots__ = (
        "x",
        "y",
        "base_x",
        "base_y",
        "order",
        "kind",
        "word",
        "color",
        "alpha",
        "flicker",
        "delay",
        "size_mult",
        "surface",
        "float_speed_y",
        "float_speed_x",
    )

    def __init__(
        self,
        x: float,
        y: float,
        order: int,
        kind: str,
        word: str,
        color: tuple[int, int, int],
        surface: pygame.Surface,
        delay: float,
        float_speed_y: float = 0.0,
        float_speed_x: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.order = order
        self.kind = kind
        self.word = word
        self.color = color
        self.surface = surface
        self.delay = delay
        self.alpha = 0.0
        self.flicker = random.uniform(0.0, 2.0 * math.pi)
        self.size_mult = random.uniform(0.95, 1.05)
        self.float_speed_y = float_speed_y
        self.float_speed_x = float_speed_x

    def update(self, step: float) -> None:
        """Memperbarui transparansi, goyangan, dan posisi partikel."""
        if step >= self.delay and self.alpha < 255.0:
            speed = CFG.fade_speed_min + random.uniform(0, CFG.fade_speed_rand)
            self.alpha = min(255.0, self.alpha + speed * CFG.frames_per_step)

        self.flicker += 0.016

        if self.kind == "floating":
            self.y -= self.float_speed_y
            self.x += self.float_speed_x + math.sin(self.flicker) * 0.20
            if self.y < -30:
                self.y = CFG.height + random.uniform(10, 60)
                self.x = random.uniform(40, CFG.width - 40)
        else:
            # Goyangan lembut halus
            self.x = self.base_x + math.sin(self.flicker) * 0.85
            self.y = self.base_y + math.cos(self.flicker * 0.8) * 0.60

    def draw(self, screen: pygame.Surface) -> None:
        """Menggambar partikel dengan efek flicker kedip lembut."""
        if self.alpha <= 0.0:
            return

        flicker_factor = 0.82 + 0.18 * math.sin(self.flicker)
        max_limit = 140 if self.kind == "floating" else 255
        current_alpha = int(min(max_limit, self.alpha) * flicker_factor)
        if current_alpha <= 0:
            return

        self.surface.set_alpha(current_alpha)
        rect = self.surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.surface, rect)


def is_inside_polygon(px: float, py: float, poly: list[tuple[float, float]]) -> bool:
    """Ray casting algorithm untuk mendeteksi apakah titik berada di dalam poligon hati."""
    inside = False
    n = len(poly)
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if py > min(p1y, p2y) and py <= max(p1y, p2y):
            if px <= max(p1x, p2x):
                xinters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x if p1y != p2y else p1x
                if p1x == p2x or px <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def create_text_cache() -> dict[tuple[str, tuple[int, int, int]], pygame.Surface]:
    """Pre-rendered text surface caching (convert_alpha()) dengan font Georgia Bold."""
    font_main = pygame.font.SysFont("georgia", 13, bold=True)
    # Gunakan font simbol untuk render glyph hati yang rapi
    font_heart = pygame.font.SysFont("segoeuisymbol", 14)

    cache: dict[tuple[str, tuple[int, int, int]], pygame.Surface] = {}
    all_words = tuple(dict.fromkeys(CFG.heart_words + CFG.float_words))

    for word in all_words:
        font_to_use = font_heart if word in ("♥", "❤") else font_main
        for color in CFG.colors:
            rendered = font_to_use.render(word, True, color).convert_alpha()
            cache[(word, color)] = rendered

    return cache


def generate_all_particles(
    cache: dict[tuple[str, tuple[int, int, int]], pygame.Surface],
) -> tuple[list[HeartParticle], list[HeartParticle], list[HeartParticle]]:
    """Menghasilkan partikel outline, fill, dan floating persis seperti di video."""
    # Polygon kontur hati untuk pengujian posisi dalam
    poly_boundary = [heart_to_screen(*heart_parametric(i * 2.0 * math.pi / 240)) for i in range(240)]

    # 1. Partikel Outline (Muncul memutar searah jarum jam dari atas ke bawah)
    outline_particles: list[HeartParticle] = []
    for i in range(CFG.n_outline):
        t = i * 2.0 * math.pi / CFG.n_outline
        hx, hy = heart_parametric(t)
        sx, sy = heart_to_screen(hx, hy)
        sx += random.uniform(-1.0, 1.0)
        sy += random.uniform(-1.0, 1.0)

        word = random.choice(CFG.heart_words)
        color = random.choice(CFG.colors)
        delay = (i / CFG.n_outline) * float(CFG.fill_delay_offset)

        outline_particles.append(
            HeartParticle(
                x=sx,
                y=sy,
                order=i,
                kind="outline",
                word=word,
                color=color,
                surface=cache[(word, color)],
                delay=delay,
            )
        )

    # 2. Partikel Fill (Mengisi bagian dalam dengan fill_gap=30, urut dari bawah ke atas)
    fill_points: list[tuple[float, float]] = []
    attempts = 0
    while len(fill_points) < CFG.n_fill and attempts < 15000:
        attempts += 1
        rx = random.uniform(180, 820)
        ry = random.uniform(140, 800)

        if not is_inside_polygon(rx, ry, poly_boundary):
            continue

        # Beri jarak terhadap outline
        if any(math.hypot(rx - ox.base_x, ry - ox.base_y) < CFG.outline_gap for ox in outline_particles):
            continue

        # Jaga jarak antar partikel fill (fill_gap)
        if any(math.hypot(rx - fx, ry - fy) < CFG.fill_gap for fx, fy in fill_points):
            continue

        fill_points.append((rx, ry))

    # Urutkan partikel fill dari bawah (y terbesar) ke atas (y terkecil)
    fill_points.sort(key=lambda pt: -pt[1])

    fill_particles: list[HeartParticle] = []
    fill_span = float(CFG.center_delay - CFG.fill_delay_offset)
    for i, (fx, fy) in enumerate(fill_points):
        word = random.choice(CFG.heart_words)
        color = random.choice(CFG.colors)
        delay = float(CFG.fill_delay_offset) + (i / max(1, len(fill_points))) * fill_span

        fill_particles.append(
            HeartParticle(
                x=fx,
                y=fy,
                order=i,
                kind="fill",
                word=word,
                color=color,
                surface=cache[(word, color)],
                delay=delay,
            )
        )

    # 3. Partikel Floating (Melayang perlahan di latar belakang)
    float_particles: list[HeartParticle] = []
    for i in range(CFG.n_floating):
        fx = random.uniform(30, CFG.width - 30)
        fy = random.uniform(120, CFG.height + 100)

        word = random.choice(CFG.float_words)
        color = random.choice(CFG.colors)
        delay = random.uniform(0.0, float(CFG.center_delay + 20))
        speed_y = random.uniform(0.12, 0.45)
        speed_x = random.uniform(-0.08, 0.08)

        float_particles.append(
            HeartParticle(
                x=fx,
                y=fy,
                order=i,
                kind="floating",
                word=word,
                color=color,
                surface=cache[(word, color)],
                delay=delay,
                float_speed_y=speed_y,
                float_speed_x=speed_x,
            )
        )

    return outline_particles, fill_particles, float_particles


def main() -> None:
    """Inisialisasi Pygame dan loop animasi utama."""
    pygame.init()
    screen = pygame.display.set_mode((CFG.width, CFG.height))
    pygame.display.set_caption(CFG.caption)
    clock = pygame.time.Clock()

    text_cache = create_text_cache()
    outline_p, fill_p, float_p = generate_all_particles(text_cache)

    # Pre-render teks tengah " I Love you" ukuran 54
    center_font = pygame.font.SysFont("georgia", 54, bold=True)
    center_surf = center_font.render(CFG.center_text, True, CFG.center_color).convert_alpha()
    glow_surf = center_font.render(CFG.center_text, True, (255, 20, 60)).convert_alpha()
    center_rect = center_surf.get_rect(center=(int(CFG.center[0]), int(CFG.center[1] + CFG.y_offset - 10)))

    step = 0.0
    center_alpha = 0.0
    center_pulse = 0.0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        step += CFG.frames_per_step
        screen.fill(CFG.bg_color)

        # 1. Update dan gambar partikel floating di latar belakang
        for p in float_p:
            p.update(step)
            p.draw(screen)

        # 2. Update dan gambar partikel outline dan fill
        for p in outline_p:
            p.update(step)
            p.draw(screen)

        for p in fill_p:
            p.update(step)
            p.draw(screen)

        # 3. Kemunculan teks tengah " I Love you" (step > center_delay + 80)
        if step > (CFG.center_delay + 80):
            if center_alpha < 255.0:
                center_alpha = min(255.0, center_alpha + 0.30)

            center_pulse += 0.009
            pulse_y = math.sin(center_pulse) * 1.5

            glow_surf.set_alpha(int(center_alpha * 0.7))
            screen.blit(glow_surf, (center_rect.x, center_rect.y + pulse_y + 2))

            center_surf.set_alpha(int(center_alpha))
            screen.blit(center_surf, (center_rect.x, center_rect.y + pulse_y))

        pygame.display.flip()
        clock.tick(CFG.fps)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
