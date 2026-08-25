#!/usr/bin/env python3
"""
🤖 Android AI Agent - متطور مع Gemini Vision
رؤية الشاشة + تحديد الإحداثيات + تنفيذ المهام
devloper : drox
instagram : rayan_71x
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
import re
import base64
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from PIL import Image
from io import BytesIO

# ============================================================
# إعدادات Gemini API
# ============================================================

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your_api_key')
GEMINI_MODEL = 'gemini-3.5-flash'  # دعم الرؤية

def call_gemini_vision(prompt, image_base64):
    """استدعاء Gemini Vision API مع صورة"""
    if not GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": image_base64}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "topP": 0.95,
            "topK": 40
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"⚠️ Gemini API خطأ: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None
    
    return None

def analyze_screen_with_vision(task, screenshot_b64):
    """تحليل الشاشة باستخدام Gemini Vision"""
    prompt = f"""
    أنت وكيل ذكي للتحكم بهاتف Android.
    
    المهمة المطلوبة: {task}
    
    أبعاد الشاشة: {SCREEN_WIDTH}x{SCREEN_HEIGHT} بكسل.
    
    قم بتحليل لقطة الشاشة وحدد:
    1. ما هو التطبيق المفتوح حالياً؟
    2. أين يوجد العنصر المطلوب؟
    3. ما هو الإجراء التالي المناسب؟
    
    أجب بصيغة JSON:
    {{
        "current_app": "اسم التطبيق المفتوح",
        "action": "tap" | "swipe" | "type" | "open_app" | "back" | "home" | "done",
        "target_text": "النص المطلوب الضغط عليه",
        "x": عدد (إحداثي X),
        "y": عدد (إحداثي Y),
        "x2": عدد (إحداثي X2 للسحب),
        "y2": عدد (إحداثي Y2 للسحب),
        "text_to_type": "نص للكتابة",
        "app_to_open": "اسم التطبيق للفتح",
        "description": "شرح مختصر للإجراء",
        "confidence": 0.0-1.0,
        "found": true/false (هل وجد العنصر المطلوب؟)
    }}
    
    كن دقيقاً جداً في تحديد الإحداثيات.
    إذا لم تجد العنصر، اجعل found: false.
    """
    
    response = call_gemini_vision(prompt, screenshot_b64)
    if response:
        try:
            # استخراج JSON من الرد
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    return None

def find_element_with_vision(search_text, screenshot_b64):
    """البحث عن عنصر باستخدام Gemini Vision"""
    prompt = f"""
    ابحث عن العنصر الذي يحتوي على النص "{search_text}" في لقطة الشاشة.
    
    أبعاد الشاشة: {SCREEN_WIDTH}x{SCREEN_HEIGHT} بكسل.
    
    أجب بصيغة JSON:
    {{
        "found": true/false,
        "x": عدد (منتصف العنصر),
        "y": عدد (منتصف العنصر),
        "text": "النص الذي وجدته",
        "bounds": "مستطيل العنصر",
        "confidence": 0.0-1.0
    }}
    """
    
    response = call_gemini_vision(prompt, screenshot_b64)
    if response:
        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    return None

# ============================================================
# إعدادات Flask
# ============================================================

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# ============================================================
# إعدادات Shizuku
# ============================================================

os.environ['RISH_APPLICATION_ID'] = 'com.termux'
RISH_PATH = Path('/data/data/com.termux/files/usr/bin/rish')
SHIZUKU_AVAILABLE = False
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 2400

# ============================================================
# قاعدة البيانات
# ============================================================

DB_PATH = Path(__file__).parent / 'memory.db'

def init_database():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discovered_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            package TEXT,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            use_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS screen_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            analysis TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ قاعدة البيانات جاهزة")

def save_conversation(session_id, user_message, bot_response):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (session_id, user_message, bot_response)
        VALUES (?, ?, ?)
    ''', (session_id, user_message, bot_response))
    conn.commit()
    conn.close()

def get_conversation_history(session_id, limit=20):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_message, bot_response FROM conversations 
        WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?
    ''', (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{'user': row[0], 'bot': row[1]} for row in rows[::-1]]

def save_screen_analysis(task, analysis):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO screen_analysis (task, analysis)
        VALUES (?, ?)
    ''', (task, json.dumps(analysis)))
    conn.commit()
    conn.close()

def get_known_apps():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT name, package, use_count FROM discovered_apps ORDER BY use_count DESC')
    rows = cursor.fetchall()
    conn.close()
    return [{'name': row[0], 'package': row[1], 'use_count': row[2]} for row in rows]

def save_app_discovered(name, package):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO discovered_apps (name, package, use_count)
        VALUES (?, ?, COALESCE((SELECT use_count + 1 FROM discovered_apps WHERE name = ?), 1))
    ''', (name, package, name))
    conn.commit()
    conn.close()

# ============================================================
# دوال Shizuku والتحكم
# ============================================================

def check_shizuku():
    global SHIZUKU_AVAILABLE
    if not RISH_PATH.exists():
        SHIZUKU_AVAILABLE = False
        return False
    try:
        env = os.environ.copy()
        env['RISH_APPLICATION_ID'] = 'com.termux'
        result = subprocess.run(
            [str(RISH_PATH), '-c', 'id'],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        if result.returncode == 0 and 'uid=' in result.stdout:
            SHIZUKU_AVAILABLE = True
            update_screen_size()
            return True
    except:
        pass
    SHIZUKU_AVAILABLE = False
    return False

def run_command(cmd):
    if not SHIZUKU_AVAILABLE:
        return None
    try:
        env = os.environ.copy()
        env['RISH_APPLICATION_ID'] = 'com.termux'
        result = subprocess.run(
            [str(RISH_PATH), '-c', cmd],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

def run_adb_command(cmd):
    try:
        result = subprocess.run(
            ['adb', 'shell', cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

def update_screen_size():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    result = run_command('wm size')
    if not result:
        result = run_adb_command('wm size')
    if result:
        match = re.search(r'(\d+)x(\d+)', result)
        if match:
            SCREEN_WIDTH = int(match.group(1))
            SCREEN_HEIGHT = int(match.group(2))
            print(f"📱 أبعاد الشاشة: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

def capture_screenshot():
    """التقاط لقطة شاشة"""
    try:
        # عبر Shizuku
        env = os.environ.copy()
        env['RISH_APPLICATION_ID'] = 'com.termux'
        result = subprocess.run(
            [str(RISH_PATH), '-c', 'adb exec-out screencap -p'],
            capture_output=True,
            timeout=10,
            env=env
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            try:
                return Image.open(BytesIO(result.stdout))
            except:
                pass
        
        # عبر ADB
        result = subprocess.run(
            ['adb', 'exec-out', 'screencap', '-p'],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            try:
                return Image.open(BytesIO(result.stdout))
            except:
                pass
        
        return None
    except:
        return None

def get_screenshot_base64():
    img = capture_screenshot()
    if img:
        try:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except:
            return None
    return None

def get_installed_apps():
    result = run_command('pm list packages')
    if not result:
        result = run_adb_command('pm list packages')
    if not result:
        return {}
    apps = {}
    for line in result.split('\n'):
        if line.startswith('package:'):
            package = line.replace('package:', '').strip()
            name = package.split('.')[-1].capitalize()
            apps[name.lower()] = {'package': package, 'name': name}
            save_app_discovered(name, package)
    return apps

def open_app(package):
    result = run_command(f'monkey -p {package} -c android.intent.category.LAUNCHER 1')
    if result is None:
        result = run_adb_command(f'monkey -p {package} -c android.intent.category.LAUNCHER 1')
    return result is not None

def tap(x, y):
    result = run_command(f'input tap {x} {y}')
    if result is None:
        result = run_adb_command(f'input tap {x} {y}')
    return result is not None

def swipe(x1, y1, x2, y2, duration=300):
    result = run_command(f'input swipe {x1} {y1} {x2} {y2} {duration}')
    if result is None:
        result = run_adb_command(f'input swipe {x1} {y1} {x2} {y2} {duration}')
    return result is not None

def press_back():
    result = run_command('input keyevent KEYCODE_BACK')
    if result is None:
        result = run_adb_command('input keyevent KEYCODE_BACK')
    return result is not None

def press_home():
    result = run_command('input keyevent KEYCODE_HOME')
    if result is None:
        result = run_adb_command('input keyevent KEYCODE_HOME')
    return result is not None

def type_text(text):
    safe_text = text.replace(' ', '%s').replace('"', '\\"')
    result = run_command(f'input text "{safe_text}"')
    if result is None:
        result = run_adb_command(f'input text "{safe_text}"')
    return result is not None

def get_foreground_app():
    result = run_command('dumpsys window windows | grep -E "mCurrentFocus"')
    if not result:
        result = run_adb_command('dumpsys window windows | grep -E "mCurrentFocus"')
    if result:
        match = re.search(r'([a-zA-Z0-9._]+)/', result)
        if match:
            return match.group(1)
    return None

# ============================================================
# الوكيل الذكي الرئيسي
# ============================================================

class SmartAgent:
    def __init__(self):
        self.session_id = None
        self.last_screenshot = None
        self.context = {}
    
    def execute_task(self, task, session_id):
        """تنفيذ مهمة باستخدام Gemini Vision"""
        self.session_id = session_id
        
        # 1. التقاط الشاشة
        screenshot_b64 = get_screenshot_base64()
        if not screenshot_b64:
            return "❌ تعذر التقاط الشاشة"
        
        # 2. تحليل الشاشة
        analysis = analyze_screen_with_vision(task, screenshot_b64)
        if not analysis:
            return "❌ لم أستطع تحليل الشاشة"
        
        # 3. حفظ التحليل
        save_screen_analysis(task, analysis)
        
        # 4. تنفيذ الإجراء
        action = analysis.get('action')
        result = None
        
        if action == 'tap':
            x = analysis.get('x', SCREEN_WIDTH // 2)
            y = analysis.get('y', SCREEN_HEIGHT // 2)
            if tap(x, y):
                result = f"✅ تم النقر على ({x}, {y})"
            else:
                result = "❌ فشل النقر"
        
        elif action == 'swipe':
            x1 = analysis.get('x', SCREEN_WIDTH // 2)
            y1 = analysis.get('y', SCREEN_HEIGHT // 2)
            x2 = analysis.get('x2', SCREEN_WIDTH // 2)
            y2 = analysis.get('y2', SCREEN_HEIGHT // 2)
            if swipe(x1, y1, x2, y2):
                result = f"✅ تم السحب من ({x1},{y1}) إلى ({x2},{y2})"
            else:
                result = "❌ فشل السحب"
        
        elif action == 'type':
            text = analysis.get('text_to_type', '')
            if type_text(text):
                result = f"✅ تم كتابة: {text}"
            else:
                result = "❌ فشل الكتابة"
        
        elif action == 'open_app':
            app = analysis.get('app_to_open', '')
            apps = get_known_apps()
            for known_app in apps:
                if app.lower() in known_app['name'].lower():
                    if open_app(known_app['package']):
                        result = f"✅ تم فتح {known_app['name']}"
                        break
            if not result:
                result = f"❌ لم يتم العثور على التطبيق: {app}"
        
        elif action == 'back':
            if press_back():
                result = "✅ تم الضغط على زر الرجوع"
            else:
                result = "❌ فشل الرجوع"
        
        elif action == 'home':
            if press_home():
                result = "✅ تم الضغط على زر الرئيسية"
            else:
                result = "❌ فشل"
        
        elif action == 'done':
            result = "✅ المهمة مكتملة!"
        
        else:
            result = f"⚠️ إجراء غير معروف: {action}"
        
        # 5. توليد رد
        response_text = f"{analysis.get('description', '')}\n\n{result}"
        
        # إضافة معلومات إضافية
        if analysis.get('found') == False:
            response_text = f"🔍 لم أجد العنصر المطلوب على الشاشة.\n\n{result}"
        
        if analysis.get('current_app'):
            response_text = f"📱 التطبيق المفتوح: {analysis.get('current_app')}\n\n{response_text}"
        
        return response_text

# ============================================================
# دوال Flask
# ============================================================

smart_agent = SmartAgent()

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = session.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'الرجاء إدخال رسالة'}), 400
    
    # التحقق من الاتصال
    is_connected = check_shizuku()
    if not is_connected:
        return jsonify({
            'response': '❌ الهاتف غير متصل. تأكد من تشغيل Shizuku.',
            'connected': False
        })
    
    # تنفيذ المهمة باستخدام الوكيل الذكي
    try:
        bot_response = smart_agent.execute_task(user_message, session_id)
    except Exception as e:
        bot_response = f"❌ خطأ: {str(e)}"
    
    # حفظ المحادثة
    save_conversation(session_id, user_message, bot_response)
    
    return jsonify({
        'response': bot_response,
        'connected': is_connected
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    connected = check_shizuku()
    apps_count = len(get_known_apps())
    foreground = get_foreground_app()
    
    return jsonify({
        'connected': connected,
        'screen_size': f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}",
        'apps_count': apps_count,
        'gemini_available': bool(GEMINI_API_KEY),
        'foreground_app': foreground,
        'session_id': session.get('session_id', 'default')
    })

@app.route('/api/screenshot', methods=['GET'])
def get_screenshot():
    img_base64 = get_screenshot_base64()
    if img_base64:
        return jsonify({
            'status': 'success',
            'screenshot': img_base64,
            'width': SCREEN_WIDTH,
            'height': SCREEN_HEIGHT
        })
    return jsonify({'status': 'error', 'message': 'تعذر التقاط الشاشة'})

@app.route('/api/apps', methods=['GET'])
def get_apps():
    apps = get_known_apps()
    return jsonify({
        'status': 'success',
        'apps': apps,
        'count': len(apps)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_screen():
    """تحليل الشاشة فقط (بدون تنفيذ)"""
    data = request.json
    task = data.get('task', 'تحليل الشاشة')
    
    screenshot_b64 = get_screenshot_base64()
    if not screenshot_b64:
        return jsonify({'status': 'error', 'message': 'تعذر التقاط الشاشة'})
    
    analysis = analyze_screen_with_vision(task, screenshot_b64)
    if analysis:
        return jsonify({'status': 'success', 'analysis': analysis})
    return jsonify({'status': 'error', 'message': 'فشل التحليل'})

@app.route('/api/tap', methods=['POST'])
def tap_endpoint():
    data = request.json
    x = data.get('x')
    y = data.get('y')
    
    if x is None or y is None:
        return jsonify({'error': 'الرجاء تحديد الإحداثيات'}), 400
    
    success = tap(x, y)
    return jsonify({'success': success, 'x': x, 'y': y})

@app.route('/api/history', methods=['GET'])
def get_history():
    session_id = session.get('session_id', 'default')
    history = get_conversation_history(session_id)
    return jsonify({'status': 'success', 'history': history})

# ============================================================
# التشغيل
# ============================================================

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                          ║
║    🤖 Android AI Agent By drox- Gemini Vision              ║
║    👁️  يرى الشاشة ويحللها                               ║
║    🎯 يحدد الإحداثيات بدقة                              ║
║                                                          ║
║    🌐 http://localhost:5000                              ║
║                                                          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    init_database()
    
    print("🔍 فحص Shizuku...")
    check_shizuku()
    
    if SHIZUKU_AVAILABLE:
        print(f"📱 أبعاد الشاشة: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        apps = get_installed_apps()
        print(f"✅ تم العثور على {len(apps)} تطبيق")
    else:
        print("❌ Shizuku غير متصل")
    
    if GEMINI_API_KEY:
        print(f"✅ Gemini API متصل (النموذج: {GEMINI_MODEL})")
    else:
        print("⚠️ Gemini غير متصل")
    
    print(f"💾 قاعدة البيانات: {DB_PATH}")
    print("\n🚀 تشغيل الخادم...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)