import os
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# النطاق المطلق للصلاحيات المطلوبة من جوجل للبلوجر
SCOPES = ['https://www.googleapis.com/auth/blogger']
EXCEL_FILE_PATH = 'lap_omega_all_colors.xlsx'
INDEX_FILE_PATH = 'last_index.txt'

def get_blogger_service():
    """
    توليد صلاحيات الاتصال ببلوجر مع الفحص والتجديد التلقائي للـ Token
    لتفادي خطأ الـ 403 (Permission Denied) في حال انتهاء الصلاحية المؤقتة.
    """
    token_str = os.environ.get('BLOGGER_TOKEN')
    if not token_str:
        raise ValueError("❌ BLOGGER_TOKEN not found in GitHub Secrets!")
    
    creds_info = json.loads(token_str)
    
    # تحويل بيانات الـ JSON إلى كائن صلاحيات معتمد من مكتبة جوجل
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    
    # 🌟 التحقق مما إذا كان الـ Token قد انتهى (ينتهي تلقائياً كل ساعة) وتجديده فوراً
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("[~] الـ Token منتهي الصلاحية... جاري تجديده تلقائياً الآن عن طريق الـ Refresh Token!")
            try:
                creds.refresh(Request())
                print("[✓] تم تجديد الصلاحية بنجاح!")
            except Exception as e:
                raise Exception(f"❌ فشل تجديد التوكن تلقائياً: {e}")
        else:
            raise Exception("❌ الـ Token غير صالح ولا يحتوي على refresh_token لإعادة التنشيط.")
            
    return build('blogger', 'v3', credentials=creds)

def publish_all_products():
    blog_id = os.environ.get('BLOG_ID')
    if not blog_id:
        raise ValueError("❌ BLOG_ID not found in GitHub Secrets!")
        
    # 1. التحقق من وجود ملف الإكسيل الخاص بالمنتجات
    if not os.path.exists(EXCEL_FILE_PATH):
        raise FileNotFoundError(f"❌ File {EXCEL_FILE_PATH} not found!")
        
    df = pd.read_excel(EXCEL_FILE_PATH)
    
    # 2. قراءة مؤشر آخر سطر تم نشره بنجاح لمنع التكرار
    start_index = 0
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as f:
            try:
                start_index = int(f.read().strip())
                print(f"[✓] تم العثور على نقطة التوقف السابقة! سنبدأ من السطر: {start_index}")
            except:
                start_index = 0

    if start_index >= len(df):
        print("[✓] تم نشر جميع المنتجات الموجودة في ملف Excel بالكامل!")
        exit()
        
    # تهيئة اتصال الخدمة بعد التحقق وتحديث الصلاحية
    service = get_blogger_service()
    
    max_publish_count = 5  # تحديد عدد المنتجات للنشر في كل دفعة (لتفادي حظر جوجل أو استهلاك طاقة الأكشن بالكامل)
    count = 0  
    current_index = start_index

    while count < max_publish_count and current_index < len(df):
        row = df.iloc[current_index]
        
        # جلب تفاصيل المنتج من أعمدة الإكسيل الخاصة بك
        product_title = row['اسم المنتج (Title)']
        color = row['اللون (Color)']
        ref = str(row['المرجع (SKU / Ref)'])
        image_url = row['رابط الصورة (Image URL)']
        desc = row['الوصف والمواصفات (Description)']
        source_link = row['رابط المصدر (Source Link)']
        
        brand = "LAP"  
        category = "commande"  
        price = "150"  
        
        # صياغة الـ HTML المتوافق مع بنية قالب متجرك الخاص
        post_content = f"""<div style="text-align: right; direction: rtl;">
<img src="{image_url}" alt="{product_title}" style="max-width:100%; display:none;" />

<p>السعر الإجمالي: {price}</p>
<p>الماركة: {brand}</p>
<p>التصنيف: {category}</p>
<p>اللون: {color}</p>
<p>المرجع: {ref}</p>

<hr />
<div class="product-description">
    <p><strong>📋 مواصفات المنتج الأساسية:</strong></p>
    <p>{desc}</p>
</div>

<div class="single-affiliate-box" style="margin-top: 20px; text-align: center;">
    <a class="aff-link-btn btn-amazon" href="{source_link}" target="_blank" style="padding: 10px 20px; background-color: #ff9900; color: white; text-decoration: none; border-radius: 5px; display: inline-block;">
        🔗 معاينة المنتج في المصدر الأصلي
    </a>
</div>
</div>"""

        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': blog_id},
            'title': f"{product_title} - {color}",
            'content': post_content,
            'labels': [category, brand],
            'status': 'DRAFT'  # يُنشر كمسودة لمراجعة جودة التنسيق قبل الإطلاق العام للمشترين
        }
        
        try:
            request = service.posts().insert(blogId=blog_id, body=post_body)
            request.execute()
            print(f"✅ Created draft: {product_title} ({color})")
            count += 1
        except Exception as e:
            print(f"❌ Error publishing {product_title}: {e}")
            
        current_index += 1

    # 3. حفظ مؤشر التوقف الجديد لاستخدامه في تشغيل الأكشن القادم تلقائياً
    with open(INDEX_FILE_PATH, 'w') as f:
        f.write(str(current_index))
    print(f"\n📝 [✓] تم تحديث الحفظ التلقائي! التشغيل القادم سيبدأ من السطر: {current_index}")
    print("🏁 انتهت مهمة الأتمتة الحالية بنجاح!")

if __name__ == '__main__':
    publish_all_products()
