import os
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# استخدام النطاق الكامل والصحيح
SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_blogger_service():
    token_str = os.environ.get('BLOGGER_TOKEN')
    if not token_str:
        raise ValueError("❌ BLOGGER_TOKEN not found in environment!")
    
    creds_info = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    return build('blogger', 'v3', credentials=creds)

def publish_all_products():
    blog_id = os.environ.get('BLOG_ID')
    if not blog_id:
        raise ValueError("❌ BLOG_ID not found in environment!")
        
    service = get_blogger_service()
    
    excel_file = "lap_omega_all_colors.xlsx"
    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"❌ File {excel_file} not found!")
        
    df = pd.read_excel(excel_file)
    print(f"📊 Found {len(df)} products. Processing...")
    
    for index, row in df.iterrows():
        title = row['اسم المنتج (Title)']
        color = row['اللون (Color)']
        ref = str(row['المرجع (SKU / Ref)'])
        img_url = row['رابط الصورة (Image URL)']
        desc = row['الوصف والمواصفات (Description)']
        
        brand = "LAP"  
        category = "protection"  
        price = "150"  
        
        post_content = f"""<div style="text-align: right; direction: rtl;">
<img src="{img_url}" alt="{title}" style="max-width:100%; display:none;" />

<p>السعر الإجمالي: {price}</p>
<p>الماركة: {brand}</p>
<p>التصنيف: {category}</p>
<p>اللون: {color}</p>
<p>المرجع: {ref}</p>

<hr />
<p>{desc}</p>
</div>"""

        # تعديل بنيوي: إرسال حالة المنشور كـ DRAFT داخل الـ body مباشرة
        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': blog_id},
            'title': f"{title} - {color}",
            'content': post_content,
            'status': 'DRAFT'  # 👈 تحديد الحالة هنا يمنع تعارض الصلاحيات
        }
        
        try:
            # نقوم بالاستدعاء بدون تمرير معامل isDraft في الرابط لتجنب تعارض الـ API
            request = service.posts().insert(blogId=blog_id, body=post_body)
            request.execute()
            print(f"✅ Created draft: {title} ({color})")
        except Exception as e:
            print(f"❌ Error publishing {title}: {e}")

if __name__ == '__main__':
    publish_all_products()
