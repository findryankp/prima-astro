# Panduan Lengkap: Cara Install & Run Agentic AI (Windows 11)

Aplikasi ini sekarang memiliki dua fitur utama: **Web Dashboard (UI)** dan **Telegram Bot**. Anda dapat menjalankan salah satu atau keduanya secara bersamaan. Ikuti panduan di bawah ini langkah demi langkah.

---

## BAGIAN 1: CARA INSTALL (Persiapan Awal)

Lakukan langkah-langkah ini hanya sekali di awal pembuatan project.

**Prasyarat:** Pastikan Anda sudah menginstal Python (v3.10+) dan mencentang "Add Python to PATH" saat proses instalasi.

1. **Buka Terminal di Folder Project**
   - Buka folder `c:\Projects\agenticai`.
   - Klik kanan di ruang kosong, lalu pilih **"Open in Terminal"** (PowerShell).

2. **Buat dan Aktifkan Virtual Environment**
   Ketikan perintah ini secara berurutan:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
   *(Catatan: Jika muncul error berwarna merah karena kebijakan PowerShell, buka PowerShell sebagai Administrator lalu jalankan `Set-ExecutionPolicy Unrestricted -Force`, setelah itu coba aktifkan lagi).*

3. **Install Semua Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Siapkan Database**
   Kita perlu mengubah file JSON mentah menjadi database SQLite agar cepat dibaca oleh sistem:
   ```powershell
   python database.py
   ```

5. **Install Local LLM (Ollama)**
   Karena kita menggunakan AI secara lokal agar gratis 100%, ikuti langkah ini:
   - Unduh dan instal Ollama dari: **[https://ollama.com/download/windows](https://ollama.com/download/windows)**
   - Setelah terinstal, tutup terminal ini dan buka terminal/PowerShell baru.
   - Jalankan perintah berikut untuk mengunduh model bahasa:
     ```powershell
     ollama run llama3
     ```
     *(Tunggu proses unduhan beberapa GB selesai).*

---

## BAGIAN 2: CARA RUN (Menjalankan Aplikasi)

Pilih cara yang Anda inginkan (A, B, atau keduanya). **Pastikan Anda selalu berada di dalam folder project dan Virtual Environment (venv) sudah aktif** (`.\venv\Scripts\activate`).
**Serta pastikan aplikasi Ollama sedang berjalan di latar belakang!**

### A. Menjalankan Web Dashboard & Chat UI (di Browser)
1. Buka terminal (PowerShell) di folder project.
2. Aktifkan venv: `.\venv\Scripts\activate`
3. Jalankan server FastAPI dengan perintah berikut:
   ```powershell
   uvicorn api:app --reload
   ```
4. Buka Browser Anda (Chrome/Edge/dll) dan buka alamat:
   👉 **http://localhost:8000**
5. Anda bisa melihat Dashboard dan melakukan chat dengan AI di menu "AI Assistant".

### B. Menjalankan Telegram Bot
1. Buka terminal (PowerShell) **BARU** di folder project.
2. Aktifkan venv di terminal baru ini: `.\venv\Scripts\activate`
3. Jalankan script Telegram:
   ```powershell
   python main.py
   ```
4. Buka aplikasi Telegram Anda, cari Bot Anda, dan mulai ngobrol!

> **💡 Tips:** Anda bisa menjalankan terminal untuk Web (A) dan terminal untuk Telegram (B) secara bersamaan di background. Keduanya akan menggunakan data dari database yang sama!
