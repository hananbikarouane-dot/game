import os
import json
import time
import random
import glob
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']
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

def find_excel_file():
    excel_files = glob.glob("lap_omega*.xlsx")
    if not excel_files:
        excel_files = glob.glob("**/lap_omega*.xlsx", recursive=True)
    if excel_files:
        print(f"[✓] تم العثور على ملف البيانات: {excel_files[0]}")
        return excel_files[0]
    return None

def bypass_hotlink(url):
    """تعديل رابط الصورة ليمر عبر خادم وسيط يكسر حظر الـ Hotlinking"""
    if not isinstance(url, str):
        return ""
    clean_url = url.replace("https://", "").replace("http://", "")
    return f"https://images.weserv.nl/?url={clean_url}"

def publish_combined_products():
    blog_id = os.environ.get('BLOG_ID')
    if not blog_id:
        raise ValueError("❌ BLOG_ID not found in GitHub Secrets!")
        
    excel_file_path = find_excel_file()
    if not excel_file_path:
        raise FileNotFoundError("❌ لم يتم العثور على أي ملف إكسيل في المستودع!")
        
    df = pd.read_excel(excel_file_path)
    
    # تجميع البيانات بناءً على "المرجع (SKU / Ref)" لدمج الألوان في منتج واحد
    grouped = df.groupby('المرجع (SKU / Ref)')
    unique_refs = list(grouped.groups.keys())
    
    start_index = 0
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'r') as f:
            try:
                start_index = int(f.read().strip())
                print(f"[✓] سنبدأ من المنتج رقم: {start_index}")
            except:
                start_index = 0

    if start_index >= len(unique_refs):
        print("[✓] تم نشر جميع المنتجات المجمعة بنجاح! إعادة التعيين...")
        start_index = 0
        
    service = get_blogger_service()
    
    max_publish_count = 1  
    count = 0  
    current_index = start_index

    while count < max_publish_count and current_index < len(unique_refs):
        ref_id = unique_refs[current_index]
        product_group = grouped.get_group(ref_id)
        
        first_row = product_group.iloc[0]
        product_title = first_row['اسم المنتج (Title)']
        desc = first_row['الوصف والمواصفات (Description)']
        
        # كسر حظر الصورة البارزة الأساسية
        main_image = bypass_hotlink(first_row['رابط الصورة (Image URL)'])
        
        brand = "lap"           
        category = "commande"   
        price = "150"           
        
        # تجميع أسماء الألوان من كل السطور المرتبطة بالمرجع وفصلها بفواصل كما يتوقع القالب
        all_colors_list = []
        for _, row in product_group.iterrows():
            c_name = str(row['اللون (Color)']).strip()
            if c_name and c_name not in all_colors_list:
                all_colors_list.append(c_name)
        
        colors_str = ", ".join(all_colors_list)

        # 🌟 الصياغة النصية الدقيقة والمطابقة لـ Regex الخاص بالقالب
        # تركنا سطر "اللون:" نظيفاً ومفصولاً بفواصل ليقوم قالبك ببناء المربعات تلقائياً
        post_content = f"""<div style="text-align: right; direction: rtl;">
<img src="{main_image}" alt="{product_title}" style="max-width:100%; display:block; margin-bottom: 20px; border-radius: 8px;" />
<p>السعر الإجمالي: {price}</p>
<p>الماركة: {brand}</p>
<p>التصنيف: {category}</p>
<p>اللون: {colors_str}</p>
<p>المرجع: {ref_id}</p>
<hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
<div class="product-description" style="line-height: 1.6; color: #555;">
    <p>{desc}</p>
</div>
</div>"""

        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': blog_id},
            'title': f"{product_title}",
            'content': post_content,
            'labels': [category, brand]
        }
        
        try:
            request = service.posts().insert(blogId=blog_id, body=post_body, isDraft=False)
            request.execute()
            print(f"✅ Published Combined Product: {product_title} (RÉF: {ref_id})")
            count += 1
            
        except Exception as e:
            print(f"❌ Error publishing {product_title}: {e}")
            
        current_index += 1

    with open(INDEX_FILE_PATH, 'w') as f:
        f.write(str(current_index))
    print(f"📝 تم حفظ مؤشر التوقف الحالي عند الحساب الفريد: {current_index}")

if __name__ == '__main__':
    publish_combined_products()
