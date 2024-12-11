import google.generativeai as genai

def createor():
    try:
        genai.configure(api_key="AIzaSyCEVrQ9LA0LM9qMgxKfj8ZzJE2Ktmu7K6I")
        model = genai.GenerativeModel("gemini-1.5-flash")
        content = f"""لطفا این مقاله رو به شکل خیلی خوب و با جزيیات بررسی کن و برداشت هات رو به شکل زبان عامیانه فارسی به‌طور کامل شرح بده بطور علمی و دقیق با فرمولها و دلایل حرفه‌ای و دقیقا توضیح بده این مقاله رو.

    مقاله راجب مهندسی  پزشکی
    دقت کن حدود 8 تا 12 خط باشه توضیحاتت
    لطفا انتهای پست هم رفرنس بزار 
    """
        response = model.generate_content(content)
        # text_ai = response.replace("#", "")
        print(response)
    

    except Exception as e:
        print(f"ERROR   :   {e}")


createor()