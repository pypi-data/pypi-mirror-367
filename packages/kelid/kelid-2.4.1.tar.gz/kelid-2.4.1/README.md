# 🔐 Kelid

**Kelid** (کلید) یک لایبرری پایتونی ساده و سبک برای قفل‌کردن (رمزگذاری) کدهای Python با استفاده از `marshal` و `base64` است.  
با این ابزار می‌تونی کد‌هاتو encode کنی.

---

## ⚙️ نصب

نصب:

```bash
pip install kelid
```

---

## 🚀 استفاده سریع

### 1. رمزگذاری فایل پایتون

```bash
kelid encode myscript.py -o locked.txt
```

> فایل `myscript.py` رو رمزگذاری می‌کنه و نتیجه‌ی base64 رو داخل `locked.txt` ذخیره می‌کنه.

### 2. اجرای کد رمزگذاری شده

```bash
kelid run "cHJpbnQoJ1NhbGFtIGRvc3QhJyk="  # نمونه بیس64 از print("سلام دوست!")
```

> کد base64 رمز شده رو می‌گیره، decode و اجرا می‌کنه.

---

## 📦 مثال

### 📄 `example.py`

```python
print("سلام! این کد رمزگذاری شده بود 🗝️")
```

### 🔐 رمزگذاری:

```bash
kelid encode example.py -o encoded.txt
```

### 🚀 اجرا:

```bash
kelid run "$(cat encoded.txt)"
```

---

## 🛡️ هشدار امنیتی

این روش فقط برای جلوگیری از دیدن مستقیم سورس‌کد مناسبه و **امنیت واقعی نیست**.  
کسی که به سیستم شما یا توکن شما دسترسی داره، می‌تونه کد رمز شده رو بازیابی کنه.  
برای امنیت بالا از ابزارهایی مثل [PyArmor](https://github.com/dashingsoft/pyarmor) یا [Nuitka](https://nuitka.net/) استفاده کن.

---

## 🧑‍💻 نویسنده

- **Name:** Ali Jafari  
- **Email:** thealiapi@gmail.com
- **GitHub:** [yourusername](https://github.com/iTs-GoJo)
