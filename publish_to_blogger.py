import pandas as pd
import requests
import html
import time

def publish_to_blogger_api(excel_file, api_key, blog_id):
    print("جاري قراءة ملف الإكسل وبدء النشر المباشر عبر الـ API...")
    
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print("خطأ في قراءة ملف الإكسل: " + str(e))
        return

    # رابط إرسال المقالات الافتراضي في جوجل API
    url = "https://www.googleapis.com/blogger/v3/blogs/" + blog_id + "/posts/"
    
    default_price = "150"
    default_category = "protection"

    for index, row in df.iterrows():
        title = str(row.get('اسم المنتج (Title)', 'منتج بدون اسم')).strip()
        color = str(row.get('اللون (Color)', 'أساسي')).strip()
        ref = str(row.get('المرجع (SKU / Ref)', 'غير متوفر')).strip()
        img_url = str(row.get('رابط الصورة (Image URL)', '')).strip()
        desc = str(row.get('الوصف والمواصفات (Description)', 'لا توجد تفاصيل إضافية.')).strip()
        
        full_title = title + " - " + color
        
        # تجهيز محتوى الـ HTML للمنتج بدمج النصوص التقليدي
        post_content = ""
        if img_url:
            post_content = post_content + "<img src='" + html.escape(img_url) + "' />\n"
        
        post_content = post_content + "<p>التصنيف: " + default_category + "</p>\n"
        post_content = post_content + "<p>الماركة: lap</p>\n"
        post_content = post_content + "<p>اللون: " + color + "</p>\n"
        post_content = post_content + "<p>المرجع: " + ref + "</p>\n"
        post_content = post_content + "<p>السعر الإجمالي: " + default_price + "</p>\n"
        post_content = post_content + "<p>" + html.escape(desc) + "</p>"

        # تجهيز البيانات المطلوبة لإرسالها لجوجل (ستنشر كمسودات Drafts للتحقق منها أولاً)
        payload = {
            "kind": "blogger#post",
            "title": full_title,
            "content": post_content,
            "status": "DRAFT",
            "labels": [default_category]
        }
        
        # إرسال الطلب لجوجل مع مفتاح الـ API
        params = {"key": api_key}
        
        print("جاري رفع المنتج: " + full_title)
        try:
            response = requests.post(url, json=payload, params=params)
            if response.status_code == 200 or response.status_code == 201:
                print("✅ تم رفع المنتج بنجاح كمسودة!")
            else:
                print("❌ فشل الرفع. كود الخطأ من جوجل: " + str(response.status_code))
                print(response.text)
        except Exception as req_err:
            print("حدث خطأ في الاتصال أثناء رفع المنتج: " + str(req_err))
            
        # إيقاف مؤقت لمدة ثانية بين كل منتج لتفادي حظر الحماية (Spam)
        time.sleep(1)

# ==========================================
# إعدادات التشغيل (إذا كنت تشغله يدوياً من جهازك)
# ==========================================
# استبدل هذه القيم ببياناتك الحقيقية إذا أردت تشغيله محلياً:
# API_KEY = "AIzaSyCLsThQ6oqrVQ47Xv8_upLHY2WtXDCPqkc"
# BLOG_ID = "ضع_رقم_مدونتك_هنا"
# publish_to_blogger_api("lap_omega_all_colors.xlsx", API_KEY, BLOG_ID)
