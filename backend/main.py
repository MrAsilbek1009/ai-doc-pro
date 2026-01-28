from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import tempfile
import json
import re
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from docx import Document
from io import BytesIO

# PDF uchun
try:
    from pypdf import PdfReader
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

# Claude API uchun
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

app = FastAPI(title="AI Doc Pro API")

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Claude client
def get_claude_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or not CLAUDE_AVAILABLE:
        return None
    return anthropic.Anthropic(api_key=api_key)

# Pydantic models
class ExcelRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {
        "message": "AI Doc Pro API ishlamoqda!",
        "ai_enabled": CLAUDE_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY")),
        "pdf_supported": PDF_SUPPORTED
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_enabled": CLAUDE_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY")),
        "pdf_supported": PDF_SUPPORTED
    }

# ============ AI EXCEL GENERATOR ============

async def generate_excel_with_ai(prompt: str) -> dict:
    """Claude AI yordamida Excel strukturasini yaratish"""
    client = get_claude_client()
    
    if not client:
        # AI yo'q bo'lsa, oddiy rule-based
        return generate_excel_fallback(prompt)
    
    system_prompt = """Sen Excel jadval yaratuvchi AI assistantsan. Foydalanuvchi so'rovi asosida JSON formatda jadval strukturasini yarat.

MUHIM: Faqat JSON qaytar, boshqa hech narsa yo'q!

JSON formati:
{
    "title": "Fayl_nomi",
    "sheets": [{
        "name": "Varaq nomi",
        "headers": ["Ustun1", "Ustun2", "Ustun3"],
        "data": [
            ["qiymat1", "qiymat2", "qiymat3"],
            ["qiymat4", "qiymat5", "=A2+B2"]
        ]
    }]
}

Qoidalar:
1. Formulalar = bilan boshlanadi (masalan: =SUM(A1:A10), =A2*B2)
2. Sonlar raqam sifatida (10000, 500.5)
3. Matn qo'shtirnoqda ("matn")
4. Sanalar "01.01.2025" formatda
5. Har doim mantiqiy va to'liq ma'lumotlar bilan
6. O'zbek tilida"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"Quyidagi so'rov uchun Excel jadval yarat:\n\n{prompt}"
                }
            ],
            system=system_prompt
        )
        
        response_text = message.content[0].text.strip()
        
        # JSON ni ajratib olish
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            structure = json.loads(json_match.group())
            return structure
        else:
            raise ValueError("JSON topilmadi")
            
    except Exception as e:
        print(f"AI xatolik: {e}")
        return generate_excel_fallback(prompt)

def generate_excel_fallback(prompt: str) -> dict:
    """AI ishlamasa, oddiy rule-based generator"""
    prompt_lower = prompt.lower()
    
    if "moliya" in prompt_lower or "daromad" in prompt_lower or "kirim" in prompt_lower or "chiqim" in prompt_lower:
        return {
            "title": "Moliyaviy_Hisobot",
            "sheets": [{
                "name": "Hisobot",
                "headers": ["№", "Sana", "Tavsif", "Kirim", "Chiqim", "Balans"],
                "data": [
                    [1, "01.01.2025", "Boshlang'ich balans", 10000000, 0, "=D2-E2"],
                    [2, "05.01.2025", "Mahsulot sotish", 5000000, 0, "=F2+D3-E3"],
                    [3, "10.01.2025", "Ofis ijarasi", 0, 2000000, "=F3+D4-E4"],
                    [4, "15.01.2025", "Xizmat ko'rsatish", 3000000, 0, "=F4+D5-E5"],
                    [5, "20.01.2025", "Oylik maosh", 0, 4000000, "=F5+D6-E6"],
                    ["", "", "JAMI:", "=SUM(D2:D6)", "=SUM(E2:E6)", "=D7-E7"],
                ]
            }]
        }
    
    elif "byudjet" in prompt_lower or "reja" in prompt_lower or "budget" in prompt_lower:
        return {
            "title": "Byudjet_Rejasi",
            "sheets": [{
                "name": "Oylik Byudjet",
                "headers": ["№", "Kategoriya", "Rejalashtirilgan", "Haqiqiy", "Farq"],
                "data": [
                    [1, "Oziq-ovqat", 2000000, 1800000, "=C2-D2"],
                    [2, "Transport", 500000, 600000, "=C3-D3"],
                    [3, "Kommunal", 800000, 750000, "=C4-D4"],
                    [4, "Kiyim-kechak", 1000000, 1200000, "=C5-D5"],
                    [5, "Ko'ngilochar", 500000, 400000, "=C6-D6"],
                    ["", "JAMI:", "=SUM(C2:C6)", "=SUM(D2:D6)", "=C7-D7"],
                ]
            }]
        }
    
    elif "xodim" in prompt_lower or "ishchi" in prompt_lower or "hodim" in prompt_lower:
        return {
            "title": "Xodimlar_Royxati",
            "sheets": [{
                "name": "Xodimlar",
                "headers": ["№", "F.I.O", "Lavozim", "Bo'lim", "Telefon", "Ish haqi"],
                "data": [
                    [1, "Karimov Anvar", "Direktor", "Rahbariyat", "+998901234567", 15000000],
                    [2, "Tosheva Madina", "Buxgalter", "Moliya", "+998901234568", 8000000],
                    [3, "Rahimov Jasur", "Dasturchi", "IT", "+998901234569", 10000000],
                    [4, "Saidova Nilufar", "Menejer", "Sotuvlar", "+998901234570", 7000000],
                    ["", "", "", "", "JAMI:", "=SUM(F2:F5)"],
                ]
            }]
        }
    
    elif "jadval" in prompt_lower or "dars" in prompt_lower or "soat" in prompt_lower or "kundalik" in prompt_lower:
        return {
            "title": "Dars_Jadvali",
            "sheets": [{
                "name": "Jadval",
                "headers": ["№", "Kun", "Fan", "Soat", "Vaqt", "O'qituvchi"],
                "data": [
                    [1, "Dushanba", "Matematika", 2, "09:00-11:00", ""],
                    [2, "Dushanba", "Ingliz tili", 2, "11:00-13:00", ""],
                    [3, "Seshanba", "Fizika", 2, "09:00-11:00", ""],
                    [4, "Seshanba", "Informatika", 2, "11:00-13:00", ""],
                    [5, "Chorshanba", "Kimyo", 2, "09:00-11:00", ""],
                    ["", "", "JAMI:", "=SUM(D2:D6)", "", ""],
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
                    [1, "Element 1", 10, 50000, "=C2*D2"],
                    [2, "Element 2", 20, 30000, "=C3*D3"],
                    [3, "Element 3", 15, 40000, "=C4*D4"],
                    ["", "", "", "JAMI:", "=SUM(E2:E4)"],
                ]
            }]
        }

def create_styled_excel(structure: dict) -> str:
    """Excel fayl yaratish"""
    wb = Workbook()
    
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for sheet_idx, sheet_data in enumerate(structure.get("sheets", [])):
        if sheet_idx == 0:
            ws = wb.active
            ws.title = sheet_data.get("name", "Sheet1")[:31]
        else:
            ws = wb.create_sheet(title=sheet_data.get("name", f"Sheet{sheet_idx+1}")[:31])
        
        headers = sheet_data.get("headers", [])
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
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
async def excel_preview(request: ExcelRequest):
    """Excel preview"""
    try:
        structure = await generate_excel_with_ai(request.prompt)
        return {
            "success": True,
            "title": structure.get("title", "Hujjat"),
            "sheets": structure.get("sheets", []),
            "ai_generated": CLAUDE_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY"))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/excel/generate")
async def excel_generate(request: ExcelRequest):
    """Excel fayl yaratish"""
    try:
        structure = await generate_excel_with_ai(request.prompt)
        filepath = create_styled_excel(structure)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{structure.get('title', 'document')}.xlsx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ AI AUTO-FILL ============

def extract_text_from_file(content: bytes, file_ext: str) -> str:
    """Fayldan matn ajratib olish"""
    text = ""
    
    if file_ext == 'pdf':
        if not PDF_SUPPORTED:
            raise HTTPException(status_code=400, detail="PDF kutubxonasi o'rnatilmagan")
        pdf_reader = PdfReader(BytesIO(content))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
    elif file_ext == 'docx':
        doc = Document(BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                    
    elif file_ext == 'txt':
        text = content.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(status_code=400, detail=f"Qo'llab-quvvatlanmaydigan format: {file_ext}")
    
    return text

async def analyze_with_ai(text: str) -> list:
    """AI yordamida hujjatni tahlil qilish"""
    client = get_claude_client()
    
    # Avval oddiy regex bilan topamiz
    replacements = []
    seen = set()
    
    patterns = [
        (r'\[([^\]]+)\]', 'placeholder'),
        (r'\{([^\}]+)\}', 'variable'),
        (r'<([^>]+)>', 'field'),
        (r'_{3,}', 'blank'),
        (r'\.{3,}', 'dots'),
    ]
    
    for pattern, pattern_type in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            original = match.group(0)
            if original not in seen:
                seen.add(original)
                placeholder = match.group(1) if match.lastindex else original
                replacements.append({
                    "original": original,
                    "placeholder": placeholder,
                    "type": pattern_type,
                    "new_value": "",
                    "ai_suggestion": ""
                })
    
    # Agar AI mavjud bo'lsa, tavsiyalar qo'shamiz
    if client and replacements:
        try:
            placeholders_list = [r["placeholder"] for r in replacements[:15]]  # Max 15 ta
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Quyidagi hujjat matnidagi bo'sh joylar uchun namuna qiymatlar tavsiya qil.

Hujjat matni (qisqartirilgan):
{text[:1500]}

Bo'sh joylar: {placeholders_list}

Har bir joy uchun mantiqiy namuna qiymat ber. JSON formatda javob ber:
{{"suggestions": {{"placeholder1": "qiymat1", "placeholder2": "qiymat2"}}}}

Faqat JSON qaytar!"""
                    }
                ]
            )
            
            response_text = message.content[0].text.strip()
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                suggestions = json.loads(json_match.group()).get("suggestions", {})
                for r in replacements:
                    if r["placeholder"] in suggestions:
                        r["ai_suggestion"] = suggestions[r["placeholder"]]
                        
        except Exception as e:
            print(f"AI tavsiya xatolik: {e}")
    
    return replacements

@app.post("/api/autofill/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Hujjatni AI bilan tahlil qilish"""
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        text = extract_text_from_file(content, file_ext)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Fayl bo'sh yoki matn topilmadi")
        
        replacements = await analyze_with_ai(text)
        
        return {
            "success": True,
            "text": text[:3000],
            "replacements": replacements,
            "file_type": file_ext,
            "total_found": len(replacements),
            "ai_enabled": CLAUDE_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY"))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server xatoligi: {str(e)}")

@app.post("/api/autofill/apply")
async def apply_autofill(
    file: UploadFile = File(...),
    replacements: str = Form("")
):
    """O'zgarishlarni qo'llash"""
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        replacement_list = json.loads(replacements) if replacements else []
        
        if file_ext == 'docx':
            doc = Document(BytesIO(content))
            
            for para in doc.paragraphs:
                for repl in replacement_list:
                    if repl.get("original") in para.text and repl.get("new_value"):
                        para.text = para.text.replace(repl["original"], repl["new_value"])
            
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for repl in replacement_list:
                            if repl.get("original") in cell.text and repl.get("new_value"):
                                cell.text = cell.text.replace(repl["original"], repl["new_value"])
            
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f"filled_{file.filename}")
            doc.save(output_path)
            
            return FileResponse(
                output_path,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=f"filled_{file.filename}"
            )
        
        elif file_ext == 'txt':
            text = content.decode('utf-8', errors='ignore')
            
            for repl in replacement_list:
                if repl.get("original") and repl.get("new_value"):
                    text = text.replace(repl["original"], repl["new_value"])
            
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f"filled_{file.filename}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return FileResponse(
                output_path,
                media_type="text/plain",
                filename=f"filled_{file.filename}"
            )
        
        elif file_ext == 'pdf':
            # PDF -> TXT
            text = extract_text_from_file(content, 'pdf')
            
            for repl in replacement_list:
                if repl.get("original") and repl.get("new_value"):
                    text = text.replace(repl["original"], repl["new_value"])
            
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f"filled_{file.filename.replace('.pdf', '.txt')}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return FileResponse(
                output_path,
                media_type="text/plain",
                filename=f"filled_{file.filename.replace('.pdf', '.txt')}"
            )
        
        else:
            raise HTTPException(status_code=400, detail="Qo'llab-quvvatlanmaydigan format")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Noto'g'ri replacements formati")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server xatoligi: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
