# love_pen_animation.py
import turtle
import math
import time
import os
import sys
import urllib.request
from io import BytesIO

# Untuk konversi PNG -> GIF
try:
    from PIL import Image
except Exception:
    print("Pillow tidak ditemukan. Install dulu dengan:\n    pip install pillow")
    raise

# --------- KONFIGURASI ---------
PEN_IMAGE_URL = "https://toppng.com/uploads/preview/hand-holding-a-pen-png-free-png-images-77434.png"
# Jika unduhan gagal, simpan gambar secara manual sebagai 'pen.png' di folder yang sama.
LOCAL_PNG = "pen.png"
LOCAL_GIF = "pen.gif"

HEART_SCALE = 10      # skala kurva hati
DRAW_DELAY = 0.005    # jeda antara titik menggambar (lebih kecil = lebih cepat)
PEN_SIZE = 3
TEXT = "I Loved Yudha"   # teks akhir
# -------------------------------

def download_image(url, out_path):
    try:
        print("Mengunduh gambar pulpen...")
        resp = urllib.request.urlopen(url, timeout=15)
        data = resp.read()
        with open(out_path, "wb") as f:
            f.write(data)
        print("Selesai mengunduh ->", out_path)
        return True
    except Exception as e:
        print("Gagal mengunduh otomatis:", e)
        return False

def convert_png_to_gif(png_path, gif_path):
    try:
        img = Image.open(png_path)
        # pastikan ukuran tidak terlalu besar agar turtle tidak berat
        max_size = (120, 120)
        img.thumbnail(max_size, Image.ANTIALIAS)
        # Convert RGBA -> P mode untuk GIF transparan
        if img.mode in ("RGBA", "LA"):
            alpha = img.split()[-1]
            bg = Image.new("RGBA", img.size, (255,255,255,0))
            bg.paste(img, mask=alpha)
            img = bg.convert("RGBA")
        img = img.convert("P", palette=Image.ADAPTIVE)
        img.save(gif_path, format="GIF", transparency=0)
        print("Konversi PNG->GIF selesai ->", gif_path)
        return True
    except Exception as e:
        print("Gagal konversi PNG->GIF:", e)
        return False

def heart_point(i_deg):
    # Rumus parametik klasik untuk bentuk hati (lemniscate-like)
    i = math.radians(i_deg)
    x = 16 * math.sin(i)**3
    y = 13 * math.cos(i) - 5 * math.cos(2*i) - 2 * math.cos(3*i) - math.cos(4*i)
    return x * HEART_SCALE, y * HEART_SCALE

def play_ding_if_windows():
    if sys.platform.startswith("win"):
        try:
            import winsound
            # Mainkan sound system "Asterisk" jika tersedia
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            try:
                winsound.Beep(800, 250)
            except Exception:
                pass

def fade_in_text(turtle_obj, text, pos=(0, -30), steps=10, delay=0.08):
    # Simulasi fade-in dengan menggambar teks berulang-ulang dari warna terang ke gelap
    turtle_obj.penup()
    turtle_obj.hideturtle()
    x, y = pos
    grey_values = [int(255 - (255 * (i/steps))) for i in range(steps)]
    # Buat daftar warna hex dari abu-abu terang ke hitam
    colors = [f"#{v:02x}{v:02x}{v:02x}" for v in grey_values]
    for c in colors:
        turtle_obj.clear()
        turtle_obj.goto(x, y)
        turtle_obj.color(c)
        turtle_obj.write(text, align="center", font=("Arial", 28, "bold"))
        time.sleep(delay)
    # Pastikan teks hitam penuh di akhir
    turtle_obj.clear()
    turtle_obj.color("black")
    turtle_obj.goto(x, y)
    turtle_obj.write(text, align="center", font=("Arial", 28, "bold"))

def main():
    # 1) Pastikan ada file PNG lokal (coba unduh otomatis)
    if not os.path.exists(LOCAL_PNG):
        ok = download_image(PEN_IMAGE_URL, LOCAL_PNG)
        if not ok:
            print("\nGagal unduh otomatis. Silakan letakkan file gambar pulpen (PNG transparan) sebagai 'pen.png' di folder ini lalu jalankan ulang.")
            return

    # 2) Konversi PNG -> GIF (turtle membutuhkan GIF untuk shape)
    if not os.path.exists(LOCAL_GIF):
        ok = convert_png_to_gif(LOCAL_PNG, LOCAL_GIF)
        if not ok:
            print("\nGagal konversi. Pastikan Pillow terpasang dan file PNG valid.")
            return

    # 3) Setup turtle
    screen = turtle.Screen()
    screen.setup(width=800, height=700)
    screen.title("Love being drawn by elegant pen")
    screen.bgcolor("white")

    # Register shape for pen
    try:
        screen.addshape(LOCAL_GIF)
    except Exception as e:
        print("Gagal mendaftarkan shape GIF:", e)
        return

    # Turtles: drawer akan menggambar garis; pen_turtle akan mengikuti bentuk sebagai sprite pulpen
    drawer = turtle.Turtle()
    drawer.hideturtle()
    drawer.speed(0)
    drawer.color("black")
    drawer.width(PEN_SIZE)

    pen_turtle = turtle.Turtle()
    pen_turtle.hideturtle()
    pen_turtle.shape(LOCAL_GIF)
    pen_turtle.penup()
    pen_turtle.speed(0)

    # Hitung titik-titik hati
    points = []
    for i in range(0, 361):
        x, y = heart_point(i)
        points.append((x, y))

    # Pindah ke titik awal tanpa menggambar
    start_x, start_y = points[0]()
