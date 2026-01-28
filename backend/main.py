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

# PDF to Word uchun
try:
    from pdf2docx import Converter
    PDF2DOCX_AVAILABLE = True
except ImportError:
    PDF2DOCX_AVAILABLE = False

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
        "pdf_supported": PDF_SUPPORTED,
        "pdf2docx_available": PDF2DOCX_AVAILABLE
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

async def get_replacements_from_ai(text: str, instruction: str) -> list:
    """AI dan almashtirish ro'yxatini olish - KUCHAYTIRILGAN"""
    client = get_claude_client()
    
    if not client:
        raise HTTPException(status_code=400, detail="AI xizmati mavjud emas")
    
    system_prompt = """Sen hujjat tahrirlovchi AI assistantsan.

VAZIFANG:
1. Hujjat matnini DIQQAT BILAN o'qi
2. Ko'rsatma asosida BARCHA almashtirilishi kerak bo'lgan joylarni top
3. JSON formatda almashtirish ro'yxatini qaytar

MUHIM QOIDALAR:
1. Hujjatda bir xil ma'lumot BIR NECHA MARTA takrorlanishi mumkin - BARCHASINI top!
2. Masalan: shartnoma raqami 5 joyda bo'lishi mumkin - 5 tasini ham qo'sh
3. Masalan: mijoz ismi 10 joyda bo'lishi mumkin - 10 tasini ham qo'sh
4. Masalan: sana 20 joyda bo'lishi mumkin - 20 tasini ham qo'sh
5. "old" maydoni AYNAN hujjatdagi matn bo'lishi kerak
6. Hatto bir xil matn bo'lsa ham, har birini alohida qo'sh

JSON formati:
{
    "replacements": [
        {"old": "eski matn 1", "new": "yangi matn 1"},
        {"old": "eski matn 2", "new": "yangi matn 2"},
        {"old": "eski matn 3", "new": "yangi matn 3"}
    ]
}

MISOLLAR:
- Agar "shartnoma raqamini 01-25/199B ga o'zgartir" deyilsa:
  Hujjatdagi "№ 01-24/123" ni toping va {"old": "№ 01-24/123", "new": "№ 01-25/199B"} qo'shing
  
- Agar "mijoz ismini Karimov ga o'zgartir" deyilsa:
  Hujjatdagi BARCHA eski ismlarni toping va har biri uchun alohida {"old": "...", "new": "Karimov"} qo'shing

- Agar "sanalarni bugungi kunga o'zgartir" deyilsa:
  Hujjatdagi BARCHA sanalarni toping (19.12.2024, 20.12.2024 va h.k.) va har biri uchun alohida replacement qo'shing

FAQAT JSON QAYTAR! Boshqa hech qanday matn yo'q!"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"""Quyidagi hujjatni DIQQAT BILAN tahlil qil va BARCHA almashtirilishi kerak bo'lgan joylarni top:

=== HUJJAT MATNI ===
{text}
=== HUJJAT TUGADI ===

=== FOYDALANUVCHI KO'RSATMASI ===
{instruction}
=== KO'RSATMA TUGADI ===

MUHIM: Hujjatda bir xil ma'lumot bir necha marta takrorlanishi mumkin. BARCHASINI top va ro'yxatga qo'sh!

JSON formatda BARCHA almashtirishlar ro'yxatini qaytar:"""
                }
            ],
            system=system_prompt
        )
        
        response_text = message.content[0].text.strip()
        
        # JSON ni ajratib olish
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            data = json.loads(json_match.group())
            replacements = data.get("replacements", [])
            print(f"AI {len(replacements)} ta almashtirish topdi")
            return replacements
        
        return []
        
    except Exception as e:
        print(f"AI xatolik: {e}")
        raise HTTPException(status_code=500, detail=f"AI xatolik: {str(e)}")

def apply_replacements_to_docx(content: bytes, replacements: list) -> str:
    """Word hujjatga almashtirishlarni qo'llash - FORMATLASHNI SAQLAGAN HOLDA"""
    doc = Document(BytesIO(content))
    replacement_count = 0
    
    def replace_in_paragraph(paragraph, old_text, new_text):
        """Paragraf ichida matnni almashtirish, formatlashni saqlash"""
        nonlocal replacement_count
        if old_text in paragraph.text:
            # Har bir run ni tekshirish
            for run in paragraph.runs:
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)
                    replacement_count += 1
                    return True
            
            # Murakkab holat - bir nechta run orasida bo'lingan
            full_text = paragraph.text
            if old_text in full_text:
                new_full_text = full_text.replace(old_text, new_text)
                if paragraph.runs:
                    first_run = paragraph.runs[0]
                    first_run.text = new_full_text
                    for run in paragraph.runs[1:]:
                        run.text = ""
                    replacement_count += 1
                    return True
        return False
    
    # Har bir almashtirish uchun
    for repl in replacements:
        old_text = repl.get("old", "")
        new_text = repl.get("new", "")
        
        if not old_text:
            continue
        if new_text is None:
            new_text = ""
        
        # Paragraflarda almashtirish
        for para in doc.paragraphs:
            replace_in_paragraph(para, old_text, new_text)
        
        # Jadvallarda almashtirish
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        replace_in_paragraph(para, old_text, new_text)
        
        # Header va Footer larda
        for section in doc.sections:
            if section.header:
                for para in section.header.paragraphs:
                    replace_in_paragraph(para, old_text, new_text)
            if section.footer:
                for para in section.footer.paragraphs:
                    replace_in_paragraph(para, old_text, new_text)
    
    print(f"Jami {replacement_count} ta almashtirish bajarildi")
    
    # Saqlash
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "tahrirlangan_hujjat.docx")
    doc.save(output_path)
    
    return output_path

def convert_pdf_to_docx(content: bytes) -> str:
    """PDF ni Word ga convert qilish - FORMATLASHNI SAQLAGAN HOLDA"""
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "input.pdf")
    docx_path = os.path.join(temp_dir, "converted.docx")
    
    # PDF ni saqlash
    with open(pdf_path, 'wb') as f:
        f.write(content)
    
    if PDF2DOCX_AVAILABLE:
        try:
            # pdf2docx bilan convert qilish - formatlashni yaxshi saqlaydi
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            return docx_path
        except Exception as e:
            print(f"pdf2docx xatolik: {e}")
    
    # Fallback - oddiy matn bilan
    if PDF_SUPPORTED:
        pdf_reader = PdfReader(BytesIO(content))
        doc = Document()
        
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                for line in text.split('\n'):
                    if line.strip():
                        doc.add_paragraph(line)
        
        doc.save(docx_path)
        return docx_path
    
    raise HTTPException(status_code=400, detail="PDF convert qilib bo'lmadi")

def apply_replacements_to_txt(content: bytes, replacements: list) -> str:
    """TXT faylga almashtirishlarni qo'llash"""
    text = content.decode('utf-8', errors='ignore')
    
    for repl in replacements:
        old_text = repl.get("old", "")
        new_text = repl.get("new", "")
        if old_text and new_text:
            text = text.replace(old_text, new_text)
    
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "tahrirlangan_hujjat.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return output_path

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
        original_filename = file.filename
        
        # PDF bo'lsa, avval Word ga convert qilamiz
        if file_ext == 'pdf':
            docx_path = convert_pdf_to_docx(content)
            with open(docx_path, 'rb') as f:
                content = f.read()
            file_ext = 'docx'
            original_filename = original_filename.replace('.pdf', '.docx')
        
        # Matnni ajratib olish (AI uchun)
        original_text = extract_text_from_file(content, file_ext)
        
        if not original_text.strip():
            raise HTTPException(status_code=400, detail="Fayl bo'sh yoki matn topilmadi")
        
        # AI dan almashtirish ro'yxatini olish
        replacements = await get_replacements_from_ai(original_text, instruction)
        
        if not replacements:
            raise HTTPException(status_code=400, detail="O'zgartirish kerak bo'lgan joylar topilmadi")
        
        # Fayl formatiga qarab almashtirishni qo'llash
        if file_ext == 'docx':
            output_path = apply_replacements_to_docx(content, replacements)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"tahrirlangan_{original_filename}"
            
        else:  # txt
            output_path = apply_replacements_to_txt(content, replacements)
            media_type = "text/plain"
            filename = f"tahrirlangan_{original_filename}"
        
        return FileResponse(
            output_path,
            media_type=media_type,
            filename=filename
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
