# AI Smart Scheduler API
<div align="center">
*API Jadwal Cerdas dengan Kecerdasan Buatan • Optimasi Produktivitas • RESTful Service*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Accuracy](https://img.shields.io/badge/Accuracy-96%25-brightgreen)](https://github.com/chelbapolandaa/Smart-CS-AI)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

AI Smart Scheduler API - RESTful API untuk perencanaan jadwal otomatis yang memahami bahasa natural Indonesia.

</div>

## Tentang Proyek
AI Smart Scheduler API adalah layanan RESTful berbasis FastAPI yang mengubah deskripsi aktivitas dalam bahasa Indonesia menjadi jadwal terstruktur dengan optimasi produktivitas.

## Keunggulan Utama
### 1. NLP Task Parsing
Masukkan input bebas seperti:
> besok urgent presentasi 2 jam, rapat team 1 jam, coding 2 jam

Sistem otomatis:
- memecah aktivitas
- mendeteksi durasi
- memberi prioritas (High/Medium/Low)
- menyusun jadwal harian

---

### 2. Mode Prioritas Tugas
Tiap task diberi prioritas:
- **High**
- **Medium**
- **Low**

Sistem mampu:
- Menggeser jadwal otomatis
- Menyelesaikan konflik jadwal
- Menempatkan aktivitas paling penting terlebih dahulu

---

### 3. Auto Time-Blocking (Greedy Algorithm)
Contoh input:
> Aku mau belajar AI 2 jam, olahraga 1 jam.

Output otomatis:
- 08:00 – 10:00 → belajar AI  
- 10:00 – 11:00 → olahraga

---

### 4. Embedding Cache Lokal
- Parsing bahasa alami jadi lebih cepat  
- Tidak memanggil model berulang-ulang

---

### 5. UI Mini (Streamlit / React)
Terdapat 3 input utama:
- Aktivitas
- Jam tersedia
- Preferensi (urgensi, durasi, fokus)

Output:
- Jadwal rapi
- Context panel
- Analytics produktivitas  
  (jam produktif, efisiensi, skor prioritas)

---

## Quick Demo
```
# Request
POST /api/schedule
{
  "text": "besok pagi meeting penting 2 jam, sore belajar AI 3 jam",
  "start_time": "09:00",
  "include_breaks": true
}

# Response
{
  "status": "success",
  "schedule_date": "2025-11-19",
  "total_productive_hours": 5.0,
  "total_break_hours": 1.25,
  "efficiency_score": 85.5,
  "schedule": [
    {
      "time": "09:00-11:00",
      "activity": "Meeting Penting",
      "duration": "2 jam",
      "type": "work"
    },
    {
      "time": "11:00-11:15", 
      "activity": "Break Pendek",
      "duration": "15 menit",
      "type": "break"
    }
  ]
}
```

## Installation
### Prasyarat
Python 3.8 atau lebih tinggi

pip package manager

Virtual environment (direkomendasikan)

### Langkah Instalasi
```
# 1. Clone repository
git clone https://github.com/your-username/ai-smart-scheduler-api.git
cd ai-smart-scheduler-api

# 2. Buat virtual environment
python -m venv scheduler_env

# 3. Aktivasi virtual environment
# Windows:
scheduler_env\Scripts\activate
# Linux/Mac:
source scheduler_env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Jalankan server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
```
http://localhost:8000/docs
```

### Alternative Docs:
```
http://localhost:8000/redoc
```

## API Endpoints
### POST /api/schedule
Generate jadwal dari teks natural language

**Request Body:**
```
{
  "text": "besok meeting 2 jam, coding 3 jam, olahraga 1 jam",
  "start_time": "09:00",
  "include_breaks": true,
  "break_duration": 15,
  "lunch_break": true,
  "lunch_duration": 60
}
```
**Response:**
```
{
  "status": "success",
  "schedule_date": "2025-11-19",
  "total_productive_hours": 6.0,
  "total_break_hours": 1.5,
  "efficiency_score": 87.2,
  "schedule": [
    {
      "time": "09:00-11:00",
      "activity": "Meeting",
      "duration": "2 jam",
      "type": "work",
      "priority": "medium"
    }
  ]
}
```
### GET /api/analytics
Dapatkan analytics dari jadwal yang digenerate

**Response:**
```
{
  "total_schedules_generated": 156,
  "average_productive_hours": 5.8,
  "average_efficiency": 82.4,
  "most_common_activities": [
    {"activity": "Meeting", "count": 89},
    {"activity": "Coding", "count": 76}
  ]
}
```

### POST /api/parse
Parse teks tanpa generate jadwal (hanya ekstraksi informasi)

**Request:**
```
{
  "text": "besok urgent presentasi 2 jam, rapat team 1 jam"
}
```

**Response:**
```
{
  "detected_activities": [
    {
      "activity": "presentasi",
      "duration_minutes": 120,
      "priority": "high",
      "keywords": ["urgent"]
    }
  ],
  "total_duration_minutes": 180,
  "date_reference": "besok"
}
```

## Contoh Penggunaan

### Menggunakan Python Requests
```
import requests
import json

API_URL = "http://localhost:8000/api/schedule"

# Contoh 1: Jadwal sederhana
payload = {
    "text": "besok meeting 2 jam, coding 3 jam, olahraga 1 jam",
    "include_breaks": True
}

response = requests.post(API_URL, json=payload)
schedule = response.json()
print(json.dumps(schedule, indent=2))
```

### Menggunakan cUrl
```
curl -X POST "http://localhost:8000/api/schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "besok pagi presentasi 2 jam, siang rapat 1 jam, sore belajar 3 jam",
    "include_breaks": true
  }'
```

### Menggunakan Javascript Fetch
```
const generateSchedule = async () => {
  const response = await fetch('http://localhost:8000/api/schedule', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: 'besok meeting 2 jam, coding 3 jam, olahraga 1 jam',
      include_breaks: true
    })
  });
  
  const schedule = await response.json();
  console.log(schedule);
};
```

## Tech Stack

### Backend Framework
**FastAPI: Modern, fast web framework**

**Pydantic: Data validation and settings management**

**Uvicorn: ASGI server**

### NLP & Processing
**SpaCy/Pattern: Natural language processing**

**Regex: Pattern matching untuk bahasa Indonesia**

**Dateutil: Date parsing and manipulation**

### Data Processing
**Pandas: Data manipulation untuk jadwal**

**NumPy: Perhitungan numerik**

## License
**Project ini dilisensikan di bawah MIT License.**

<div align="center">
⭐ Jangan lupa kasih star jika project ini bermanfaat!

Dibuat dengan ❤️ menggunakan FastAPI dan Python

"API cerdas untuk penjadwalan otomatis yang memahami bahasa manusia"

</div>
