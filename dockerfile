# ۱. انتخاب ایمیج پایه سبک
FROM python:3.11-slim AS base  # انتخاب تگ مشخص برای ثبات نسخه پایتون 6

# ۲. ست کردن دایرکتوری کاری
WORKDIR /app

# ۳. کپی کردن فایل‌های وابستگی
COPY requirements.txt .

# ۴. نصب وابستگی‌ها و استفاده از کش برای pip
RUN pip install --no-cache-dir -r requirements.txt  # کاهش لایه‌ها و حجم نهایی 7

# ۵. کپی کردن باقی سورس‌کد
COPY . .

# ۶. تعریف کاربر غیر‌ریزروت برای امنیت بیشتر
RUN adduser --system --no-create-home botuser && chown -R botuser:botuser /app
USER botuser  # اجرا با کاربر غیر‌ریزروت 8

# ۷. متغیر محیطی فایل .env را بارگذاری می‌کنیم
ENV PYTHONUNBUFFERED=1

# ۸. دستور پیش‌فرض برای اجرا
ENTRYPOINT ["python", "bot.py"]