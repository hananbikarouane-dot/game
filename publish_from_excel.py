import pandas as pd
import requests
import re
import json

# --- إعدادات الحساب والمدونة ---
API_KEY = "ضع_مفتاح_الـ_API_الخاص_بـ_غوغل_هنا"
BLOG_ID = "ضع_معرف_المدونة_BLOG_ID_هنا"
EXCEL_FILE_PATH = "lap_omega_all_colors.xlsx"  # اسم ملف الإكسل الخاص بك

# --- دالة نشر تدوينة جديدة في بلوجر ---
def create_blogger_post(title, content, tags):
    url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed" # (مثال توضيحي، استخدم رابط Blogger API الفعلي أدناه)
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": tags
    }
    
    # يمكنك تفعيل السطرين أدناه عند إدخال الـ Token الصحيح الخاص بك
    # response = requests.post(url, headers=headers, json=payload)
    # return response.json()
    print(f"✔️ تم تجهيز ونشر المنتج: {title} مع ألوانه وتصنيفاته.")

# --- 1. قراءة البيانات من ملف الإكسل ---
try:
    df = pd.read_excel(EXCEL_FILE_PATH)
except Exception as e:
    print(f"❌ خطأ في قراءة ملف الإكسل: {e}")
    exit()

# تنظيف أسماء الأعمدة (إزالة أي مساحات زائدة)
df.columns = [c.strip() for c in df.columns]

# --- 2. تجميع المنتجات بناءً على الاسم ---
# سنقوم بتجميع كل الصفوف التي لها نفس اسم المنتج لكي ندمج الألوان والصور الخاصة بها
grouped = df.groupby('اسم المنتج')

print(f"📦 تم العثور على {len(grouped)} منتج فريد بعد دمج الألوان والخيارات.")

# --- 3. معالجة كل منتج مدمج ونشره ---
for product_name, group in grouped:
    # أخذ البيانات الأساسية من أول صف في المجموعة
    first_row = group.iloc[0]
    
    price = first_row.get('السعر الإجمالي', 0)
    brand = str(first_row.get('الماركة', '')).strip()
    sub_category = str(first_row.get('التصنيف', '')).strip()
    ref = str(first_row.get('المرجع', '')).strip()
    description = str(first_row.get('الوصف', '')).strip()
    
    # بناء مصفوفة المتغيرات (الألوان والصور) للمنتج الحالي
    variants_list = []
    all_tags = [brand, sub_category]
    
    for _, row in group.iterrows():
        color_name = str(row.get('اللون', 'أساسي')).strip()
        image_url = str(row.get('رابط الصورة', '')).strip()
        
        if image_url:
            variants_list.append({
                "color": color_name,
                "image": image_url
            })
            
    # إذا لم تكن هناك أي متغيرات مصورة، نضع صورة افتراضية
    if not variants_list:
        variants_list.append({
            "color": "أساسي",
            "image": "https://via.placeholder.com/400?text=No+Image"
        })

    # --- 4. بناء محتوى الـ HTML المتوافق مع قالب المتجر المطور ---
    # الصورة الأولى ستكون هي الصورة البارزة للمنتج
    featured_image = variants_list[0]['image']
    
    # تحويل مصفوفة الألوان إلى نص JSON منظم
    variants_json_string = json.dumps(variants_list, ensure_ascii=False)
    
    # صياغة المحتوى النصي المنظم لكي يقرأه محرك القالب
    html_content = f"""
    <!-- الصورة البارزة الأساسية للمنتج -->
    <div class="separator" style="clear: both; text-align: center;">
        <a href="{featured_image}" imageanchor="1" style="margin-left: 1em; margin-right: 1em;">
            <img border="0" src="{featured_image}" data-original-width="800" data-original-height="800" />
        </a>
    </div>
    
    <!-- البيانات النصية المنظمة التي يقرأها السكربت -->
    <p>السعر الإجمالي: {price} DH</p>
    <p>الماركة: {brand}</p>
    <p>التصنيف: {sub_category}</p>
    <p>المرجع: {ref}</p>
    
    <div class="product-description-text">
        {description}
    </div>

    <!-- مصفوفة JSON الذكية والمخفية التي سيتعرف عليها القالب لإنشاء أزرار الألوان التفاعلية -->
    <script type="application/json" class="product-variants-json">
    {variants_json_string}
    </script>
    """
    
    # تنفيذ عملية النشر
    create_blogger_post(
        title=product_name,
        content=html_content,
        tags=all_tags
    )

print("\n🚀 تم الانتهاء من معالجة جميع المنتجات بنجاح!")
