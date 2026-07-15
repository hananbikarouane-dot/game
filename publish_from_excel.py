import os
import json
import time
import random
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']
EXCEL_FILE_PATH = 'lap_omega_all_colors.xlsx'
INDEX_FILE_PATH = 'last_index.txt'

def get_blogger_service():
    token_str = os.environ.get('BLOGGER_TOKEN')
    if not token_str:
        raise ValueError("❌ BLOGGER_TOKEN not found in GitHub Secrets!")
    
    creds_info = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("[~] الـ Token منتهي الصلاحية... جاري تجديده تلقائياً...")
            try:
                creds.refresh(Request())
                print("[✓] تم تجديد الصلاحية بنجاح!")
            except Exception as e:
                raise Exception(f"❌ فشل تجديد التوكن: {e}")
        else:
            raise Exception("❌ الـ Token غير صالح ولا يحتوي على refresh_token.")
            
    return build('blogger', 'v3', credentials=creds)

def publish_all_products():
    blog_id = os.environ.get('BLOG_ID')
    if not blog_id:
        raise ValueError("❌ BLOG_ID not found in GitHub Secrets!")
        
    if not os.path.exists(EXCEL_FILE_PATH):
        raise FileNotFoundError(f"❌ File {EXCEL_FILE_PATH} not found!")
        
    df = pd.read_excel(EXCEL_FILE_PATH)
    
    start_index = 0
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as f:
            try:
                start_index = int(f.read().strip())
                print(f"[✓] سنبدأ من السطر: {start_index}")
            except:
                start_index = 0

    if start_index >= len(df):
        print("[✓] تم نشر كافة المنتجات! إعادة التعيين إلى الصفر...")
        start_index = 0
        
    service = get_blogger_service()
    
    # نشر 5 منتجات فقط في كل تشغيل لحماية الحساب الجديد
    max_publish_count = 5  
    count = 0  
    current_index = start_index

    while count < max_publish_count and current_index < len(df):
        row = df.iloc[current_index]
        
        product_title = row['اسم المنتج (Title)']
        color = row['اللون (Color)']
        ref = str(row['المرجع (SKU / Ref)'])
        image_url = row['رابط الصورة (Image URL)']
        desc = row['الوصف والمواصفات (Description)']
        
        # ⚠️ القيم الافتراضية المتوافقة مع فلاتر القالب 
        brand = "lap"           # القالب يفحص وجود كلمة 'lap' أو 'ingelec' ليصنف الماركة
        category = "commande"   # القالب يقبل: protection, commande, automatisation, énergie
        price = "150"           # يجب أن يكتب السعر كرقم مجرد ليقرأه القالب
        
        # 🌟 صياغة المحتوى متطابقة تماماً مع الـ Regular Expressions (Regex) الموجودة في قالبك
        post_content = f"""<div style="text-align: right; direction: rtl;">
<img src="{image_url}" alt="{product_title}" style="max-width:100%; display:block; margin-bottom: 15px;" />
<p>السعر الإجمالي: {price}</p>
<p>الماركة: {brand}</p>
<p>التصنيف: {category}</p>
<p>اللون: {color}</p>
<p>المرجع: {ref}</p>
<hr />
<div class="product-description">
    <p>{desc}</p>
</div>
</div>"""

        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': blog_id},
            'title': f"{product_title}",
            'content': post_content,
            # القالب يقرأ النصوص من الداخل، ولكن إضافة التسميات تنظم الأرشيف
            'labels': [category, brand]
        }
        
        try:
            # 🚨 تنبيه: القالب يقوم بجلب المنشورات العامة فقط (fetch) 
            # لذلك يجب تغيير isDraft إلى False لكي يراها القالب على الواجهة فوراً!
            request = service.posts().insert(blogId=blog_id, body=post_body, isDraft=False)
            request.execute()
            print(f"✅ Published Live: {product_title} ({color})")
            count += 1
            
            if count < max_publish_count:
                delay_time = random.randint(30, 60)
                print(f"[⏳] الانتظار لمدة {delay_time} ثانية لمحاكاة السلوك البشري...")
                time.sleep(delay_time)
                
        except Exception as e:
            print(f"❌ Error publishing {product_title}: {e}")
            
        current_index += 1

    with open(INDEX_FILE_PATH, 'w') as f:
        f.write(str(current_index))
    print(f"\n📝 [✓] تم حفظ مؤشر التوقف الحالي: {current_index}")

if __name__ == '__main__':
    publish_all_products()
