"""
AI Doc Pro - FastAPI Backend
Excel va Auto-Fill funksiyalari
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from docx import Document
# import fitz  # PyMuPDF - disabled for Railway
from io import BytesIO
import json
import re
from datetime import datetime

app = FastAPI(title="AI Doc Pro API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================== MODELS ===================

class ExcelRequest(BaseModel):
    prompt: str
    include_charts: bool = False

class Replacement(BaseModel):
    old: str
    new: str
    type: str = "Matn"
    confidence: str = "high"

class AutoFillRequest(BaseModel):
    instruction: str
    text: str

class AutoFillApplyRequest(BaseModel):
    replacements: List[Replacement]

# =================== EXCEL GENERATOR ===================

def generate_excel_structure(prompt: str) -> dict:
    """
    Prompt asosida Excel strukturasini generatsiya qilish
    Bu yerda oddiy logika - real loyihada AI API ishlatiladi
    """
    prompt_lower = prompt.lower()
    
    # Moliyaviy prognoz
    if "moliyaviy" in prompt_lower or "financial" in prompt_lower or "prognoz" in prompt_lower:
        months = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", 
                  "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
        
        return {
            "title": "Moliyaviy_Prognoz_2025",
            "sheets": [{
                "name": "Prognoz",
                "headers": ["Kategoriya"] + months + ["Jami"],
                "data": [
                    ["DAROMADLAR", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["Asosiy sotuvlar", 15000000, 16500000, 18000000, 17500000, 19000000, 21000000, 
                     22000000, 20500000, 19500000, 21500000, 23000000, 25000000, "=SUM(B2:M2)"],
                    ["Qo'shimcha xizmatlar", 3000000, 3200000, 3500000, 3300000, 3800000, 4200000,
                     4500000, 4100000, 3900000, 4300000, 4600000, 5000000, "=SUM(B3:M3)"],
                    ["Jami daromad", "=B2+B3", "=C2+C3", "=D2+D3", "=E2+E3", "=F2+F3", "=G2+G3",
                     "=H2+H3", "=I2+I3", "=J2+J3", "=K2+K3", "=L2+L3", "=M2+M3", "=SUM(B4:M4)"],
                    ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["XARAJATLAR", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["Ish haqi", 8000000, 8000000, 8500000, 8500000, 8500000, 9000000,
                     9000000, 9000000, 9500000, 9500000, 10000000, 10000000, "=SUM(B7:M7)"],
                    ["Ijara", 3000000, 3000000, 3000000, 3000000, 3000000, 3000000,
                     3500000, 3500000, 3500000, 3500000, 3500000, 3500000, "=SUM(B8:M8)"],
                    ["Marketing", 1500000, 2000000, 2500000, 2000000, 2500000, 3000000,
                     3000000, 2500000, 2000000, 2500000, 3000000, 3500000, "=SUM(B9:M9)"],
                    ["Boshqa xarajatlar", 1000000, 1100000, 1200000, 1100000, 1300000, 1400000,
                     1500000, 1300000, 1200000, 1400000, 1500000, 1600000, "=SUM(B10:M10)"],
                    ["Jami xarajat", "=SUM(B7:B10)", "=SUM(C7:C10)", "=SUM(D7:D10)", "=SUM(E7:E10)",
                     "=SUM(F7:F10)", "=SUM(G7:G10)", "=SUM(H7:H10)", "=SUM(I7:I10)", "=SUM(J7:J10)",
                     "=SUM(K7:K10)", "=SUM(L7:L10)", "=SUM(M7:M10)", "=SUM(B11:M11)"],
                    ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["SOF FOYDA", "=B4-B11", "=C4-C11", "=D4-D11", "=E4-E11", "=F4-F11", "=G4-G11",
                     "=H4-H11", "=I4-I11", "=J4-J11", "=K4-K11", "=L4-L11", "=M4-M11", "=SUM(B13:M13)"]
                ]
            }]
        }
    
    # Kafe/restoran
    elif "kafe" in prompt_lower or "cafe" in prompt_lower or "restoran" in prompt_lower:
        months = ["Yan", "Fev", "Mar", "Apr", "May", "Iyn", "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"]
        
        return {
            "title": "Kafe_Moliyaviy_Prognoz",
            "sheets": [{
                "name": "Dashboard",
                "headers": ["Kategoriya"] + months + ["Yillik Jami"],
                "data": [
                    ["📊 DAROMADLAR", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["Kofe sotuvi", 8500000, 9000000, 9500000, 10000000, 11000000, 12000000,
                     12500000, 12000000, 11000000, 10500000, 9500000, 11000000, "=SUM(B2:M2)"],
                    ["Ovqat sotuvi", 6000000, 6500000, 7000000, 7500000, 8000000, 8500000,
                     9000000, 8500000, 8000000, 7500000, 7000000, 8000000, "=SUM(B3:M3)"],
                    ["Tovarlar", 2000000, 2200000, 2500000, 2800000, 3000000, 3200000,
                     3500000, 3200000, 3000000, 2800000, 2500000, 3000000, "=SUM(B4:M4)"],
                    ["Jami daromad", "=SUM(B2:B4)", "=SUM(C2:C4)", "=SUM(D2:D4)", "=SUM(E2:E4)",
                     "=SUM(F2:F4)", "=SUM(G2:G4)", "=SUM(H2:H4)", "=SUM(I2:I4)", "=SUM(J2:J4)",
                     "=SUM(K2:K4)", "=SUM(L2:L4)", "=SUM(M2:M4)", "=SUM(B5:M5)"],
                    ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["💰 XARAJATLAR", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["Ijara", 3000000, 3000000, 3000000, 3000000, 3000000, 3000000,
                     3000000, 3000000, 3000000, 3000000, 3000000, 3000000, "=SUM(B8:M8)"],
                    ["Ish haqi", 5000000, 5000000, 5500000, 5500000, 6000000, 6500000,
                     6500000, 6500000, 6000000, 5500000, 5500000, 6000000, "=SUM(B9:M9)"],
                    ["Materiallar", 4000000, 4300000, 4600000, 5000000, 5500000, 6000000,
                     6200000, 5800000, 5400000, 5000000, 4600000, 5200000, "=SUM(B10:M10)"],
                    ["Marketing", 500000, 600000, 700000, 800000, 900000, 1000000,
                     1000000, 900000, 800000, 700000, 600000, 800000, "=SUM(B11:M11)"],
                    ["Jami xarajat", "=SUM(B8:B11)", "=SUM(C8:C11)", "=SUM(D8:D11)", "=SUM(E8:E11)",
                     "=SUM(F8:F11)", "=SUM(G8:G11)", "=SUM(H8:H11)", "=SUM(I8:I11)", "=SUM(J8:J11)",
                     "=SUM(K8:K11)", "=SUM(L8:L11)", "=SUM(M8:M11)", "=SUM(B12:M12)"],
                    ["", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["✨ SOF FOYDA", "=B5-B12", "=C5-C12", "=D5-D12", "=E5-E12", "=F5-F12", "=G5-G12",
                     "=H5-H12", "=I5-I12", "=J5-J12", "=K5-K12", "=L5-L12", "=M5-M12", "=SUM(B14:M14)"],
                    ["Foyda %", "=B14/B5*100", "=C14/C5*100", "=D14/D5*100", "=E14/E5*100",
                     "=F14/F5*100", "=G14/G5*100", "=H14/H5*100", "=I14/I5*100", "=J14/J5*100",
                     "=K14/K5*100", "=L14/L5*100", "=M14/M5*100", "=AVERAGE(B15:M15)"]
                ]
            }]
        }
    
    # Byudjet
    elif "byudjet" in prompt_lower or "budget" in prompt_lower:
        return {
            "title": "Byudjet_Rejasi",
            "sheets": [{
                "name": "Byudjet",
                "headers": ["Kategoriya", "Rejalashtirilgan", "Haqiqiy", "Farq", "Foiz"],
                "data": [
                    ["DAROMADLAR", "", "", "", ""],
                    ["Asosiy ish haqi", 10000000, 10000000, "=C2-B2", "=D2/B2*100"],
                    ["Qo'shimcha daromad", 2000000, 2500000, "=C3-B3", "=D3/B3*100"],
                    ["Jami daromad", "=SUM(B2:B3)", "=SUM(C2:C3)", "=C4-B4", "=D4/B4*100"],
                    ["", "", "", "", ""],
                    ["XARAJATLAR", "", "", "", ""],
                    ["Uy-joy", 3000000, 3000000, "=C7-B7", "=D7/B7*100"],
                    ["Oziq-ovqat", 2000000, 2200000, "=C8-B8", "=D8/B8*100"],
                    ["Transport", 1000000, 1100000, "=C9-B9", "=D9/B9*100"],
                    ["Kommunal", 500000, 600000, "=C10-B10", "=D10/B10*100"],
                    ["Boshqa", 1000000, 1200000, "=C11-B11", "=D11/B11*100"],
                    ["Jami xarajat", "=SUM(B7:B11)", "=SUM(C7:C11)", "=C12-B12", "=D12/B12*100"],
                    ["", "", "", "", ""],
                    ["TEJAM", "=B4-B12", "=C4-C12", "=C14-B14", "=D14/B14*100"]
                ]
            }]
        }
    
    # Default - oddiy jadval
    else:
        return {
            "title": "Yangi_Hujjat",
            "sheets": [{
                "name": "Ma'lumotlar",
                "headers": ["№", "Nomi", "Miqdori", "Narxi", "Summasi"],
                "data": [
                    [1, "Mahsulot A", 100, 50000, "=C2*D2"],
                    [2, "Mahsulot B", 75, 75000, "=C3*D3"],
                    [3, "Mahsulot C", 50, 100000, "=C4*D4"],
                    [4, "Mahsulot D", 200, 25000, "=C5*D5"],
                    [5, "Mahsulot E", 150, 35000, "=C6*D6"],
                    ["", "", "", "JAMI:", "=SUM(E2:E6)"]
                ]
            }]
        }

def create_excel_file(structure: dict) -> bytes:
    """Excel faylini yaratish"""
    wb = Workbook()
    wb.remove(wb.active)
    
    # Ranglar
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    total_fill = PatternFill(start_color="D6DCE4", end_color="D6DCE4", fill_type="solid")
    profit_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    for sheet_data in structure.get('sheets', []):
        ws = wb.create_sheet(title=sheet_data['name'][:31])
        
        # Headers
        headers = sheet_data.get('headers', [])
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
        
        # Freeze panes
        ws.freeze_panes = 'B2'
        
        # Data
        for row_idx, row_data in enumerate(sheet_data.get('data', []), 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center' if col_idx > 1 else 'left', vertical='center')
                
                # Number formatting
                if isinstance(value, (int, float)) and value > 1000:
                    cell.number_format = '#,##0'
                
                # Highlight totals
                row_text = str(row_data[0]).lower() if row_data else ""
                if "jami" in row_text:
                    cell.fill = total_fill
                    cell.font = Font(bold=True)
                elif "foyda" in row_text or "profit" in row_text:
                    cell.fill = profit_fill
                    cell.font = Font(bold=True, color="006100")
        
        # Auto column width
        for col in ws.columns:
            max_length = 0
            column = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if cell.value:
                        cell_len = len(str(cell.value))
                        if cell_len > max_length:
                            max_length = cell_len
                except:
                    pass
            ws.column_dimensions[column].width = min(max(max_length + 3, 10), 25)
        
        # Row height
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 22
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

# =================== AUTO-FILL ===================

def analyze_text_for_replacements(text: str, instruction: str) -> List[dict]:
    """Matnni tahlil qilib, almashtirishlarni topish"""
    replacements = []
    instruction_lower = instruction.lower()
    
    # Sanalarni topish
    date_patterns = [
        r'\d{2}\.\d{2}\.\d{4}г?\.?',
        r'\d{2}/\d{2}/\d{4}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{4}-\d{2}-\d{2}',
    ]
    
    if "sana" in instruction_lower or "date" in instruction_lower or "bugun" in instruction_lower:
        today = datetime.now().strftime("%d.%m.%Y")
        
        # Yangi sanani aniqlash
        new_date = today
        date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', instruction)
        if date_match:
            new_date = date_match.group(1)
        
        for pattern in date_patterns:
            found_dates = re.findall(pattern, text)
            for old_date in set(found_dates):
                # g. va boshqa suffixlarni saqlash
                suffix = ""
                if old_date.endswith("г."):
                    suffix = "г."
                    new_val = new_date + suffix
                elif old_date.endswith("."):
                    suffix = "."
                    new_val = new_date + suffix
                else:
                    new_val = new_date
                
                replacements.append({
                    "old": old_date,
                    "new": new_val,
                    "type": "Sana",
                    "confidence": "high"
                })
    
    # Ismlarni topish (F.I.O)
    if "ism" in instruction_lower or "name" in instruction_lower:
        # Yangi ismni olish
        new_name_match = re.search(r'(?:ga|ni)\s+([A-ZА-ЯЁ][a-zа-яё]+(?:\s+[A-ZА-ЯЁ][a-zа-яё]+)*)', instruction)
        if new_name_match:
            new_name = new_name_match.group(1)
        else:
            new_name = "YANGI_ISM"
        
        # Kirill F.I.O
        cyrillic_names = re.findall(r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+ович|евич|ич', text)
        for name in set(cyrillic_names):
            replacements.append({
                "old": name,
                "new": new_name,
                "type": "F.I.O",
                "confidence": "high"
            })
    
    # Passport
    if "passport" in instruction_lower:
        new_passport_match = re.search(r'([A-Z]{2}\d{7})', instruction)
        new_passport = new_passport_match.group(1) if new_passport_match else "YANGI_PASSPORT"
        
        passport_pattern = r'[A-Z]{2}\d{7}'
        found_passports = re.findall(passport_pattern, text)
        for passport in set(found_passports):
            replacements.append({
                "old": passport,
                "new": new_passport,
                "type": "Passport",
                "confidence": "high"
            })
    
    # Telefon raqam
    if "telefon" in instruction_lower or "phone" in instruction_lower:
        phone_pattern = r'\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}|\d{2}\s?\d{3}\s?\d{2}\s?\d{2}'
        found_phones = re.findall(phone_pattern, text)
        for phone in set(found_phones):
            replacements.append({
                "old": phone,
                "new": "YANGI_TELEFON",
                "type": "Telefon",
                "confidence": "medium"
            })
    
    # Umumiy matn almashtirish
    # "X ni Y ga" formati
    general_match = re.search(r'"([^"]+)"\s*(?:ni|dan)\s*"([^"]+)"', instruction)
    if not general_match:
        general_match = re.search(r'([^\s]+)\s+(?:ni|dan)\s+([^\s,]+)\s+(?:ga)', instruction)
    
    if general_match:
        old_text = general_match.group(1)
        new_text = general_match.group(2)
        if old_text in text:
            replacements.append({
                "old": old_text,
                "new": new_text,
                "type": "Matn",
                "confidence": "high"
            })
    
    return replacements

def apply_replacements_to_pdf(pdf_bytes: bytes, replacements: List[dict]) -> tuple:
    """PDF ga o'zgarishlarni qo'llash"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_changes = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        for repl in replacements:
            old = repl['old']
            new = repl['new']
            
            text_instances = page.search_for(old)
            
            if text_instances:
                # Font ma'lumotlarini olish
                blocks = page.get_text("dict")["blocks"]
                font_info = {'size': 11, 'font': 'helv', 'color': (0, 0, 0)}
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if old in span["text"]:
                                    color_int = span.get("color", 0)
                                    font_info = {
                                        'size': span.get("size", 11),
                                        'font': 'helv',
                                        'color': (
                                            ((color_int >> 16) & 255) / 255.0,
                                            ((color_int >> 8) & 255) / 255.0,
                                            (color_int & 255) / 255.0
                                        )
                                    }
                                    break
                
                # Har bir instance uchun
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                
                page.apply_redactions()
                
                for inst in text_instances:
                    try:
                        page.insert_text(
                            (inst.x0, inst.y1 - 2),
                            new,
                            fontsize=font_info['size'],
                            fontname=font_info['font'],
                            color=font_info['color']
                        )
                        total_changes += 1
                    except:
                        total_changes += 1
    
    output = BytesIO()
    doc.save(output, garbage=4, deflate=True)
    output.seek(0)
    return output.getvalue(), total_changes

def apply_replacements_to_docx(docx_bytes: bytes, replacements: List[dict]) -> tuple:
    """Word hujjatiga o'zgarishlarni qo'llash"""
    doc = Document(BytesIO(docx_bytes))
    total_changes = 0
    
    for para in doc.paragraphs:
        for repl in replacements:
            old = repl['old']
            new = repl['new']
            
            if old.lower() in para.text.lower():
                for run in para.runs:
                    if old.lower() in run.text.lower():
                        pattern = re.compile(re.escape(old), re.IGNORECASE)
                        matches = pattern.findall(run.text)
                        if matches:
                            run.text = pattern.sub(new, run.text)
                            total_changes += len(matches)
    
    # Tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for repl in replacements:
                        for run in para.runs:
                            if repl['old'].lower() in run.text.lower():
                                pattern = re.compile(re.escape(repl['old']), re.IGNORECASE)
                                if pattern.search(run.text):
                                    run.text = pattern.sub(repl['new'], run.text)
                                    total_changes += 1
    
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue(), total_changes

# =================== API ENDPOINTS ===================

@app.get("/")
async def root():
    return {"message": "AI Doc Pro API", "version": "1.0.0", "status": "active"}

@app.post("/api/excel/generate")
async def generate_excel(request: ExcelRequest):
    """Excel yaratish"""
    try:
        structure = generate_excel_structure(request.prompt)
        excel_bytes = create_excel_file(structure)
        
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={structure['title']}.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/excel/preview")
async def preview_excel(request: ExcelRequest):
    """Excel strukturasini oldindan ko'rish"""
    try:
        structure = generate_excel_structure(request.prompt)
        return {"success": True, "structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/autofill/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    instruction: str = ""
):
    """Hujjatni tahlil qilish"""
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        # Matnni ajratib olish
        text = ""
        if file_ext == 'pdf':
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text += page.get_text() + "\n"
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
            raise HTTPException(status_code=400, detail="Qo'llab-quvvatlanmaydigan format")
        
        # Almashtirishlarni topish
        replacements = analyze_text_for_replacements(text, instruction)
        
        return {
            "success": True,
            "text": text[:3000],
            "replacements": replacements,
            "file_type": file_ext
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/autofill/apply")
async def apply_autofill(
    file: UploadFile = File(...),
    replacements: str = ""
):
    """O'zgarishlarni qo'llash"""
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        repl_list = json.loads(replacements) if replacements else []
        
        if file_ext == 'pdf':
            modified, changes = apply_replacements_to_pdf(content, repl_list)
            media_type = "application/pdf"
        elif file_ext == 'docx':
            modified, changes = apply_replacements_to_docx(content, repl_list)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_ext == 'txt':
            text = content.decode('utf-8', errors='ignore')
            for r in repl_list:
                pattern = re.compile(re.escape(r['old']), re.IGNORECASE)
                text = pattern.sub(r['new'], text)
            modified = text.encode('utf-8')
            changes = len(repl_list)
            media_type = "text/plain"
        else:
            raise HTTPException(status_code=400, detail="Qo'llab-quvvatlanmaydigan format")
        
        return StreamingResponse(
            BytesIO(modified),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=modified_{file.filename}",
                "X-Changes-Count": str(changes)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
