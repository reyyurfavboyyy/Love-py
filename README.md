# Heart Game - Romantic Text Particle Animation ❤️

Animasi partikel teks berbentuk hati (*heart*) interaktif menggunakan **Python** dan **Pygame** dengan performa 120 FPS.

## ✨ Fitur
- **Animasi Kontur Hati (*Outline*)**: Partikel teks muncul melingkari kurva hati secara searah jarum jam (*clockwise*).
- **Pengisian Hati (*Fill*)**: Partikel memenuhi rongga dalam hati dari bawah ke atas (*bottom-up*).
- **Partikel Melayang (*Floating*)**: Partikel kata cinta dan simbol hati (`♥`, `❤`) melayang lembut di latar belakang.
- **Teks Tengah Epik**: Teks `" I Love you"` bermekaran perlahan di tengah layar dengan efek pendar (*glow*).
- **High Performance (120 FPS)**: Menggunakan teknik *pre-rendered text surface caching* (`convert_alpha()`) dan optimasi `__slots__`.

## 🚀 Cara Menjalankan

1. Pastikan Python 3.10+ sudah terinstal.
2. Pasang library `pygame`:
   ```bash
   pip install pygame
   ```
3. Jalankan script:
   ```bash
   python Heart_Game.py
   ```
4. Tekan tombol `Esc` atau tombol silang pada jendela untuk keluar.
