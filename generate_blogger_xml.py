import pandas as pd
import html
from datetime import datetime

def create_blogger_import_xml(excel_file, output_xml_file):
    print("جاري قراءة ملف الإكسل: " + excel_file)
    
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print("خطأ في قراءة ملف الإكسل: " + str(e))
        return

    # الترويسة الرسمية المتوافقة تماماً مع معايير بلوجر لتجنب مشاكل الصلاحيات
    xml_header = "<?xml version='1.0' encoding='UTF-8'?>\n"
    xml_header = xml_header + "<feed xmlns='http://www.w3.org/2005/Atom'\n"
    xml_header = xml_header + "      xmlns:openSearch='http://a9.com/-/spec/opensearch/1.1/'\n"
    xml_header = xml_header + "      xmlns:gd='http://schemas.google.com/g/2005'\n"
    xml_header = xml_header + "      xmlns:thr='http://purl.org/syndication/thread/1.0'>\n"
    xml_header = xml_header + "  <generator version='7.00'>Blogger</generator>\n"
    xml_header = xml_header + "  <title type='text'>Blogger Import Feed</title>\n"

    xml_entries = ""
    
    default_price = "150" 
    default_category = "protection"

    print("جاري تحويل المنتجات بناءً على الهيكل القياسي...")
    
    for index, row in df.iterrows():
        title = str(row.get('اسم المنتج (Title)', 'منتج بدون اسم')).strip()
        color = str(row.get('اللون (Color)', 'أساسي')).strip()
        ref = str(row.get('المرجع (SKU / Ref)', 'غير متوفر')).strip()
        img_url = str(row.get('رابط الصورة (Image URL)', '')).strip()
        desc = str(row.get('الوصف والمواصفات (Description)', 'لا توجد تفاصيل إضافية.')).strip()
        
        full_title = title + " - " + color
        
        # تجهيز الكود الداخلي للمقال
        post_content = ""
        if img_url:
            post_content = post_content + "<img src='" + html.escape(img_url) + "' />\n"
        
        post_content = post_content + "<p>التصنيف: " + default_category + "</p>\n"
        post_content = post_content + "<p>الماركة: lap</p>\n"
        post_content = post_content + "<p>اللون: " + color + "</p>\n"
        post_content = post_content + "<p>المرجع: " + ref + "</p>\n"
        post_content = post_content + "<p>السعر الإجمالي: " + default_price + "</p>\n"
        post_content = post_content + "<p>" + html.escape(desc) + "</p>"

        # توليد معرف فريد وتاريخ بصيغة بلوجر الرسمية
        post_id = "tag:blogger.com,1999:blog-123456789.post-" + str(1000000000000000000 + index)
        now_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000-08:00')
        
        # هيكلة Entry مطابقة تماماً للملفات المصدرة من بلوجر
        entry = "  <entry>\n"
        entry = entry + "    <id>" + post_id + "</id>\n"
        entry = entry + "    <published>" + now_str + "</published>\n"
        entry = entry + "    <updated>" + now_str + "</updated>\n"
        entry = entry + "    <category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/blogger/2008/kind#post'/>\n"
        # إضافة تصنيف (Label) للمقال ليسهل عليك تصنيفه برمجياً
        entry = entry + "    <category scheme='http://www.blogger.com/atom/ns#' term='" + default_category + "'/>\n"
        entry = entry + "    <title type='text'>" + html.escape(full_title) + "</title>\n"
        entry = entry + "    <content type='html'>" + html.escape(post_content) + "</content>\n"
        # تحديد الكاتب الافتراضي لتجنب تعارض الصلاحيات
        entry = entry + "    <author>\n"
        entry = entry + "      <name>Admin</name>\n"
        entry = entry + "    </author>\n"
        # جعلها كمسودة (Draft) بشكل افتراضي للتحكم الآمن من لوحة التحكم
        entry = entry + "    <control xmlns='http://appspace.internal/atom-protocol'>\n"
        entry = entry + "      <draft>yes</draft>\n"
        entry = entry + "    </control>\n"
        entry = entry + "  </entry>\n"
        
        xml_entries = xml_entries + entry

    xml_footer = "</feed>\n"
    final_xml = xml_header + xml_entries + xml_footer
    
    try:
        with open(output_xml_file, "w", encoding="utf-8") as f:
            f.write(final_xml)
        print("🎉 تم إنشاء الملف بالصيغة القياسية بنجاح: " + output_xml_file)
    except Exception as save_err:
        print("خطأ أثناء الحفظ: " + str(save_err))

# تشغيل وتوليد الملف
create_blogger_import_xml("lap_omega_all_colors.xlsx", "blogger_import_lap_products.xml")
