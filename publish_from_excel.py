import os
import json
import time
import random
import glob
import base64
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
    
    # تجميع البيانات بناءً على "المرجع (SKU / Ref)"
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
        
        main_image = bypass_hotlink(first_row['رابط الصورة (Image URL)'])
        
        brand = "lap"           
        category = "commande"   
        price = "150"           
        
        # استخراج قائمة الألوان والروابط
        all_colors = []
        variants_data = []
        
        for _, row in product_group.iterrows():
            c_name = str(row['اللون (Color)']).strip()
            c_url = str(row['رابط الصورة (Image URL)']).strip()
            if c_name and c_name not in all_colors:
                all_colors.append(c_name)
                variants_data.append({
                    "color": c_name,
                    "image": bypass_hotlink(c_url)
                })
        
        # كود الجافا سكريبت النقي والمضغوط لتفعيل الضغط على الأزرار
        raw_js = f"""
        (function() {{
            var refId = "{ref_id}";
            var btns = document.querySelectorAll('.color-btn-' + refId);
            var img = document.getElementById('main-product-img-' + refId);
            var txt = document.getElementById('current-color-text-' + refId);
            if(btns.length > 0) {{
                btns[0].style.borderColor = "#ff8c00";
                btns[0].style.backgroundColor = "#fff9f2";
            }}
            btns.forEach(function(b) {{
                b.addEventListener('click', function() {{
                    var tImg = this.getAttribute('data-image');
                    var tCol = this.getAttribute('data-color');
                    if(img && tImg) img.src = tImg;
                    if(txt) txt.innerText = tCol;
                    btns.forEach(function(x) {{
                        x.style.borderColor = "#ccc";
                        x.style.backgroundColor = "#fff";
                    }});
                    this.style.borderColor = "#ff8c00";
                    this.style.backgroundColor = "#fff9f2";
                }});
            }});
        }})();
        """
        
        b64_js = base64.b64encode(raw_js.encode('utf-8')).decode('utf-8')

        # بناء التصميم الجديد النظيف: حذفنا كل النصوص المكررة والعشوائية تماماً لمنع تشويه القالب
        post_content = f"""<div class="product-container" style="text-align: right; direction: rtl; font-family: sans-serif; padding: 10px;">
        
    <!-- صورة المنتج الرئيسية -->
    <div class="product-main-image-wrapper" style="text-align: center; margin-bottom: 20px;">
        <img id="main-product-img-{ref_id}" src="{main_image}" alt="{product_title}" style="max-width:100%; max-height: 350px; object-fit: contain; border-radius: 8px; border: 1px solid #eee; padding: 5px;" />
    </div>

    <!-- تفاصيل المنتج الأساسية المنظمة -->
    <div class="product-meta-data" style="margin-bottom: 15px; font-size: 14px; color: #333; line-height: 1.8;">
        <p style="margin: 5px 0;"><strong>المرجع (Ref):</strong> {ref_id}</p>
        <p style="margin: 5px 0;"><strong>السعر الإجمالي:</strong> <span style="font-size: 18px; color: #ff8c00; font-weight: bold;">{price} DH</span></p>
        <p style="margin: 5px 0;"><strong>اللون المختار:</strong> <span id="current-color-text-{ref_id}" style="font-weight: bold; color: #555;">{all_colors[0] if all_colors else ''}</span></p>
    </div>

    <!-- أزرار اختيار الألوان التفاعلية والنظيفة تماماً -->
    <div class="color-variants-selector" style="display: flex; gap: 8px; flex-wrap: wrap; margin: 15px 0;">
        {"".join([f'<button type="button" class="color-btn-{ref_id}" data-color="{v["color"]}" data-image="{v["image"]}" style="padding: 6px 14px; border: 1px solid #ccc; background: #fff; cursor: pointer; border-radius: 4px; font-size: 13px; font-weight: 600; transition: all 0.2s; outline: none;">{v["color"]}</button>' for v in variants_data])}
    </div>

    <hr style="border: 0; border-top: 1px solid #f5f5f5; margin: 15px 0;" />
    
    <!-- الوصف والمواصفات الكاملة -->
    <div class="product-description" style="line-height: 1.6; color: #666; font-size: 14px;">
        <p>{desc}</p>
    </div>

    <!-- تشغيل السكربت من خلال حدث onerror للصورة الشفافة لتجنب طباعته كنص نهائياً -->
    <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" onerror="eval(atob('{b64_js}')); this.parentNode.removeChild(this);" style="display:none !important;" />
</div>
"""

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
            print(f"✅ Published: {product_title} successfully with clean layout.")
            count += 1
            
        except Exception as e:
            print(f"❌ Error publishing {product_title}: {e}")
            
        current_index += 1

    with open(INDEX_FILE_PATH, 'w') as f:
        f.write(str(current_index))
    print(f"📝 تم حفظ مؤشر التوقف عند المنتج رقم: {current_index}")

if __name__ == '__main__':
    publish_combined_products()
