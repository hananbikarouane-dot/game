import pandas as pd
import html
from datetime import datetime

def create_blogger_import_xml(excel_file, output_xml_file):
    print("جاري قراءة ملف الإكسل: " + excel_file)
    
    try:
        # قراءة البيانات من ملف الإكسل
        df = pd.read_excel(excel_file)
    except Exception as e:
        print("خطأ في قراءة ملف الإكسل. تأكد من وجوده في نفس المجلد: " + str(e))
        return

    # بداية هيكل ملف Blogger XML
    xml_header = "<?xml version='1.0' encoding='UTF-8'?>\n"
    xml_header = xml_header + "<feed xmlns='http://www.w3.org/2005/Atom'\n"
    xml_header = xml_header + "      xmlns:openSearch='http://a9.com/-/spec/opensearch/1.1/'\n"
    xml_header = xml_header + "      xmlns:gd='http://schemas.google.com/g/2005'\n"
    xml_header = xml_header + "      xmlns:thr='http://purl.org/syndication/thread/1.0'>\n"
    xml_header = xml_header + "  <title type='text'>Blogger Import Feed</title>\n"

    xml_entries = ""
    
    # تصنيف افتراضي وسعر افتراضي (يمكنك تعديل السعر يدوياً في الإكسل أو داخل بلوجر لاحقاً)
    default_price = "150" 
    default_category = "protection" # تصنيف افتراضي (يمكنك تغييره إلى: commande, automatisation, énergie)

    print("جاري تحويل المنتجات إلى صيغة XML...")
    
    for index, row in df.iterrows():
        # استخراج البيانات وتجهيزها بأمان مع تفادي القيم الفارغة (NaN)
        title = str(row.get('اسم المنتج (Title)', 'منتج بدون اسم')).strip()
        color = str(row.get('اللون (Color)', 'أساسي')).strip()
        ref = str(row.get('المرجع (SKU / Ref)', 'غير متوفر')).strip()
        img_url = str(row.get('رابط الصورة (Image URL)', '')).strip()
        desc = str(row.get('الوصف والمواصفات (Description)', 'لا توجد تفاصيل إضافية.')).strip()
        
        # دمج اسم المنتج مع اللون ليكون العنوان واضحاً في لوحة التحكم
        full_title = title + " - " + color
        
        # تجهيز محتوى المقال الداخلي متوافقاً مع قارئ البيانات في القالب الجديد
        # تم استخدام الـ HTML لترتيب البيانات التي يبحث عنها المتجر
        post_content = ""
        if img_url:
            post_content = post_content + "<img src='" + html.escape(img_url) + "' />\n"
        
        post_content = post_content + "<p>التصنيف: " + default_category + "</p>\n"
        post_content = post_content + "<p>الماركة: lap</p>\n"
        post_content = post_content + "<p>اللون: " + color + "</p>\n"
        post_content = post_content + "<p>المرجع: " + ref + "</p>\n"
        post_content = post_content + "<p>السعر الإجمالي: " + default_price + "</p>\n"
        post_content = post_content + "<p>" + html.escape(desc) + "</p>"

        # تاريخ ووقت النشر الحالي بصيغة Blogger المقبولة
        now_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # إنشاء الـ Entry الخاص بالمنتج في ملف الـ XML
        # تم ضبط الحالة كـ DRAFT (مسودة) حتى تراجع الأسعار والتصنيفات قبل نشرها للعلن دفعة واحدة
        entry = "  <entry>\n"
        entry = entry + "    <category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/blogger/2008/kind#post'/>\n"
        entry = entry + "    <title type='text'>" + html.escape(full_title) + "</title>\n"
        entry = entry + "    <content type='html'>" + html.escape(post_content) + "</content>\n"
        entry = entry + "    <published>" + now_str + "</published>\n"
        # لتنزيل المنتجات مباشرة كـ "مسودات" لمراجعتها:
        entry = entry + "    <control xmlns='http://appspace.internal/atom-protocol'><draft>yes</draft></control>\n"
        entry = entry + "  </entry>\n"
        
        xml_entries = xml_entries + entry

    xml_footer = "</feed>\n"
    
    # دمج وحفظ الملف النهائي
    final_xml = xml_header + xml_entries + xml_footer
    
    try:
        with open(output_xml_file, "w", encoding="utf-8") as f:
            f.write(final_xml)
        print("==================================================================")
        print("🎉 تم توليد ملف الاستيراد بنجاح!")
        print("اسم الملف الناتج: " + output_xml_file)
        print("عدد المنتجات الجاهزة للرفع: " + str(len(df)))
        print("==================================================================")
    except Exception as save_err:
        print("حدث خطأ أثناء حفظ ملف الـ XML: " + str(save_err))

# تشغيل السكربت لتحويل ملف إكسل الذي تم استخراجه لـ LAP
create_blogger_import_xml("lap_omega_all_colors.xlsx", "blogger_import_lap_products.xml")
