import os
import base64
import io
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

DRIVING_MODES = {
    'dynamic': {
        'label': '疾走感',
        'description': 'High-speed drifting with snow spray, dynamic motion blur, aggressive stance'
    },
    'tough': {
        'label': '雪まみれ',
        'description': 'Car covered in snow, pushing through blizzard, snow accumulation on body'
    },
    'night': {
        'label': '夜の幻想',
        'description': 'Magical night scene with diamond dust, aurora borealis, starry sky'
    }
}

CAR_MODELS = {
    'mazda3': 'MAZDA3 FASTBACK',
    'roadster': 'EUNOS ROADSTER',
    'mazda787b': 'MAZDA 787B'
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_prompt(car_model, driving_mode):
    mode_info = DRIVING_MODES.get(driving_mode, DRIVING_MODES['dynamic'])
    car_name = CAR_MODELS.get(car_model, 'MAZDA3 FASTBACK')
    
    prompt = f"""Transform this children's car coloring drawing into a photorealistic image of a {car_name} driving on a snowy Hokkaido winter test track.

Scene requirements:
- Location: Hokkaido winter test track with deep snow
- Weather: Heavy snowfall, winter atmosphere
- {mode_info['description']}

Style requirements:
- Photorealistic rendering
- Professional automotive photography quality
- 16:9 aspect ratio
- Dramatic lighting
- Keep the color scheme from the original drawing if visible

The car should be the main focus, driving through the snowy landscape with realistic snow effects and winter atmosphere."""
    
    return prompt


def generate_image_with_gemini(image_data, car_model, driving_mode):
    if DRY_RUN:
        return create_placeholder_image()
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
        
        prompt = generate_prompt(car_model, driving_mode)
        
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_bytes = part.inline_data.data
                return base64.b64encode(image_bytes).decode('utf-8')
        
        return create_placeholder_image()
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return create_placeholder_image()


def create_placeholder_image():
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(30, 60, 90))
    
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    for i in range(0, width, 20):
        for j in range(0, height, 20):
            if (i + j) % 40 == 0:
                draw.ellipse([i, j, i+3, j+3], fill=(255, 255, 255, 128))
    
    text = "DRY RUN MODE"
    text2 = "AI くるまデザイナー"
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font = ImageFont.load_default()
        font2 = font
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 30
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    bbox2 = draw.textbbox((0, 0), text2, font=font2)
    text2_width = bbox2[2] - bbox2[0]
    x2 = (width - text2_width) // 2
    y2 = y + text_height + 20
    draw.text((x2, y2), text2, fill=(200, 200, 200), font=font2)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


@app.route('/')
def index():
    return render_template('index.html', 
                         driving_modes=DRIVING_MODES,
                         car_models=CAR_MODELS)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': '画像がアップロードされていません'}), 400
        
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        car_model = data.get('car_model', 'mazda3')
        driving_mode = data.get('driving_mode', 'dynamic')
        
        if car_model not in CAR_MODELS:
            car_model = 'mazda3'
        if driving_mode not in DRIVING_MODES:
            driving_mode = 'dynamic'
        
        result_image = generate_image_with_gemini(image_data, car_model, driving_mode)
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{result_image}',
            'dry_run': DRY_RUN
        })
        
    except Exception as e:
        print(f"Error in generate endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': '画像データがありません'}), 400
        
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name='ai_car_designer_result.png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
