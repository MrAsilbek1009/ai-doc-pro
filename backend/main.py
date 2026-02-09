from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import json
import re
import zipfile
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from docx import Document
from io import BytesIO

# Claude API
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

app = FastAPI(title="AI Doc Pro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory usage tracking (IP based)
# Railway da har deploy da reset bo'ladi, lekin oddiy limit uchun yetarli
usage_store = {}

def get_claude_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or not CLAUDE_AVAILABLE:
        return None
    return anthropic.Anthropic(api_key=api_key)

class ExcelRequest(BaseModel):
    prompt: str

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def check_daily_limit(ip: str) -> dict:
    """Kunlik limitni tekshirish"""
    from datetime import date
    today = str(date.today())
    
    key = f"{ip}:{today}"
    count = usage_store.get(key, 0)
    limit = 5
    
    return {
        "allowed": count < limit,
        "remaining": max(0, limit - count),
        "used": count,
        "limit": limit
    }

def record_usage(ip: str):
    """Foydalanishni qayd qilish"""
    from datetime import date
    today = str(date.today())
    
    key = f"{ip}:{today}"
    usage_store[key] = usage_store.get(key, 0) + 1

# ============ ENDPOINTS ============

@app.get("/")
async def root():
    return {
        "message": "AI Doc Pro API ishlamoqda!",
        "version": "2.0",
        "ai_enabled": CLAUDE_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY"))
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/check-limit")
async def check_limit(request: Request):
    """Limitni tekshirish"""
    ip = get_client_ip(request)
    return check_daily_limit(ip)

# ============ EXCEL ============

async def generate_excel_with_ai(prompt: str) -> dict:
    client = get_claude_client()
    
    if not client:
        return generate_excel_fallback(prompt)
    
    system_prompt = """Sen Excel jadval yaratuvchi AI assistantsan. JSON formatda jadval yarat.

FAQAT JSON QAYTAR:
{
    "title": "Fayl_nomi",
    "sheets": [{
        "name": "Varaq",
        "headers": ["A", "B", "C"],
        "data": [["1", "2", "=A2+B2"]]
    }]
}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": f"Excel jadval yarat: {prompt}"}],
            system=system_prompt
        )
        
        response_text = message.content[0].text.strip()
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"AI error: {e}")
    
    return generate_excel_fallback(prompt)

def generate_excel_fallback(prompt: str) -> dict:
    prompt_lower = prompt.lower()
    
    if any(w in prompt_lower for w in ["moliya", "hisobot", "kirim", "chiqim", "daromad"]):
        return {
            "title": "Oylik_Moliyaviy_Hisobot",
            "sheets": [{
                "name": "Hisobot",
                "headers": ["№", "Sana", "Tavsif", "Kirim", "Chiqim", "Balans"],
                "data": [
                    [1, "01.01.2025", "Boshlang'ich balans", 10000000, 0, "=D2-E2"],
                    [2, "05.01.2025", "Sotuvdan tushum", 5000000, 0, "=F2+D3-E3"],
                    [3, "10.01.2025", "Ijara to'lovi", 0, 2000000, "=F3+D4-E4"],
                    [4, "15.01.2025", "Maosh", 0, 3000000, "=F4+D5-E5"],
                    ["", "", "JAMI:", "=SUM(D2:D5)", "=SUM(E2:E5)", "=D6-E6"]
                ]
            }]
        }
    elif any(w in prompt_lower for w in ["xodim", "ishchi", "hodim", "maosh"]):
        return {
            "title": "IT_Kompaniya_Xodimlari",
            "sheets": [{
                "name": "Xodimlar",
                "headers": ["№", "F.I.O", "Lavozim", "Bo'lim", "Maosh"],
                "data": [
                    [1, "Karimov Jasur", "Senior Developer", "IT", 15000000],
                    [2, "Tosheva Madina", "HR Manager", "HR", 10000000],
                    [3, "Rahimov Bobur", "Designer", "Design", 8000000],
                    ["", "", "", "JAMI:", "=SUM(E2:E4)"]
                ]
            }]
        }
    else:
        return {
            "title": "Jadval",
            "sheets": [{
                "name": "Ma'lumotlar",
                "headers": ["№", "Nomi", "Miqdori", "Narxi", "Jami"],
                "data": [
                    [1, "Mahsulot A", 10, 50000, "=C2*D2"],
                    [2, "Mahsulot B", 20, 30000, "=C3*D3"],
                    ["", "", "", "JAMI:", "=SUM(E2:E3)"]
                ]
            }]
        }

def create_styled_excel(structure: dict) -> str:
    wb = Workbook()
    
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    
    for sheet_idx, sheet_data in enumerate(structure.get("sheets", [])):
        ws = wb.active if sheet_idx == 0 else wb.create_sheet()
        ws.title = sheet_data.get("name", "Sheet1")[:31]
        
        headers = sheet_data.get("headers", [])
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        
        for row_idx, row_data in enumerate(sheet_data.get("data", []), 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center")
        
        for col_idx in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 18
    
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, f"{structure.get('title', 'document')}.xlsx")
    wb.save(filepath)
    return filepath

@app.post("/api/excel/preview")
async def excel_preview(request: Request, data: ExcelRequest):
    try:
        # Limit tekshirish
        ip = get_client_ip(request)
        limit_info = check_daily_limit(ip)
        
        if not limit_info["allowed"]:
            raise HTTPException(status_code=429, detail="Kunlik limit tugadi")
        
        structure = await generate_excel_with_ai(data.prompt)
        return {
            "success": True,
            "title": structure.get("title"),
            "sheets": structure.get("sheets"),
            "remaining": limit_info["remaining"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/excel/generate")
async def excel_generate(request: Request, data: ExcelRequest):
    try:
        # Limit tekshirish
        ip = get_client_ip(request)
        limit_info = check_daily_limit(ip)
        
        if not limit_info["allowed"]:
            raise HTTPException(status_code=429, detail="Kunlik limit tugadi")
        
        # Foydalanishni qayd qilish
        record_usage(ip)
        
        structure = await generate_excel_with_ai(data.prompt)
        filepath = create_styled_excel(structure)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{structure.get('title', 'document')}.xlsx"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ AUTO-FILL ============

def extract_text_from_docx(content: bytes) -> str:
    doc = Document(BytesIO(content))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text + " "
            text += "\n"
    return text

async def get_replacements_from_ai(text: str, instruction: str) -> list:
    client = get_claude_client()
    
    if not client:
        return []
    
    system_prompt = """Sen hujjat tahrirlovchi AI san.

VAZIFA: Ko'rsatma asosida BARCHA o'zgartirilishi kerak joylarni top.

FAQAT JSON QAYTAR:
{
    "replacements": [
        {"old": "eski matn", "new": "yangi matn"}
    ]
}

MUHIM: Bir xil matn bir necha joyda bo'lishi mumkin - BARCHASINI top!"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": f"Hujjat:\n{text[:8000]}\n\nKo'rsatma:\n{instruction}\n\nJSON:"
            }],
            system=system_prompt
        )
        
        response_text = message.content[0].text.strip()
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("replacements", [])
    except Exception as e:
        print(f"AI error: {e}")
    
    return []

def apply_replacements_to_docx(content: bytes, replacements: list) -> bytes:
    doc = Document(BytesIO(content))
    
    def replace_in_paragraph(paragraph, old_text, new_text):
        if old_text in paragraph.text:
            for run in paragraph.runs:
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)
                    return True
            if old_text in paragraph.text:
                full_text = paragraph.text.replace(old_text, new_text)
                if paragraph.runs:
                    paragraph.runs[0].text = full_text
                    for run in paragraph.runs[1:]:
                        run.text = ""
                    return True
        return False
    
    for repl in replacements:
        old_text = repl.get("old", "")
        new_text = repl.get("new", "") or ""
        if not old_text:
            continue
        
        for para in doc.paragraphs:
            replace_in_paragraph(para, old_text, new_text)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        replace_in_paragraph(para, old_text, new_text)
        
        for section in doc.sections:
            if section.header:
                for para in section.header.paragraphs:
                    replace_in_paragraph(para, old_text, new_text)
            if section.footer:
                for para in section.footer.paragraphs:
                    replace_in_paragraph(para, old_text, new_text)
    
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output.read()

@app.post("/api/autofill/process")
async def process_autofill(
    request: Request,
    files: List[UploadFile] = File(...),
    instruction: str = Form(...)
):
    try:
        if not instruction.strip():
            raise HTTPException(status_code=400, detail="Ko'rsatma kiriting")
        
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="Fayl yuklang")
        
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maksimum 10 ta fayl")
        
        # Limit tekshirish
        ip = get_client_ip(request)
        limit_info = check_daily_limit(ip)
        
        if not limit_info["allowed"]:
            raise HTTPException(status_code=429, detail="Kunlik limit tugadi")
        
        # Foydalanishni qayd qilish
        record_usage(ip)
        
        processed_files = []
        
        for file in files:
            if not file.filename.lower().endswith('.docx'):
                raise HTTPException(status_code=400, detail=f"Faqat .docx qabul qilinadi: {file.filename}")
            
            content = await file.read()
            text = extract_text_from_docx(content)
            
            if not text.strip():
                continue
            
            replacements = await get_replacements_from_ai(text, instruction)
            
            if replacements:
                modified_content = apply_replacements_to_docx(content, replacements)
            else:
                modified_content = content
            
            processed_files.append({
                "filename": f"tahrirlangan_{file.filename}",
                "content": modified_content
            })
        
        if len(processed_files) == 0:
            raise HTTPException(status_code=400, detail="Fayllar qayta ishlanmadi")
        
        if len(processed_files) == 1:
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, processed_files[0]["filename"])
            with open(output_path, 'wb') as f:
                f.write(processed_files[0]["content"])
            
            return FileResponse(
                output_path,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=processed_files[0]["filename"]
            )
        
        # Ko'p fayl - ZIP
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "tahrirlangan_hujjatlar.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for pf in processed_files:
                zf.writestr(pf["filename"], pf["content"])
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="tahrirlangan_hujjatlar.zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ TEMPLATES (oddiy) ============

# Tayyor shablonlar
DEFAULT_TEMPLATES = [
    {"id": "1", "name": "Shartnoma", "category": "contract", "description": "Umumiy shartnoma shabloni"},
    {"id": "2", "name": "Ishonchnoma", "category": "legal", "description": "Avtomobil uchun ishonchnoma"},
    {"id": "3", "name": "Ariza", "category": "application", "description": "Umumiy ariza shabloni"},
]

@app.get("/api/templates")
async def get_templates():
    return {"templates": DEFAULT_TEMPLATES}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
