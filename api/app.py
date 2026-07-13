import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import requests

app = FastAPI()

# تفعيل الـ CORS لكي يتمكن موقعك في بلوجر من الاتصال بهذا السيرفر بأمان
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# جلب مفتاح غروق تلقائياً من إعدادات البيئة الآمنة في السيرفر
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

class VideoRequest(BaseModel):
    url: str

@app.post("/roast-video")
async def roast_video(request: VideoRequest):
    video_url = request.url.strip()
    
    if not video_url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
        
    try:
        # 1. استخراج النصوص، العناوين، أو الوصف من رابط الفيديو باستخدام yt-dlp
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get('title', '')
            video_description = info.get('description', '')
            # دمج العنوان والوصف لإعطاء الذكاء الاصطناعي سياقاً كاملاً عن الفيديو
            video_context = f"Title: {video_title}\nDescription: {video_description}"

        # 2. إعداد الـ Prompt الساخر والمطور بلغة غروق لإنتاج ميمز بالإنجليزية
        prompt_text = (
            "You are a savage, witty, and deeply sarcastic internet roaster from Reddit/Twitter. "
            "Analyze the following video metadata (Title and Description) and generate exactly 3 separate, "
            "short, extremely funny, and savage comment options IN ENGLISH that would get thousands of upvotes "
            "under this video. Do not be generic. Your output must ONLY contain the 3 comment options, "
            "each on a brand new line. Absolutely NO numbers, NO explanations, and NO introduction."
        )

        # 3. إرسال البيانات المجمعة إلى سيرفر Groq باستخدام موديل النصوص الضخم والأحدث
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": f"Video Data:\n{video_context}\n\n{prompt_text}"
                }
            ],
            "temperature": 0.85
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Groq API failed to respond")
            
        result_data = response.json()
        output_text = result_data['choices'][0]['message']['content']
        
        # تنظيف الأسطر المرتجعة وتجهيزها في مصفوفة مرتبة
        lines = [line.strip() for line in output_text.split('\n') if line.strip()]
        
        return {"comments": lines}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
