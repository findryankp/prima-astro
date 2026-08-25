# ⚙️ Mekanisme Kerja — Prima Astro Agentic AI

Dokumen ini menjelaskan secara lengkap bagaimana project **Prima Astro** bekerja, mulai dari arsitektur sistem, teknologi yang digunakan, hingga alur data dari ujung ke ujung.

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                         │
│                                                                     │
│    ┌─────────────┐ ┌───────────────┐     ┌─────────────┐            │
│    │ Web Browser │ │REST API Client│     │ Telegram App│            │
│    │ (Dashboard) │ │(Postman, dll) │     │             │            │
│    └──────┬──────┘ └───────┬───────┘     └──────┬──────┘            │
│           │                │                    │                   │
└───────────┼────────────────┼────────────────────┼───────────────────┘
            │                │                    │
            └───────┬────────┘                    │
                    ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                            │
│                                                                     │
<<<<<<< HEAD
│  ┌──────────────────────┐    ┌──────────────────────────────┐       │
│  │  FastAPI Server       │    │  Telegram Bot (python-       │       │
│  │  (app/delivery/http)  │    │  telegram-bot)               │       │
│  │                       │    │  (app/delivery/telegram)     │       │
│  │                       │    │                              │       │
│  │  • GET  /             │    │  • /start command            │       │
│  │  • POST /api/chat     │    │  • Text message handler      │       │
│  │  • GET  /api/dashboard│    │                              │       │
│  │  • GET  /api/stock    │    │                              │       │
│  │  • GET  /api/forecast │    │                              │       │
│  │  • GET  /api/items    │    │                              │       │
│  └──────────┬───────────┘    └──────────────┬───────────────┘       │
│             │                               │                       │
│             └───────────────┬───────────────┘                       │
│                             ▼                                       │
│              ┌──────────────────────────┐                           │
│              │  Celery Queue (Redis)     │                           │
│              │  1 request diproses       │                           │
│              │  satu per satu            │                           │
│              └──────────┬───────────────┘                           │
│                         ▼                                           │
│              ┌──────────────────────────┐                           │
│              │   CrewAI Crew Engine      │                           │
│              │   (app/agent/crew.py)     │                           │
│              │                          │                           │
│              │   Manager Agent (auto)   │                           │
│              │   delegates ke:          │                           │
│              │   • Stock Specialist     │                           │
│              │   • Transaction Spec.    │                           │
│              │   • Analytics Specialist │                           │
│              │   • Purchasing Spec.     │                           │
│              │   • Cost Insight Spec.   │                           │
│              └──────────┬───────────────┘                           │
│                         │  (lewat app/agent/tools.py)                │
│          ┌──────────────┼──────────────────────┐                    │
│          ▼              ▼                      ▼                    │
│  ┌──────────────┐ ┌───────────────┐  ┌────────────────┐            │
│  │ stock_        │ │ transaction_  │  │   analytics_   │            │
│  │ usecase.py    │ │ usecase.py    │  │   usecase.py   │            │
│  │              │ │               │  │                │            │
│  │ • check_stock│ │ • view_outgo- │  │ • analyze_     │            │
│  │ • get_low_   │ │   ing_stock   │  │   sparepart_   │            │
│  │   stock      │ │ • get_top_    │  │   trend        │            │
│  │              │ │   users       │  │ • predict_     │            │
│  │              │ │               │  │   monthly_needs│            │
│  │              │ │               │  │ • get_forecast │            │
│  │              │ │               │  │   _data / insights │        │
│  └──────┬───────┘ └──────┬────────┘  └───────┬────────┘            │
│         │                │                   │                      │
│         └────────────────┴───────────────────┘                      │
│                          ▼ (app/repository/*.py — satu-satunya       │
│                            layer yang menyentuh SQL)                 │
=======
│      ┌─────────────────────────┐  ┌─────────────────────────┐       │
│      │ FastAPI Server          │  │ Telegram Bot (python-   │       │
│      │ (app/delivery/http)     │  │ telegram-bot)           │       │
│      │                         │  │ (app/delivery/telegram) │       │
│      │ • GET  /                │  │                         │       │
│      │ • POST /api/chat        │  │ • /start command        │       │
│      │ • GET  /api/dashboard   │  │ • Text message handler  │       │
│      │ • GET  /api/stock       │  │                         │       │
│      │ • GET  /api/forecast    │  │                         │       │
│      │ • GET  /api/items       │  │                         │       │
│      └────────────┬────────────┘  └────────────┬────────────┘       │
│                   │                            │                    │
│                   └──────────────┬─────────────┘                    │
│                                  ▼                                  │
│                    ┌───────────────────────────┐                    │
│                    │ Celery Queue (Redis)      │                    │
│                    │ 1 request diproses        │                    │
│                    │ satu per satu             │                    │
│                    └──────────────┬────────────┘                    │
│                                   ▼                                 │
│                    ┌───────────────────────────┐                    │
│                    │ CrewAI Crew Engine        │                    │
│                    │ (app/agent/crew.py)       │                    │
│                    │                           │                    │
│                    │ Manager Agent (auto)      │                    │
│                    │ delegates ke:             │                    │
│                    │ • Stock Specialist        │                    │
│                    │ • Transaction Spec.       │                    │
│                    │ • Analytics Specialist    │                    │
│                    └──────────────┬────────────┘                    │
│                                   │ (app/agent/tools.py)            │
│           ┌───────────────────────┼───────────────────────┐         │
│           ▼                       ▼                       ▼         │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐    │
│  │ stock_          │   │ transaction_    │   │ analytics_      │    │
│  │ usecase.py      │   │ usecase.py      │   │ usecase.py      │    │
│  │                 │   │                 │   │                 │    │
│  │ • check_stock   │   │ • view_outgo-   │   │ • analyze_trend │    │
│  │ • get_low_stock │   │   ing_stock     │   │ • predict_needs │    │
│  │                 │   │ • get_top_users │   │ • get_forecast  │    │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘    │
│           │                     │                     │             │
│           └─────────────────────┴─────────────────────┘             │
│                                 ▼ (app/repository/*.py)             │
>>>>>>> 870eeb327ec4cd41bc44c3c170faba12e1cf1372
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                │
│                                                                     │
│      ┌───────────────────────────────────────────────────────┐      │
│      │             SQLite Database (sparepart.db)            │      │
│      │                                                       │      │
│      │   ┌─────────────────┐         ┌──────────────────┐    │      │
│      │   │ spareparts      │         │ transactions     │    │      │
│      │   │                 │         │                  │    │      │
│      │   │ • item_number   │◄────────│ • item_number(FK)│    │      │
│      │   │ • product_name  │         │ • product_name   │    │      │
│      │   │ • soh           │         │ • qty_out        │    │      │
│      │   │ • safety_stock  │         │ • department     │    │      │
│      │   │ • status        │         │ • pic            │    │      │
│      │   │ • unit          │         │ • tanggal        │    │      │
│      │   │ • kategori      │         │ • status         │    │      │
│      │   │ • moq           │         │ • keterangan     │    │      │
│      │   │ • last_price    │         │ • nomor_pesanan  │    │      │
│      │   └─────────────────┘         └──────────────────┘    │      │
│      └───────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL AI SERVICE                         │
│                                                                     │
│    ┌────────────────────────┐        ┌────────────────────────┐     │
│    │ Google Gemini API      │        │ Ollama (Local LLM)     │     │
│    │ (gemini-2.5-flash)     │        │ (llama3.1)             │     │
│    │                        │        │                        │     │
│    │ Cloud-based            │        │ Self-hosted            │     │
│    │ via litellm            │        │ localhost:11434        │     │
│    └────────────────────────┘        └────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧰 Teknologi & Framework yang Digunakan

### Backend (Python)

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| **Python** | 3.10+ | Bahasa pemrograman utama |
| **FastAPI** | latest | Web framework untuk REST API & serving dashboard |
| **Uvicorn** | latest | ASGI server untuk menjalankan FastAPI |
| **CrewAI** | latest | Framework Agentic AI — mengorkestrasi agent, task, dan tools |
| **LiteLLM** | latest | Abstraksi universal untuk memanggil berbagai LLM provider |
| **Langchain Google GenAI** | latest | Konektor Langchain untuk Google Gemini |
| **Facebook Prophet** | latest | Library forecasting time-series untuk prediksi demand |
| **Pandas** | latest | Manipulasi dan analisis data tabular |
| **SQLite3** | built-in | Database ringan embedded (tanpa server terpisah) |
| **python-dotenv** | latest | Membaca konfigurasi dari file `.env` |
| **python-telegram-bot** | latest | Library untuk membuat Telegram Bot |

### Frontend (Browser)

| Teknologi | Fungsi |
|-----------|--------|
| **HTML5** | Struktur halaman dashboard |
| **CSS3 (Custom)** | Styling dengan tema dark mode & glassmorphism |
| **JavaScript (Vanilla)** | Logika frontend, fetch API, dan interaktivitas |
| **Chart.js** | Library charting untuk visualisasi grafik forecasting |
| **Select2** | Plugin dropdown dengan fitur pencarian (searchable select) |
| **jQuery** | Dependency untuk Select2 |
| **Google Fonts (Inter)** | Tipografi modern untuk UI |

---

## 🧠 Konsep Agentic AI — Bagaimana AI "Berpikir"

### Apa itu Agentic AI?

Berbeda dengan chatbot biasa yang hanya menjawab berdasarkan teks, **Agentic AI** memiliki kemampuan untuk:
1. **Memahami** pertanyaan pengguna dalam bahasa natural
2. **Memilih tool** yang tepat untuk menjawab pertanyaan tersebut
3. **Mengeksekusi tool** untuk mengambil data nyata dari database
4. **Menyusun jawaban** yang informatif berdasarkan data yang didapat

### Framework: CrewAI

Project ini menggunakan **CrewAI** sebagai framework orkestrasi AI. CrewAI terdiri dari 3 komponen utama:

```
┌─────────────────────────────────────────────────────────────────────┐
│                               CREW                                  │
│                                                                     │
│    ┌───────────────────────────────────────────────────────────┐    │
│    │                           AGENT                           │    │
│    │                                                           │    │
│    │  Role : "Sparepart Inventory Specialist"                  │    │
│    │  Goal : Provide accurate stock data, analyze trends,      │    │
│    │         and predict needs                                 │    │
│    │  LLM  : Gemini 2.5 Flash / Ollama Llama 3.1               │    │
│    │                                                           │    │
│    │      ┌─────────────────────────────────────────────┐      │    │
│    │      │                    TOOLS                    │      │    │
│    │      │                                             │      │    │
│    │      │  > Check Stock                              │      │    │
│    │      │  > Get Low Stock Items                      │      │    │
│    │      │  > View Outgoing Stock                      │      │    │
│    │      │  > Get Top Users of Item                    │      │    │
│    │      │  > Analyze Sparepart Trend                  │      │    │
│    │      │  > Predict Monthly Needs                    │      │    │
│    │      └─────────────────────────────────────────────┘      │    │
│    └───────────────────────────────────────────────────────────┘    │
│                                                                     │
│    ┌───────────────────────────────────────────────────────────┐    │
│    │                           TASK                            │    │
│    │                                                           │    │
│    │  Description : "Answer the user's query: '...'"           │    │
│    │  Expected    : "A helpful answer with actual data"        │    │
│    └───────────────────────────────────────────────────────────┘    │
│                                                                     │
│    Process: Sequential                                              │
└─────────────────────────────────────────────────────────────────────┘
```

#### Komponen CrewAI:

1. **Agent** — Entitas AI yang memiliki peran (`role`), tujuan (`goal`), dan latar belakang (`backstory`). Agent dilengkapi dengan tools dan LLM untuk berpikir.

2. **Task** — Tugas spesifik yang diberikan kepada agent. Dalam project ini, setiap pertanyaan user menjadi 1 task baru.

3. **Crew** — Orkestrator yang menjalankan agent dan task. Menggunakan `Process.sequential` (task dijalankan satu per satu secara berurutan).

### Daftar Tools (Kemampuan AI)

| Tool | File Sumber | Fungsi |
|------|-------------|--------|
| `Check Stock` | `app/usecase/stock_usecase.py` | Mengecek sisa stok (SOH) suatu sparepart berdasarkan nama/nomor item |
| `Get Low Stock Items` | `app/usecase/stock_usecase.py` | Mengambil daftar barang dengan status WARNING atau DANGER |
| `View Outgoing Stock` | `app/usecase/transaction_usecase.py` | Melihat transaksi pengeluaran barang terbaru, bisa filter per departemen |
| `Get Top Users of Item` | `app/usecase/transaction_usecase.py` | Mencari departemen/PIC yang paling banyak menggunakan suatu item |
| `Analyze Sparepart Trend` | `app/usecase/analytics_usecase.py` | Menganalisis tren penggunaan: total pemakaian, rata-rata harian, proyeksi bulanan |
| `Predict Monthly Needs` | `app/usecase/analytics_usecase.py` | Memprediksi kebutuhan 30 hari ke depan menggunakan algoritma Prophet |
| `Get Dashboard Insights` | `app/usecase/analytics_usecase.py` | Insight katalog: item butuh restock, trending naik/turun, total forecast demand (moving-average) |
| `Draft Purchase Order` | `app/usecase/purchasing_usecase.py` | Bikin draft PO dari restock alert — qty order minimal MOQ + estimasi biaya |
| `Get Price Insights` | `app/usecase/pricing_usecase.py` | Item termahal & item dengan nilai stok terbesar (soh x last_price) katalog-wide |
| `Estimate Item Price` | `app/usecase/pricing_usecase.py` | Harga terakhir + nilai stok untuk satu item spesifik |

Tiap tool di atas hanyalah wrapper tipis (`app/agent/tools.py`) yang memanggil fungsi usecase yang sama persis dengan yang dipakai endpoint REST API — jadi chatbot dan dashboard REST selalu konsisten karena berbagi satu business logic. Tiap agent spesialis dirakit di file-nya sendiri di `app/agent/agents/`, jadi nambah agent baru gak perlu ubah `crew.py`.

---

## 🔄 Alur Kerja Sistem (Flow)

### A. Alur Chat (AI Assistant)

```
User mengetik pertanyaan
         │
         ▼
┌──────────────────────┐
│  Frontend (browser)  │─── POST /api/chat ──┐
│  atau Telegram Bot   │                     │
└──────────────────────┘                     │
                                             ▼
                                  ┌──────────────────────┐
                                  │ FastAPI / Telegram   │
                                  │ menerima pesan       │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ CrewAI membuat Task  │
                                  │ baru dari pertanyaan │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Agent "berpikir"     │
                                  │ menggunakan LLM      │
                                  │ (Gemini / Ollama)    │
                                  └──────────┬───────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              ▼              ▼              ▼
                      ┌───────────────┐┌───────────────┐┌───────────────┐
                      │ Tool:         ││ Tool:         ││ Tool:         │
                      │ Check Stock   ││ Analyze Trend ││ Predict Needs │
                      └───────┬───────┘└───────┬───────┘└───────┬───────┘
                              │              │              │
                              └──────────────┼──────────────┘
                                             ▼
                                  ┌──────────────────────┐
                                  │ Query ke SQLite      │
                                  │ Database             │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Data dikirim kembali │
                                  │ ke Agent             │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Agent menyusun       │
                                  │ jawaban final dalam  │
                                  │ bahasa natural       │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Response dikirim     │
                                  │ ke User              │
                                  └──────────────────────┘
```

**Contoh Alur Nyata:**

1. User bertanya: *"Berapa sisa stok PALU KARET?"*
2. CrewAI membuat Task dari pertanyaan tersebut
3. Agent (ditenagai Gemini 2.5 Flash) **menganalisis pertanyaan** dan memutuskan: *"Saya perlu menggunakan tool Check Stock"*
4. Agent **memanggil tool** `Check Stock` dengan input `"PALU KARET"`
5. Tool menjalankan **SQL query** ke database: `SELECT ... FROM spareparts WHERE product_name LIKE '%PALU KARET%'`
6. Database **mengembalikan data**: SOH = 15, Unit = PCS, Status = WARNING
7. Agent **menyusun jawaban**: *"Sisa stok PALU KARET saat ini adalah 15 PCS dengan status WARNING..."*
8. Jawaban dikirim kembali ke user

### B. Alur Forecasting (Prophet)

```
User memilih item dari dropdown
         │
         ▼
┌──────────────────────┐
│  Frontend (browser)  │── GET /api/forecast/{item} ──┐
└──────────────────────┘                              │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ analytics_usecase     │
                                          │ get_forecast_data()   │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ Ambil semua data      │
                                          │ transaksi item        │
                                          │ dari database         │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ Pandas: Group by      │
                                          │ tanggal, sum          │
                                          │ qty_out per hari      │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ Prophet:              │
                                          │ 1. Fit model          │
                                          │ 2. Make future        │
                                          │    dataframe          │
                                          │    (30 hari)          │
                                          │ 3. Predict            │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ Return JSON:          │
                                          │ • dates[]             │
                                          │ • actual[]            │
                                          │ • predicted[]         │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ Chart.js render       │
                                          │ grafik di browser     │
                                          │ • Garis hijau:        │
                                          │   data aktual         │
                                          │ • Garis biru          │
                                          │   putus-putus:        │
                                          │   prediksi AI         │
                                          └───────────────────────┘
```

---

## 🗄️ Mekanisme Database

### Sumber Data

Data berasal dari 2 file JSON mentah:
- `sparepart-table-data.json` — Data master sparepart (stok, safety stock, harga, dll)
- `transaction.json` — Data histori transaksi keluar (tanggal, qty, departemen, PIC)

### Migrasi Data

Script `database.py` mengubah JSON → SQLite:

```
sparepart-table-data.json ──► Tabel: spareparts
transaction.json          ──► Tabel: transactions
```

### Relasi Tabel

Tabel `transactions` memiliki **Foreign Key** `item_number` yang merujuk ke tabel `spareparts`. Ini memungkinkan join data antara master barang dan histori transaksinya.

---

## 🔀 Mekanisme Pemilihan LLM

Sistem mendukung **2 provider LLM** yang bisa dipilih melalui environment variable:

```python
# Dibaca dari file .env
llm_provider = os.getenv("LLM_PROVIDER", "ollama")

if llm_provider == "gemini":
    # Cloud: Google Gemini 2.5 Flash via litellm
    selected_llm = LLM(model="gemini/gemini-2.5-flash")
else:
    # Lokal: Ollama + Llama 3.1
    selected_llm = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")
```

### Perbandingan Provider

```
┌──────────────────┬───────────────────────┬──────────────────────────┐
│                  │   Gemini (Cloud)      │   Ollama (Lokal)         │
├──────────────────┼───────────────────────┼──────────────────────────┤
│ Model            │ gemini-2.5-flash      │ llama3.1                 │
│ Kecepatan        │ Sangat cepat          │ Tergantung hardware      │
│ Biaya            │ Gratis (quota)        │ Gratis 100%              │
│ Koneksi          │ Butuh internet        │ Offline                  │
│ RAM/GPU          │ Tidak membebani       │ Butuh ≥8GB RAM           │
│ Privasi          │ Data via cloud        │ Data tetap lokal         │
│ Routing          │ litellm → Google API  │ litellm → localhost      │
└──────────────────┴───────────────────────┴──────────────────────────┘
```

---

## 🌐 Mekanisme REST API

FastAPI menyediakan beberapa endpoint:

| Method | Endpoint | Fungsi | Response |
|--------|----------|--------|----------|
| `GET` | `/` | Serve halaman dashboard (HTML) | HTML |
| `POST` | `/api/chat` | Kirim pertanyaan ke AI Agent | `{ status, response }` |
| `GET` | `/api/dashboard/stats` | Statistik ringkas (total item, low stock, total tx) | `{ total_items, low_stock_items, total_transactions }` |
| `GET` | `/api/stock/low` | Daftar barang stok menipis | `[{ item_number, product_name, soh, ... }]` |
| `GET` | `/api/transactions/recent` | 10 transaksi keluar terbaru | `[{ tanggal, product_name, qty_out, ... }]` |
| `GET` | `/api/items` | Daftar semua item + jumlah transaksi | `[{ item_number, product_name, tx_count }]` |
| `GET` | `/api/forecast/{item}` | Data forecast Prophet untuk charting | `{ dates[], actual[], predicted[] }` |
| `GET` | `/api/insights` | Insight katalog-wide (restock, tren, forecast total) | `{ status, restock_alerts[], trending_up[], trending_down[] }` |
| `GET` | `/api/purchase-orders/draft` | Draft rekomendasi PO untuk item yang butuh restock | `{ status, total_estimated_cost, items[] }` |
| `GET` | `/api/pricing/insights` | Item termahal & nilai stok terbesar | `{ status, total_stock_value, most_expensive_items[] }` |
| `POST` | `/api/reports/generate` | Antrikan job pembuatan CSV insight report | `{ status: "queued", task_id }` |
| `GET` | `/api/reports/status/{task_id}` | Cek status job report | `{ status, filename? }` |
| `GET` | `/api/reports/download/{filename}` | Download CSV report yang sudah jadi | file CSV |

Endpoint `/api/reports/*` sengaja dibikin async lewat Celery, bukan langsung diproses di request — supaya generate laporan (yang bisa nyentuh Prophet berkali-kali) gak nge-block thread FastAPI. Alur pemakaiannya: `POST /generate` → dapat `task_id` → poll `GET /status/{task_id}` sampai `status: "done"` → `GET /download/{filename}`.

### Notifikasi Restock Otomatis (Celery Beat)

Selain worker biasa, ada satu proses tambahan yang opsional: `celery -A celery_app beat`. Proses ini yang baca jadwal di `app/delivery/worker/celery_app.py` (`beat_schedule`) dan tiap jam 7 pagi ngirim task `send_restock_alert_task` ke antrian yang sama. Task itu manggil `notification_usecase.send_restock_alert()`, yang ngecek insight terbaru dan kalau ada item kritis, kirim ringkasannya ke Telegram lewat `TELEGRAM_ALERT_CHAT_ID`. Kalau env var itu kosong, task-nya tetap jalan tapi cuma di-skip (gak error).

---

## 🎨 Mekanisme Frontend

### Navigasi Single Page Application (SPA)

Dashboard menggunakan konsep **SPA sederhana** tanpa framework (Vanilla JS). Navigasi dilakukan dengan menyembunyikan/menampilkan `<section>` berdasarkan menu yang diklik:

```javascript
function setActiveView(navEl, viewEl) {
    // Sembunyikan semua section
    [viewDashboard, viewForecast, viewChat].forEach(v => v.classList.remove("active"));
    // Tampilkan section yang dipilih
    viewEl.classList.add("active");
}
```

### Tema Visual

- **Dark Mode** dengan warna dasar `#0f172a`
- **Glassmorphism** — efek kaca transparan menggunakan `backdrop-filter: blur()`
- **Radial Gradient** — background dengan gradien biru-hijau halus
- **Micro-animations** — hover effects dan fade-in transitions

### Forecasting Chart

Menggunakan **Chart.js** dengan 2 dataset:
- **Historical Actuals** (garis hijau solid) — data pemakaian nyata dari database
- **Prophet Forecast** (garis biru putus-putus) — prediksi AI 30 hari ke depan

---

## 📱 Mekanisme Telegram Bot

```python
# main.py menggunakan python-telegram-bot
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Handler untuk command /start
application.add_handler(CommandHandler("start", start))

# Handler untuk semua pesan teks → diteruskan ke CrewAI
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Mulai polling (long-polling ke Telegram API)
application.run_polling()
```

Telegram Bot menggunakan metode **long-polling** — artinya bot terus-menerus bertanya ke server Telegram: *"Ada pesan baru tidak?"*. Ketika ada pesan masuk, pesan tersebut diteruskan ke fungsi `process_user_query()` yang sama dengan yang digunakan oleh Web Dashboard.

---

## 🔮 Mekanisme Forecasting (Prophet)

**Facebook Prophet** adalah library forecasting open-source yang dirancang untuk data time-series bisnis. Cara kerjanya dalam project ini:

### Langkah-langkah:

1. **Ambil Data** — Query semua transaksi keluar untuk item tertentu dari database
2. **Agregasi** — Group by tanggal, jumlahkan `qty_out` per hari
3. **Formatting** — Ubah kolom menjadi format Prophet: `ds` (tanggal) dan `y` (nilai)
4. **Training** — Prophet mempelajari pola dari data historis
5. **Prediksi** — Buat dataframe 30 hari ke depan dan prediksi nilainya
6. **Sanitasi** — Clip nilai negatif menjadi 0, konversi NaN menjadi None
7. **Response** — Kirim data (dates, actual, predicted) ke frontend untuk di-render Chart.js

### Syarat Minimum

Prophet membutuhkan **minimal 5 data point** (transaksi) untuk bisa melakukan forecasting. Item dengan kurang dari 5 transaksi akan menampilkan pesan error. Di frontend, item yang memenuhi syarat ditandai dengan **⭐ (>5 tx)** pada dropdown.

---

## 📊 Ringkasan Masalah yang Diselesaikan

| Masalah | Solusi dalam Project |
|---------|---------------------|
| **Real-time stock data unavailable** | Tool `Check Stock` & `Get Low Stock` + Dashboard metrics + endpoint `/api/stock/low` |
| **Difficulty tracking sparepart usage** | Tool `View Outgoing Stock` & `Get Top Users` + tabel Recent Outgoing di Dashboard |
| **Inaccurate demand forecasting** | Facebook Prophet + Tool `Predict Monthly Needs` + halaman Forecasting dengan Chart.js |
| **Manual report generation** | AI Assistant (chatbot) via Web & Telegram yang menjawab pertanyaan secara otomatis |
