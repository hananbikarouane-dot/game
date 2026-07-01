import os
import random
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bikoe_secret_key_2026'

# تفعيل الـ WebSockets مع خادم الإخراج لبيئة الإنتاج
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

QUESTIONS = [
    "لو استيقظت غداً ووجدت نفسك الشخص الوحيد في الكوكب، ما هو أول شيء ستفعله؟",
    "ما هو الموقف المضحك أو الغريب الذي حدث معك ولم تخبر به أحداً من قبل؟",
    "لو أتيحت لك الفرصة للسفر بالزمن، هل ستذهب للمستقبل أم للماضي؟ ولماذا؟",
    "خمن شيئاً واحداً تعتقد أن صديقك يخاف منه بشدة الآن؟",
    "ما هي العادة الغريبة التي تقوم بها عندما تكون بمفردك تماماً؟",
    "لو تم تخييرك بين العيش بدون إنترنت أو بدون مكيف طوال حياتك، ماذا تختار؟"
]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_or_join')
def on_create_or_join(data):
    room = data['room']
    join_room(room)
    initial_question = random.choice(QUESTIONS)
    emit('next_question', {'question': initial_question}, to=room)

@socketio.on('request_next')
def on_request_next(data):
    room = data['room']
    new_question = random.choice(QUESTIONS)
    emit('next_question', {'question': new_question}, to=room)

if __name__ == '__main__':
    # جلب المنفذ تلقائياً من السيرفر أو استخدام 5000 محلياً
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)