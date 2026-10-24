# Air Hockey Berbasis Deteksi Objek

Final Project 1 mata kuliah Pengolahan Citra dan Video.

Proyek ini merupakan game **Air Hockey** yang mengontrol paddle pemain menggunakan posisi objek yang terdeteksi melalui kamera. Sistem deteksi objek menggunakan OpenCV dan pemrosesan citra berbasis threshold warna, sedangkan game dibuat menggunakan library Arcade.

## Fitur

- Deteksi objek secara real-time menggunakan kamera.
- Pengontrolan paddle pemain berdasarkan posisi centroid objek.
- Pemilihan ruang warna:
  - BGR
  - HLS
  - HSV
  - LAB
  - YUV
  - YCrCb
- Pengaturan nilai minimum dan maksimum setiap channel.
- Auto Threshold berdasarkan area objek yang dipilih pada kamera.
- Tampilan frame hasil pemrosesan dan threshold.
- Game Air Hockey dengan:
  - Paddle pemain
  - Paddle musuh berbasis AI
  - Puck dengan fisika sederhana
  - Sistem skor
  - Sistem gol dan serve
- Penyimpanan konfigurasi threshold ke file JSON.

## Teknologi yang Digunakan

- Python 3.10
- OpenCV
- NumPy
- Arcade
- Kamera/webcam

## Struktur Proyek

```text
PCV-Project-1/
├── config/
│   └── saved_setting.json
├── src/
│   ├── main.py
│   └── include/
│       ├── detection_settings_view.py
│       ├── entity.py
│       ├── game_view.py
│       ├── image_processing.py
│       ├── menu_view.py
│       └── shared.py
├── run.sh
└── README.md
```

## Instalasi

Pastikan Python 3.10 atau versi yang kompatibel sudah terpasang.

Buat dan aktifkan virtual environment:

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependency:

```bash
pip install arcade opencv-python numpy
```

Pastikan webcam sudah terhubung dan dapat diakses oleh sistem operasi.

## Menjalankan Program

Dari root repository, jalankan:

```bash
./run.sh
```

Atau jalankan secara langsung:

```bash
./.venv/bin/python3.10 ./src/main.py
```

Menu utama menyediakan tiga pilihan:

1. **Play** — memulai permainan Air Hockey.
2. **Calibrate Camera** — membuka halaman konfigurasi deteksi objek dan threshold.
3. **Quit** — menutup aplikasi.

## Kalibrasi Kamera dan Auto Threshold

Sebelum bermain, lakukan kalibrasi objek yang akan digunakan sebagai kontrol paddle:

1. Buka menu **Calibrate Camera**.
2. Pilih ruang warna yang sesuai dengan kondisi pencahayaan.
3. Klik tombol **Auto Threshold**.
4. Klik dan drag area objek pada window kamera.
5. Sistem mengambil nilai minimum dan maksimum setiap channel secara otomatis.
6. Jika diperlukan, sesuaikan nilai threshold menggunakan slider.
7. Klik **Save** untuk menyimpan konfigurasi.
8. Klik **Back**, kemudian pilih **Play**.

Objek dengan area kontur terbesar digunakan sebagai objek kontrol. Posisi centroid objek dinormalisasi dan dipetakan ke posisi paddle pemain pada area permainan.

[![Watch the video](https://raw.githubusercontent.com/Machive5/PCV-Project-1/main/assets/threshold_video.mp4)](https://raw.githubusercontent.com/Machive5/PCV-Project-1/main/assets/threshold_video.mp4)

## Cara Bermain

- Letakkan objek berwarna yang digunakan sebagai controller di depan kamera.
- Gerakkan objek untuk menggerakkan paddle pemain.
- Pada awal ronde, pukul puck menggunakan paddle pemain.
- Arahkan puck ke gawang lawan.
- Paddle musuh dikendalikan oleh AI.
- Pemain mendapatkan skor ketika puck masuk ke gawang lawan.

[![Watch the video](https://raw.githubusercontent.com/Machive5/PCV-Project-1/main/assets/play_game_video.mp4)](https://raw.githubusercontent.com/Machive5/PCV-Project-1/main/assets/play_game_video.mp4)

## Alur Sistem

```text
Webcam
   │
   ▼
Frame Capture
   │
   ▼
Konversi Ruang Warna
   │
   ▼
Thresholding
   │
   ▼
Erosi dan Dilasi
   │
   ▼
Deteksi Kontur
   │
   ▼
Kontur Terbesar dan Centroid
   │
   ▼
Normalisasi Posisi Objek
   │
   ▼
Pergerakan Paddle Pemain
```
## Catatan

- Pastikan pencahayaan cukup agar objek dapat terdeteksi dengan stabil.
- Gunakan objek dengan warna yang berbeda dari latar belakang.
- Jika paddle bergerak tidak stabil, sesuaikan kembali threshold atau gunakan ruang warna lain.
- Kamera default yang digunakan adalah kamera dengan index `0`.
- Konfigurasi threshold tersimpan pada `config/saved_setting.json`.

## Pembagian Modul

| Modul | Deskripsi |
|---|---|
| `main.py` | Inisialisasi window, view, object detection, dan konfigurasi |
| `image_processing.py` | Pengambilan frame, thresholding, kontur, dan posisi objek |
| `detection_settings_view.py` | UI kalibrasi threshold |
| `game_view.py` | Arena, gameplay, skor, dan state permainan |
| `entity.py` | Implementasi paddle, enemy, dan puck |
| `menu_view.py` | Menu utama aplikasi |
| `shared.py` | Variabel bersama antara deteksi objek dan game |
