from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import tempfile
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from docx import Document
from io import BytesIO
import json
import re

app = FastAPI(title="AI Doc Pro API")

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Doc Pro API ishlamoqda!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ============ EXCEL GENERATOR ============

def generate_excel_structure(prompt: str) -> dict:
    """Prompt asosida Excel strukturasini aniqlash"""
    prompt_lower = prompt.lower()
    
    # Moliyaviy hisobot
    if "moliya" in prompt_lower or "daromad" in prompt_lower or "xarajat" in prompt_lower or "kirim" in prompt_lower or "chiqim" in prompt_lower:
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
    
    # Byudjet rejasi
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
                    [6, "Jamg'arma", 1500000, 1500000, "=C7-D7"],
                    ["", "JAMI:", "=SUM(C2:C7)", "=SUM(D2:D7)", "=C8-D8"],
                ]
            }]
        }
    
    # Mahsulotlar ro'yxati
    elif "mahsulot" in prompt_lower or "narx" in prompt_lower or "tovar" in prompt_lower or "price" in prompt_lower:
        return {
            "title": "Mahsulotlar_Royxati",
            "sheets": [{
                "name": "Mahsulotlar",
                "headers": ["№", "Mahsulot nomi", "Miqdori", "Birlik narxi", "Jami summa"],
                "data": [
                    [1, "Mahsulot A", 100, 50000, "=C2*D2"],
                    [2, "Mahsulot B", 50, 75000, "=C3*D3"],
                    [3, "Mahsulot C", 200, 25000, "=C4*D4"],
                    [4, "Mahsulot D", 75, 60000, "=C5*D5"],
                    [5, "Mahsulot E", 150, 40000, "=C6*D6"],
                    ["", "", "", "JAMI:", "=SUM(E2:E6)"],
                ]
            }]
        }
    
    # Kafe/Restoran
    elif "kafe" in prompt_lower or "restoran" in prompt_lower or "menyu" in prompt_lower or "menu" in prompt_lower:
        return {
            "title": "Kafe_Hisoboti",
            "sheets": [{
                "name": "Menyu",
                "headers": ["№", "Taom nomi", "Kategoriya", "Narxi", "Sotilgan", "Daromad"],
                "data": [
                    [1, "Palov", "Asosiy taom", 35000, 50, "=D2*E2"],
                    [2, "Lag'mon", "Asosiy taom", 30000, 40, "=D3*E3"],
                    [3, "Shashlik", "Asosiy taom", 45000, 30, "=D4*E4"],
                    [4, "Choy", "Ichimlik", 5000, 100, "=D5*E5"],
                    [5, "Salat", "Yengil taom", 20000, 25, "=D6*E6"],
                    ["", "", "", "", "JAMI:", "=SUM(F2:F6)"],
                ]
            }]
        }
    
    # Kundalik ishlar / Vazifalar
    elif "kundalik" in prompt_lower or "vazifa" in prompt_lower or "task" in prompt_lower or "ish ro'yxat" in prompt_lower:
        return {
            "title": "Kundalik_Ishlar",
            "sheets": [{
                "name": "Vazifalar",
                "headers": ["№", "Sana", "Vazifa", "Status", "Izoh"],
                "data": [
                    [1, "27.01.2025", "Namuna vazifa 1", "Bajarildi", ""],
                    [2, "27.01.2025", "Namuna vazifa 2", "Jarayonda", ""],
                    [3, "28.01.2025", "Namuna vazifa 3", "Kutilmoqda", ""],
                    [4, "28.01.2025", "Namuna vazifa 4", "Kutilmoqda", ""],
                    [5, "29.01.2025", "Namuna vazifa 5", "Kutilmoqda", ""],
                ]
            }]
        }
    
    # Xodimlar ro'yxati
    elif "xodim" in prompt_lower or "ishchi" in prompt_lower or "hodim" in prompt_lower or "personal" in prompt_lower:
        return {
            "title": "Xodimlar_Royxati",
            "sheets": [{
                "name": "Xodimlar",
                "headers": ["№", "F.I.O", "Lavozim", "Telefon", "Ish haqi", "Izoh"],
                "data": [
                    [1, "Ismailov Anvar", "Direktor", "+998901234567", 15000000, ""],
                    [2, "Karimova Dilnoza", "Buxgalter", "+998901234568", 8000000, ""],
                    [3, "Toshmatov Jasur", "Menejer", "+998901234569", 6000000, ""],
                ]
            }]
        }

    # Inventar / Ombor
    elif "inventar" in prompt_lower or "ombor" in prompt_lower or "sklad" in prompt_lower:
        return {
            "title": "Inventar_Hisoboti",
            "sheets": [{
                "name": "Ombor",
                "headers": ["№", "Mahsulot nomi", "Miqdori", "Birligi", "Narxi", "Jami summa"],
                "data": [
                    [1, "Mahsulot A", 100, "dona", 50000, "=C2*E2"],
                    [2, "Mahsulot B", 50, "kg", 25000, "=C3*E3"],
                    [3, "Mahsulot C", 200, "litr", 15000, "=C4*E4"],
                    ["", "", "", "", "JAMI:", "=SUM(F2:F4)"],
                ]
            }]
        }
    
    # Jadval / Table
    elif "jadval" in prompt_lower or "table" in prompt_lower:
        return {
            "title": "Jadval",
            "sheets": [{
                "name": "Ma'lumotlar",
                "headers": ["№", "Ustun 1", "Ustun 2", "Ustun 3", "Ustun 4"],
                "data": [
                    [1, "Ma'lumot 1", "Ma'lumot 2", "Ma'lumot 3", "Ma'lumot 4"],
                    [2, "Ma'lumot 5", "Ma'lumot 6", "Ma'lumot 7", "Ma'lumot 8"],
                    [3, "Ma'lumot 9", "Ma'lumot 10", "Ma'lumot 11", "Ma'lumot 12"],
                ]
            }]
        }
    
    # Default - oddiy jadval
    else:
        return {
            "title": "Hujjat",
            "sheets": [{
                "name": "Varaq1",
                "headers": ["№", "Nomi", "Miqdori", "Narxi", "Jami"],
                "data": [
                    [1, "Element 1", 10, 5000, "=C2*D2"],
                    [2, "Element 2", 20, 3000, "=C3*D3"],
                    [3, "Element 3", 15, 4000, "=C4*D4"],
                    ["", "", "", "JAMI:", "=SUM(E2:E4)"],
                ]
            }]
        }

def create_styled_excel(structure: dict) -> str:
    """Chiroyli Excel fayl yaratish"""
    wb = Workbook()
    
    # Stillar
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for sheet_idx, sheet_data in enumerate(structure["sheets"]):
        if sheet_idx == 0:
            ws = wb.active
            ws.title = sheet_data["name"]
        else:
            ws = wb.create_sheet(title=sheet_data["name"])
        
        # Sarlavhalar
        for col_idx, header in enumerate(sheet_data["headers"], 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        # Ma'lumotlar
        for row_idx, row_data in enumerate(sheet_data["data"], 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center")
        
        # Ustun kengligini sozlash
        for col_idx, header in enumerate(sheet_data["headers"], 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 18
    
    # Faylni saqlash
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, f"{structure['title']}.xlsx")
    wb.save(filepath)
    
    return filepath

# Excel Preview endpoint - Frontend kutayotgan nom
@app.post("/api/excel/preview")
async def excel_preview(prompt: str = Form(...)):
    """Excel preview - strukturani ko'rsatish"""
    try:
        structure = generate_excel_structure(prompt)
        return {
            "success": True,
            "preview": structure,
            "title": structure["title"],
            "sheets": structure["sheets"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Excel Generate endpoint - Frontend kutayotgan nom
@app.post("/api/excel/generate")
async def excel_generate(prompt: str = Form(...)):
    """Excel fayl yaratish va yuklab olish"""
    try:
        structure = generate_excel_structure(prompt)
        filepath = create_styled_excel(structure)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{structure['title']}.xlsx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Eski endpoint ham saqlab qolamiz
@app.post("/api/generate-excel")
async def generate_excel(prompt: str = Form(...)):
    """Excel fayl yaratish (eski endpoint)"""
    return await excel_generate(prompt)

# ============ AUTO-FILL ============

def analyze_text_for_replacements(text: str, instruction: str) -> list:
    """Matndan almashtirilishi kerak bo'lgan joylarni topish"""
    replacements = []
    
    # Umumiy patternlar
    patterns = [
        (r'\[([^\]]+)\]', 'square_bracket'),
        (r'\{([^\}]+)\}', 'curly_bracket'),
        (r'<([^>]+)>', 'angle_bracket'),
        (r'___+', 'underline'),
        (r'\.\.\.+', 'dots'),
        (r'_____', 'blank'),
    ]
    
    for pattern, pattern_type in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            replacements.append({
                "original": match.group(0),
                "placeholder": match.group(1) if match.lastindex else match.group(0),
                "type": pattern_type,
                "start": match.start(),
                "end": match.end(),
                "suggested_value": ""
            })
    
    return replacements

# Auto-Fill Analyze endpoint
@app.post("/api/autofill/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    instruction: str = Form("")
):
    """Hujjatni tahlil qilish"""
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        text = ""
        
        if file_ext == 'pdf':
            raise HTTPException(status_code=400, detail="PDF hozircha qo'llab-quvvatlanmaydi. Word yoki TXT fayldan foydalaning.")
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
        
        replacements = analyze_text_for_replacements(text, instruction)
        
        return {
            "success": True,
            "text": text[:3000],
            "replacements": replacements,
            "file_type": file_ext
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Auto-Fill Apply endpoint
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
        
        else:
            raise HTTPException(status_code=400, detail="Qo'llab-quvvatlanmaydigan format")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Noto'g'ri replacements formati")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
