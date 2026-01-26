# AI Doc Pro 🚀

Professional hujjatlar yaratish platformasi - React + FastAPI

![AI Doc Pro](https://img.shields.io/badge/AI%20Doc%20Pro-v1.0-blue)
![React](https://img.shields.io/badge/React-18.2-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)

## 📋 Xususiyatlar

### ✅ Ishlaydi
- **Excel yaratish** - AI yordamida professional Excel fayllar
  - Moliyaviy prognozlar
  - Byudjet rejalari
  - Formulalar va formatlar
  
- **Auto-Fill** - Hujjatlarni avtomatik to'ldirish
  - PDF, Word, TXT formatlarini qo'llab-quvvatlash
  - Sanalarni avtomatik almashtirish
  - F.I.O, passport va boshqa ma'lumotlarni topish

### 🔜 Tez kunda
- Doc yaratish
- PDF yaratish
- Slaydlar (Prezentatsiyalar)
- Chat interfeys

## 🛠 O'rnatish

### Backend (Python)

```bash
cd backend

# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Serverni ishga tushirish
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)

```bash
cd frontend

# Kutubxonalarni o'rnatish
npm install

# Development serverni ishga tushirish
npm run dev
```

## 📁 Loyiha Strukturasi

```
ai-doc-pro/
├── backend/
│   ├── main.py          # FastAPI asosiy fayl
│   └── requirements.txt # Python kutubxonalari
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Asosiy React komponent
│   │   ├── main.jsx     # Entry point
│   │   └── index.css    # Stillar
│   │
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── README.md
```

## 🔌 API Endpoints

### Excel

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/api/excel/generate` | Excel fayl yaratish |
| POST | `/api/excel/preview` | Strukturani oldindan ko'rish |

### Auto-Fill

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/api/autofill/analyze` | Hujjatni tahlil qilish |
| POST | `/api/autofill/apply` | O'zgarishlarni qo'llash |

## 💡 Foydalanish

### Excel yaratish

1. "Excel" tabini tanlang
2. Hujjat tavsifini kiriting:
   - "12 oylik moliyaviy prognoz yarating"
   - "Kafe uchun byudjet rejasi"
3. "Yaratish" tugmasini bosing
4. Fayl avtomatik yuklab olinadi

### Auto-Fill

1. "Auto-Fill" tabini tanlang
2. PDF, Word yoki TXT faylni yuklang
3. Ko'rsatma kiriting:
   - "Sanalarni bugungi kunga o'zgartir"
   - "Ismni Alisher ga o'zgartir"
4. "Tahlil qilish" → "Tasdiqlash"

## 🎨 Texnologiyalar

**Frontend:**
- React 18
- Tailwind CSS
- Framer Motion
- Lucide Icons
- Vite

**Backend:**
- FastAPI
- OpenPyXL (Excel)
- python-docx (Word)
- PyMuPDF (PDF)

## 📝 License

MIT License

## 👨‍💻 Muallif

AI Doc Pro Team
