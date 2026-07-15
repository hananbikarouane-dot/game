import pandas as pd
import requests
import json
import os
import glob

# --- إعدادات الحساب والمدونة عبر البيئة المحمية (GitHub Actions Env) ---
BLOG_ID = os.environ.get("BLOG_ID", "ضع_معرف_المدونة_هنا")
BLOGGER_TOKEN = os.environ.get("BLOGGER_TOKEN") 

def find_excel_file():
    # يبحث عن ملف الإكسل الخاص بك في المجلد
    excel_files = glob.glob("*.xlsx") + glob.glob("*.xls")
    if excel_files:
        print(f"📂 تم العثور تلقائياً على ملف الإكسل: {excel_files[0]}")
        return excel_files[0]
    return "lap_omega_all_colors (2).xlsx"

EXCEL_FILE_PATH = find_excel_file()

# --- دالة نشر تدوينة جديدة في بلوجر ---
def create_blogger_post(title, content, tags):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {BLOGGER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": tags
    }
    
    if BLOGGER_TOKEN and BLOG_ID != "ضع_معرف_المدونة_هنا":
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print(f"✔️ تم نشر المنتج بنجاح: {title}")
        else:
            print(f"❌ خطأ أثناء النشر لـ {title}: {response.text}")
    else:
        print(f"⚠️ وضع التجربة: تم تجهيز المنتج بنجاح: {title}")

# --- 1. قراءة البيانات من ملف الإكسل ---
try:
    df = pd.read_excel(EXCEL_FILE_PATH)
except Exception as e:
    print(f"❌ خطأ في قراءة ملف الإكسل ({EXCEL_FILE_PATH}): {e}")
    exit()

# تنظيف أسماء الأعمدة من أي مسافات زائدة
df.columns = [str(c).strip() for c in df.columns]

# تحديد الأعمدة الصحيحة بناءً على ملفك المرفق
col_title = 'اسم المنتج (Title)'
col_color = 'اللون (Color)'
col_ref = 'المرجع (SKU / Ref)'
col_image = 'رابط الصورة (Image URL)'
col_desc = 'الوصف والمواصفات (Description)'

# --- 2. تجميع المنتجات بناءً على اسم المنتج ---
grouped = df.groupby(col_title)
print(f"📦 تم العثور على {len(grouped)} منتج فريد بعد دمج الألوان والخيارات.")

# --- 3. معالجة كل منتج مدمج ونشره ---
for product_name, group in grouped:
    if pd.isna(product_name) or str(product_name).strip() == "":
        continue
        
    first_row = group.iloc[0]
    
    # جلب البيانات الأساسية للمنتج
    ref = str(first_row.get(col_ref, '')).strip()
    description = str(first_row.get(col_desc, '')).strip()
    
    # بناء قائمة المتغيرات (الألوان والصور)
    variants_list = []
    
    for _, row in group.iterrows():
        color_name = str(row.get(col_color, 'أساسي')).strip()
        image_url = str(row.get(col_image, '')).strip()
        
        if image_url and not pd.isna(row.get(col_image)):
            variants_list.append({
                "color": color_name,
                "image": image_url
            })
            
    # إذا لم تكن هناك صور، نضع صورة افتراضية
    if not variants_list:
        variants_list.append({
            "color": "أساسي",
            "image": "https://via.placeholder.com/400?text=No+Image"
        })

    # الصورة الأولى ستكون هي الصورة الأساسية للتدوينة
    featured_image = variants_list[0]['image']
    
    # تحويل مصفوفة الألوان والصور إلى نص JSON منظم ليقرأه القالب
    variants_json_string = json.dumps(variants_list, ensure_ascii=False)
    
    # صياغة محتوى الـ HTML المتوافق مع قالب التدوينة المطور الخاص بك
    html_content = f"""
    <div class="separator" style="clear: both; text-align: center;">
        <a href="{featured_image}" imageanchor="1" style="margin-left: 1em; margin-right: 1em;">
            <img border="0" src="{featured_image}" data-original-width="800" data-original-height="800" />
        </a>
    </div>
    
    <p>المرجع: {ref}</p>
    
    <div class="product-description-text">
        {description}
    </div>

    <!-- مصفوفة JSON التي ستجعل أزرار الألوان تظهر وتغير الصور تفاعلياً -->
    <script type="application/json" class="product-variants-json">
    {variants_json_string}
    </script>
    """
    
    # استخدام المرجع (SKU) أو اسم عام كعلامة (Tag/Label) للتدوينة
    tags = ["أوميغا", ref] if ref else ["أوميغا"]
    
    create_blogger_post(
        title=str(product_name),
        content=html_content,
        tags=tags
    )

print("\n🚀 تم الانتهاء من معالجة ونشر جميع المنتجات بنجاح بالتوافق مع ملف الإكسل المرفق!")
