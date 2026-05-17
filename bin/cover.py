import yaml
import os
import fitz  # PyMuPDF
from datetime import datetime
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors

# --- THEME SETTINGS ---
BACKGROUND_COLOR = colors.black
FRAME_COLOR = colors.yellow
TEXT_COLOR = colors.white
URL = "wildlife.vonlaszewski.com"
FULL_URL = "https://wildlife.vonlaszewski.com"
CREATE_PNG = True
IMAGE_DIR = "./images"  # Target directory for generated files

def load_quarto_config(filepath="_quarto.yml"):
    """Finds and parses the Quarto config, checking parent dir if needed."""
    if not os.path.exists(filepath):
        parent_path = os.path.join("..", "_quarto.yml")
        if os.path.exists(parent_path):
            filepath = parent_path
        else:
            return "Observing Eagles", "Gregor von Laszewski", "March 2026", "images/landing.png"
            
    with open(filepath, 'r') as file:
        config = yaml.safe_load(file)
    
    book_cfg = config.get('book', {})
    format_cfg = config.get('format', {}).get('pdf', {})
    
    title = book_cfg.get('title', 'Observing Eagles')
    author = book_cfg.get('author', 'Gregor von Laszewski')
    image_path = book_cfg.get('cover-image', format_cfg.get('cover-image', 'images/landing.png'))
    
    date_val = book_cfg.get('date', 'last-modified')
    if date_val == "last-modified":
        try:
            mtime = os.path.getmtime(filepath)
            date_str = datetime.fromtimestamp(mtime).strftime("%B %d, %Y")
        except OSError:
            date_str = datetime.now().strftime("%B %d, %Y")
    else:
        date_str = str(date_val)
        
    return title, author, date_str, image_path

def draw_rounded_image(c, image_path, x, y, width, height, corner_radius):
    """Clips image to rounded rectangle."""
    if not os.path.exists(image_path):
        return
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, width, height, corner_radius)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(image_path, x, y, width=width, height=height, mask='auto')
    c.restoreState()

def convert_pdf_to_png(pdf_path, png_path):
    """High-res PDF to PNG conversion using PyMuPDF (300 DPI)."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(4.166, 4.166))
    pix.save(png_path)
    doc.close()

def create_cover_page(title, author, date_str, image_path, filename="cover.pdf"):
    # Ensure the target directory exists
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == 'bin':
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
    else:
        project_root = current_dir
        
    target_path = os.path.join(project_root, IMAGE_DIR)
    os.makedirs(target_path, exist_ok=True)

    pdf_out = os.path.join(target_path, filename)
    png_out = os.path.join(target_path, filename.replace(".pdf", ".png"))

    c = canvas.Canvas(pdf_out, pagesize=LETTER)
    w_page, h_page = LETTER
    center_x, center_y = w_page / 2.0, h_page / 2.0

    # 1. Background Layer
    c.setFillColor(BACKGROUND_COLOR)
    c.rect(0, 0, w_page, h_page, fill=1, stroke=0)

    # 2. Frame Layer
    c.setStrokeColor(FRAME_COLOR)
    c.setLineWidth(2)
    c.rect(0.5 * inch, 0.5 * inch, w_page - 1 * inch, h_page - 1 * inch, fill=0, stroke=1)

    # 3. Image Layer
    final_img_h = 0
    if os.path.exists(image_path):
        img_w_target = 6.0 * inch
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
        final_img_h = img_w_target * (orig_h / orig_w)
        img_x, img_y = center_x - (img_w_target/2.0), center_y - (final_img_h/2.0)
        draw_rounded_image(c, image_path, img_x, img_y, img_w_target, final_img_h, 0.4 * inch)

    # 4. Text Layer
    c.setFillColor(TEXT_COLOR)
    
    # Title
    title_y = (center_y + (final_img_h/2.0) + 0.8 * inch) if final_img_h else (h_page - 2.5 * inch)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(center_x, title_y, title.upper())
    
    # Author
    author_y = (center_y - (final_img_h/2.0) - 1.2 * inch) if final_img_h else (3.0 * inch)
    c.setFont("Helvetica", 18)
    c.drawCentredString(center_x, author_y, f"By {author}")
    
    # Date
    date_y = author_y - 0.5 * inch
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(center_x, date_y, f"Updated: {date_str}")

    # URL (Clickable Link)
    url_y = date_y - 0.3 * inch
    c.setFont("Helvetica", 10)
    c.drawCentredString(center_x, url_y, URL)
    
    # Calculate link area
    url_width = c.stringWidth(URL, "Helvetica", 10)
    link_rect = (center_x - url_width/2, url_y - 2, center_x + url_width/2, url_y + 10)
    c.linkURL(FULL_URL, link_rect, thickness=0)

    c.save()
    print(f"PDF built: {pdf_out}")
    
    if CREATE_PNG:
        try:
            convert_pdf_to_png(pdf_out, png_out)
            print(f"PNG built: {png_out}")
        except Exception as e:
            print(f"PNG Error: {e}")

if __name__ == "__main__":
    yml_file = "_quarto.yml" if os.path.exists("_quarto.yml") else "../_quarto.yml"
    try:
        t, a, d, img = load_quarto_config(yml_file)
        create_cover_page(t, a, d, img)
    except Exception as e:
        print(f"Build Failed: {e}")