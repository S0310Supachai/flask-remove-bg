from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from rembg import remove
from PIL import Image

# ตั้งค่าตัวแปร environment variable สำหรับ API key
api_key = os.environ.get("REMOVEBG_API_KEY")

app = Flask(__name__)

# ตั้งค่าโฟลเดอร์สำหรับเก็บไฟล์
UPLOAD_FOLDER = 'img'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# ฟังก์ชันตรวจสอบว่าเป็นไฟล์ที่รองรับหรือไม่
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ฟังก์ชันเพิ่มความละเอียดของภาพ (เพิ่มขนาดภาพ)
def enhance_image(input_image_path):
    with Image.open(input_image_path) as img:
        # เพิ่มความละเอียด (ปรับขนาดภาพให้ใหญ่ขึ้น)
        img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
        enhanced_image_path = input_image_path.replace(".", "_enhanced.")
        img.save(enhanced_image_path)
        return enhanced_image_path

# ฟังก์ชันลบพื้นหลัง
def remove_background(input_image_path, output_image_path):
    with open(input_image_path, 'rb') as input_file:
        input_data = input_file.read()
        
    output_data = remove(input_data)
    
    with open(output_image_path, 'wb') as output_file:
        output_file.write(output_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'fileUpload' not in request.files:
        return redirect(request.url)
    file = request.files['fileUpload']
    
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # เพิ่มความละเอียดของภาพ
        enhanced_image_path = enhance_image(file_path)
        
        # ลบพื้นหลังจากภาพที่เพิ่มความละเอียดแล้ว
        output_filename = f"no_bg_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        remove_background(enhanced_image_path, output_path)
        
        # ส่งชื่อไฟล์ที่ลบพื้นหลังแล้วไปยังหน้า HTML
        return render_template('index.html', uploaded_image=output_filename)

@app.route('/img/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # ใช้พอร์ตที่ Render กำหนด
    app.run(host='0.0.0.0', port=port)
