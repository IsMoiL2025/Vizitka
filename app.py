from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Telegram bot konfiguratsiyasi
BOT_TOKEN = '6592066300:AAED-lf6dpiRQy_k98s24dfR_1l2iMjms4U'
CHAT_ID = '5641197226'

def get_location(ip):
    """IP orqali lokatsiyani aniqlash"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        data = response.json()
        if data['status'] == 'success':
            return f"{data['city']}, {data['regionName']}, {data['country']}"
        return "Noma'lum"
    except:
        return "Noma'lum"

def send_to_telegram(message):
    """Telegramga xabar yuborish"""
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegramga xabar yuborishda xato: {e}")
        return False

@app.route('/notify', methods=['POST'])
def notify():
    try:
        data = request.get_json()
        
        # Foydalanuvchi ma'lumotlari
        ip = data.get('ip', 'Noma\'lum')
        name = data.get('name', 'Noma\'lum')
        platform = data.get('platform', 'Noma\'lum')
        captcha_status = data.get('captcha', 'Noma\'lum')
        
        # Qo'shimcha ma'lumotlar
        location = get_location(ip)
        browser = "Chrome" if "Chrome" in data.get('device', '') else "Boshqa"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Telegramga yuboriladigan xabar
        message = f"""
<b>🆕 Yangi vizitka kirishi! (Kapcha: {'✅' if captcha_status == 'passed' else '❌'})</b>

👤 <b>Ism:</b> {name}
📱 <b>Platforma:</b> {platform}
🌐 <b>IP manzil:</b> {ip}
📍 <b>Lokatsiya:</b> {location}
🕒 <b>Vaqt:</b> {current_time}
        
<b>📱 Qurilma ma'lumotlari:</b>
🖥️ <b>Brauzer:</b> {browser}
📏 <b>Ekran o'lchami:</b> {data.get('screen', 'Noma\'lum')}
🗣️ <b>Til:</b> {data.get('language', 'Noma\'lum')}
        """
        
        # Xabarni yuborish
        if send_to_telegram(message):
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Telegramga xabar yuborib bo\'lmadi'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='https://ismoil2025.github.io/Vizitka/notify', port=5001, debug=True)
