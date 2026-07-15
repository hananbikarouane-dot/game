import os
import json
import time
import random
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']
EXCEL_FILE_PATH = 'lap_omega_all_colors (2).xlsx'
INDEX_FILE_PATH = 'last_product_index.txt'

def get_blogger_service():
    token_str = os.environ.get('BLOGGER_TOKEN')
    if not token_str:
        raise ValueError("❌ BLOGGER_TOKEN not found in GitHub Secrets!")
    
    creds_info = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("[~] التوكن منتهي... جاري التجديد تلقائياً...")
            try:
                creds.refresh(Request())
            except Exception as e:
                raise Exception(f"❌ فشل تجديد التوكن: {e}")
        else:
            raise Exception("❌ التوكن غير صالح.")
            
    return build('blogger', 'v3', credentials=creds)

def publish_combined_products():
    blog_id = os.environ.get('BLOG_ID')
    if not blog_id:
        raise ValueError("❌ BLOG_ID not found in GitHub Secrets!")
        
    if not os.path.exists(EXCEL_FILE_PATH):
        raise FileNotFoundError(f"❌ لم يتم العثور على الملف: {EXCEL_FILE_PATH}")
        
    df = pd.read_excel(EXCEL_FILE_PATH)
    
    # تجميع البيانات بناءً على "المرجع (SKU / Ref)" لدمج الألوان
    grouped = df.groupby('المرجع (SKU / Ref)')
    unique_refs = list(grouped.groups.keys())
    
    start_index = 0
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as f:
            try:
                start_index = int(f.read().strip())
                print(f"[✓] سنبدأ من المنتج الفريد رقم: {start_index}")
            except:
                start_index = 0

    if start_index >= len(unique_refs):
        print("[✓] تم نشر جميع المنتجات المجمعة بنجاح! إعادة التعيين...")
        start_index = 0
        
    service = get_blogger_service()
    
    # نشر منتج رئيسي واحد (يحتوي على كل ألوانه) في كل تشغيل لحماية الحساب من الحظر
    max_publish_count = 1  
    count = 0  
    current_index = start_index

    while count < max_publish_count and current_index < len(unique_refs):
        ref_id = unique_refs[current_index]
        product_group = grouped.get_group(ref_id)
        
        # أخذ معلومات المنتج الأساسية من السطر الأول للمجموعة
        first_row = product_group.iloc[0]
        product_title = first_row['اسم المنتج (Title)']
        desc = first_row['الوصف والمواصفات (Description)']
        main_image = first_row['رابط الصورة (Image URL)'] # الصورة الأساسية للمنتج
        
        brand = "lap"           
        category = "commande"   
        price = "150"           
        
        # 🎨 إنشاء كود استعراض الألوان والصور المتعددة داخل المقال
        color_variants_html = '<div class="product-colors-gallery" style="margin-top:20px; display:grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap:10px;">'
        
        all_colors_list = []
        for _, row in product_group.iterrows():
            c_name = row['اللون (Color)']
            c_img = row['رابط الصورة (Image URL)']
            all_colors_list.append(c_name)
            
            # إضافة الصورة مصغرة مع اسم اللون تحتها لتظهر كخيارات داخل المنتج
            color_variants_html += f"""
            <div style="text-align:center; border:1px solid #eee; padding:5px; border-radius:5px;">
                <img src="{c_img}" alt="{c_name}" style="width:80px; height:80px; object-fit:contain;" />
                <span style="font-size:12px; display:block; color:#555;">{c_name}</span>
            </div>
            """
        color_variants_html += '</div>'
        
        colors_str = ", ".join(all_colors_list)

        # 🌟 صياغة المحتوى النهائي متوافق مع القالب + يحتوي على كل صور الألوان مجتمعة
        post_content = f"""<div style="text-align: right; direction: rtl;">
<img src="{main_image}" alt="{product_title}" style="max-width:100%; display:block; margin-bottom: 15px;" />
<p>السعر الإجمالي: {price}</p>
<p>الماركة: {brand}</p>
<p>التصنيف: {category}</p>
<p>المرجع: {ref_id}</p>
<p>الألوان المتوفرة: {colors_str}</p>
<hr />
<h4 style="color:#c00;">تصفح صور الألوان المتوفرة لهذا المنتج:</h4>
{color_variants_html}
<hr />
<div class="product-description">
    <p>{desc}</p>
</div>
</div>"""

        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': blog_id},
            'title': f"{product_title} - RÉF: {ref_id}",
            'content': post_content,
            'labels': [category, brand]
        }
        
        try:
            request = service.posts().insert(blogId=blog_id, body=post_body, isDraft=False)
            request.execute()
            print(f"✅ Published Combined Product: {product_title} (Contains {len(product_group)} colors)")
            count += 1
            
        except Exception as e:
            print(f"❌ Error publishing {product_title}: {e}")
            
        current_index += 1

    with open(INDEX_FILE_PATH, 'w') as f:
        f.write(str(current_index))
    print(f"📝 تم حفظ مؤشر التوقف عند المنتج الفريد: {current_index}")

if __name__ == '__main__':
    publish_combined_products()
