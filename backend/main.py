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
from docx.shared import Pt
from io import BytesIO

# PDF uchun
try:
    from pypdf import PdfReader
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

# PDF yaratish uchun
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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
    return {"status": "healthy"}

# ============ AI EXCEL GENERATOR ============

async def generate_excel_with_ai(prompt: str) -> dict:
    """Claude AI yordamida Excel strukturasini yaratish"""
    client = get_claude_client()
    
    if not client:
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
                    ["", "", "JAMI:", "=SUM(D2:D4)", "=SUM(E2:E4)", "=D5-E5"],
                ]
            }]
        }
    
    elif "xodim" in prompt_lower or "ishchi" in prompt_lower:
        return {
            "title": "Xodimlar",
            "sheets": [{
                "name": "Royxat",
                "headers": ["№", "F.I.O", "Lavozim", "Telefon", "Ish haqi"],
                "data": [
                    [1, "Karimov Anvar", "Direktor", "+998901234567", 15000000],
                    [2, "Tosheva Madina", "Buxgalter", "+998901234568", 8000000],
                    ["", "", "", "JAMI:", "=SUM(E2:E3)"],
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
                    ["", "", "", "JAMI:", "=SUM(E2:E3)"],
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
            "sheets": structure.get("sheets", [])
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
                text += "\n"
                    
    elif file_ext == 'txt':
        text = content.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(status_code=400, detail=f"Qo'llab-quvvatlanmaydigan format: {file_ext}")
    
    return text

async def process_document_with_ai(text: str, instruction: str) -> str:
    """AI yordamida hujjatni ko'rsatma asosida o'zgartirish"""
    client = get_claude_client()
    
    if not client:
        raise HTTPException(status_code=400, detail="AI xizmati mavjud emas")
    
    system_prompt = """Sen professional hujjat tahrir qiluvchi AI assistantsan. 

VAZIFANG:
1. Berilgan hujjat matnini diqqat bilan o'qi
2. Foydalanuvchi ko'rsatmasi asosida BARCHA kerakli joylarni toping va o'zgartiring
3. FAQAT yangilangan to'liq hujjat matnini qaytar
4. Hech qanday izoh, tushuntirish, yoki "Mana tahrirlangan hujjat" kabi so'zlar qo'shma
5. Asl hujjat strukturasini va formatlashni saqlang

MUHIM QOIDALAR:
- Agar shartnoma raqamini o'zgartirish kerak bo'lsa - BARCHA joylarda o'zgartiring
- Agar sanalarni o'zgartirish kerak bo'lsa - BARCHA sanalarni o'zgartiring
- Agar mijoz ma'lumotlarini o'zgartirish kerak bo'lsa - BARCHA joylarda o'zgartiring
- Agar avtomobil ma'lumotlarini o'zgartirish kerak bo'lsa - BARCHA joylarda o'zgartiring

FAQAT yangilangan hujjat matnini qaytar!"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Quyidagi hujjatni ko'rsatma asosida tahrirlang:

=== HUJJAT ===
{text}
=== HUJJAT TUGADI ===

=== KO'RSATMA ===
{instruction}
=== KO'RSATMA TUGADI ===

Tahrirlangan hujjatni to'liq qaytar:"""
                }
            ],
            system=system_prompt
        )
        
        return message.content[0].text.strip()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI xatolik: {str(e)}")

def create_word_document(text: str, original_filename: str) -> str:
    """Matndan Word hujjat yaratish"""
    doc = Document()
    
    # Matnni paragraflarga bo'lish
    paragraphs = text.split('\n')
    
    for para_text in paragraphs:
        if para_text.strip():
            p = doc.add_paragraph(para_text)
            for run in p.runs:
                run.font.size = Pt(11)
                run.font.name = 'Times New Roman'
        else:
            doc.add_paragraph()
    
    temp_dir = tempfile.mkdtemp()
    output_filename = f"tahrirlangan_{original_filename}"
    if not output_filename.endswith('.docx'):
        output_filename = output_filename.rsplit('.', 1)[0] + '.docx'
    output_path = os.path.join(temp_dir, output_filename)
    doc.save(output_path)
    
    return output_path

def create_pdf_document(text: str, original_filename: str) -> str:
    """Matndan PDF hujjat yaratish"""
    temp_dir = tempfile.mkdtemp()
    output_filename = f"tahrirlangan_{original_filename}"
    if not output_filename.endswith('.pdf'):
        output_filename = output_filename.rsplit('.', 1)[0] + '.pdf'
    output_path = os.path.join(temp_dir, output_filename)
    
    if not REPORTLAB_AVAILABLE:
        # Reportlab yo'q bo'lsa, DOCX sifatida saqlash
        return create_word_document(text, original_filename.replace('.pdf', '.docx'))
    
    try:
        # PDF yaratish
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Shriftni ro'yxatdan o'tkazish
        font_registered = False
        font_name = "Helvetica"
        
        # DejaVu shriftini topishga harakat qilish
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                    font_name = "DejaVuSans"
                    font_registered = True
                    break
                except:
                    pass
        
        c.setFont(font_name, 10)
        
        # Matnni qatorlarga bo'lish
        lines = text.split('\n')
        y_position = height - 50
        line_height = 14
        margin_left = 50
        
        for line in lines:
            if y_position < 50:
                c.showPage()
                c.setFont(font_name, 10)
                y_position = height - 50
            
            # Uzun qatorlarni kesish
            while len(line) > 85:
                part = line[:85]
                # So'z orasida kesish
                last_space = part.rfind(' ')
                if last_space > 50:
                    part = line[:last_space]
                    line = line[last_space+1:]
                else:
                    line = line[85:]
                
                try:
                    c.drawString(margin_left, y_position, part)
                except:
                    safe_part = part.encode('latin-1', 'replace').decode('latin-1')
                    c.drawString(margin_left, y_position, safe_part)
                y_position -= line_height
                
                if y_position < 50:
                    c.showPage()
                    c.setFont(font_name, 10)
                    y_position = height - 50
            
            if line:
                try:
                    c.drawString(margin_left, y_position, line)
                except:
                    safe_line = line.encode('latin-1', 'replace').decode('latin-1')
                    c.drawString(margin_left, y_position, safe_line)
            y_position -= line_height
        
        c.save()
        return output_path
        
    except Exception as e:
        print(f"PDF yaratishda xatolik: {e}")
        # Xatolik bo'lsa DOCX sifatida qaytarish
        return create_word_document(text, original_filename.replace('.pdf', '.docx'))

@app.post("/api/autofill/process")
async def process_autofill(
    file: UploadFile = File(...),
    instruction: str = Form(...)
):
    """Hujjatni AI bilan tahlil qilish va o'zgartirish"""
    try:
        if not instruction.strip():
            raise HTTPException(status_code=400, detail="Ko'rsatma kiriting")
        
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        # Matnni ajratib olish
        original_text = extract_text_from_file(content, file_ext)
        
        if not original_text.strip():
            raise HTTPException(status_code=400, detail="Fayl bo'sh yoki matn topilmadi")
        
        # AI bilan o'zgartirish
        modified_text = await process_document_with_ai(original_text, instruction)
        
        # Fayl formatiga qarab saqlash
        if file_ext == 'docx':
            output_path = create_word_document(modified_text, file.filename)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_ext == 'pdf':
            output_path = create_pdf_document(modified_text, file.filename)
            if output_path.endswith('.docx'):
                media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                media_type = "application/pdf"
        else:  # txt
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f"tahrirlangan_{file.filename}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_text)
            media_type = "text/plain"
        
        return FileResponse(
            output_path,
            media_type=media_type,
            filename=os.path.basename(output_path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server xatoligi: {str(e)}")

# Eski endpoint
@app.post("/api/autofill/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Hujjatni tahlil qilish (eski endpoint)"""
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        text = extract_text_from_file(content, file_ext)
        
        return {
            "success": True,
            "text": text[:3000],
            "file_type": file_ext
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
