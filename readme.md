# 🤖 Prima Astro — Agentic AI Sparepart Management

Aplikasi AI untuk manajemen sparepart berbasis **CrewAI** dengan fitur:
- **Web Dashboard** — Monitoring stok real-time, low stock alerts, dan demand forecasting (Prophet)
- **AI Assistant** — Chatbot cerdas untuk query inventori menggunakan bahasa natural
- **Telegram Bot** — Akses AI Assistant langsung dari Telegram
- **Demand Forecasting** — Prediksi kebutuhan sparepart 30 hari ke depan menggunakan Facebook Prophet

---

## 📋 Prasyarat

- **Python** v3.10+ (pastikan centang "Add Python to PATH" saat instalasi)
- **Git** (opsional, untuk clone repository)

---

## 🚀 Cara Install

### 1. Clone Repository

```powershell
git clone https://github.com/findryankp/astroboy.git
cd astroboy
```

### 2. Buat dan Aktifkan Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

> ⚠️ **Jika muncul error merah terkait kebijakan PowerShell:**
> Buka PowerShell sebagai **Administrator**, jalankan perintah berikut, lalu coba lagi:
> ```powershell
> Set-ExecutionPolicy Unrestricted -Force
> ```

### 3. Install Semua Dependencies

```powershell
pip install -r requirements.txt
```

> 💡 **Catatan untuk Python v3.14+:**
> Jika Anda menggunakan Python v3.14 atau yang lebih baru, jalankan instalasi dengan mengabaikan pembatasan versi Python agar dependency versi terbaru dapat teresolusi dengan benar:
> ```powershell
> pip install -r requirements.txt --ignore-requires-python
> ```

### 4. Konfigurasi Environment Variables

Copy file `.env.example` menjadi `.env`, lalu isi dengan konfigurasi Anda:

```powershell
copy .env.example .env
```

Buka file `.env` dengan text editor dan isi nilainya:

```env
# Pilih LLM provider: "ollama" (lokal) atau "gemini" (cloud, lebih cepat)
LLM_PROVIDER=gemini

# Wajib diisi jika LLM_PROVIDER=gemini
# Dapatkan API Key gratis di: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Wajib diisi jika ingin menjalankan Telegram Bot
# Dapatkan token dari @BotFather di Telegram
TELEGRAM_TOKEN=your_telegram_bot_token_here
```

### 5. Siapkan Database

Jalankan script migrasi untuk mengubah file JSON mentah menjadi database SQLite:

```powershell
python database.py
```

### 6. Siapkan Redis (Wajib — untuk Antrian Query)

Web Dashboard dan Telegram Bot mengirim setiap pertanyaan AI Assistant ke antrian **Celery + Redis**, supaya keduanya diproses satu per satu (tidak nyerobot LLM secara bersamaan). Redis harus berjalan sebelum menjalankan aplikasi.

- **Docker (paling mudah):**
  ```powershell
  docker run -d --name redis -p 6379:6379 redis
  ```
- **WSL:** `sudo apt install redis-server && redis-server`
- **Windows native:** gunakan [Memurai](https://www.memurai.com/) (Redis-compatible untuk Windows)

Konfigurasi broker/backend ada di `.env` (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`), default `redis://localhost:6379/0`.

### 7. (Opsional) Install Ollama — Jika menggunakan LLM Lokal

Langkah ini **hanya diperlukan** jika Anda memilih `LLM_PROVIDER=ollama` di file `.env`.

1. Unduh dan instal Ollama dari: **[https://ollama.com/download/windows](https://ollama.com/download/windows)**
2. Buka terminal baru dan jalankan:
   ```powershell
   ollama run llama3.1
   ```
   *(Tunggu proses unduhan model selesai, ukuran beberapa GB)*

---

## ▶️ Cara Menjalankan

Pastikan Anda selalu berada di folder project, **Virtual Environment sudah aktif** (`.\venv\Scripts\activate`), dan **Redis sudah berjalan** (lihat langkah 6 di atas).

### A. Celery Worker (Wajib — jalankan pertama)

Buka satu terminal khusus untuk worker yang memproses antrian query AI Assistant:

```powershell
.\venv\Scripts\activate
celery -A celery_app worker --loglevel=info --pool=solo
```

> `--pool=solo` dipakai karena Celery `prefork` (default) tidak didukung di Windows.

### B. Web Dashboard & AI Chat (Browser)

```powershell
uvicorn api:app --reload
```

Buka browser dan akses: 👉 **http://localhost:8000**

Fitur yang tersedia di dashboard:
| Menu | Fungsi |
|------|--------|
| **Dashboard** | Overview stok, low stock alerts, transaksi terbaru |
| **Forecasting** | Prediksi demand sparepart 30 hari ke depan (Prophet AI) |
| **AI Assistant** | Chatbot cerdas untuk tanya jawab inventori |

### C. Telegram Bot

Buka terminal **baru** (terpisah dari web dashboard & worker):

```powershell
.\venv\Scripts\activate
python main.py
```

Buka Telegram, cari bot Anda, dan mulai chat!

> 💡 **Tips:** Anda perlu menjalankan Redis, Celery Worker (A), Web Dashboard (B), dan Telegram Bot (C) secara bersamaan di terminal yang berbeda. Semuanya berbagi antrian dan database yang sama, jadi setiap pertanyaan (dari web maupun Telegram) diproses satu per satu oleh worker.

---

## 📁 Struktur Project

```
agenticai/
├── api.py                 # FastAPI server (Web Dashboard + REST API)
├── main.py                # Telegram Bot entry point
├── agent.py               # CrewAI Agents (Stock/Transaction/Analytics) & Tools
├── celery_app.py          # Celery app config (Redis broker/backend)
├── tasks.py               # Celery task that runs the CrewAI crew
├── analytics.py           # Trend analysis & Prophet forecasting
├── database.py            # Database migration script (JSON → SQLite)
├── stock_manager.py       # Stock checking logic
├── transaction_manager.py # Transaction query logic
├── sparepart.db           # SQLite database (generated)
├── requirements.txt       # Python dependencies
├── .env.example           # Template environment variables
├── .env                   # Environment variables (tidak di-commit)
└── static/
    ├── index.html          # Web Dashboard UI
    ├── style.css           # Dashboard styling (dark theme)
    └── app.js              # Dashboard frontend logic
```

---

## 🛠️ Konfigurasi LLM Provider

Aplikasi ini mendukung **2 provider LLM** yang bisa diganti kapan saja melalui file `.env`:

| Provider | `LLM_PROVIDER` | Kelebihan | Kekurangan |
|----------|----------------|-----------|------------|
| **Google Gemini** | `gemini` | Cepat, tidak membebani laptop | Butuh internet & API Key |
| **Ollama (Lokal)** | `ollama` | Gratis 100%, offline | Butuh RAM/GPU besar, lebih lambat |

Untuk mengganti provider, cukup ubah nilai `LLM_PROVIDER` di file `.env` dan restart aplikasi.

---

## 📝 Contoh Pertanyaan untuk AI Assistant

- *"Berapa sisa stock PALU KARET?"*
- *"Tampilkan barang dengan stok menipis"*
- *"Siapa yang sering ambil KAWAT LAS?"*
- *"Prediksi kebutuhan OLI SUPER SLIDE bulan depan"*
- *"Lihat transaksi keluar departemen produksi"*
