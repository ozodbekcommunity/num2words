from fastapi import FastAPI, Query, HTTPException

app = FastAPI(
    title="Number to Words API",
    description="Juda katta sonlarni ham o'zbek, rus va ingliz tillarida so'zga o'girib beruvchi mukammal API.",
    version="1.0.0"
)

# ==========================================
# 1. LUG'ATLAR VA QOIDALAR (Dictionaries)
# ==========================================

# --- O'zbek tili lug'ati ---
uz_units = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
uz_tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
uz_scales = [
    "", "ming", "million", "milliard", "trillion", "kvadrillion", "kvintillion",
    "sekstillion", "septillion", "oktillion", "nonillion", "detsillion"
]

# --- Ingliz tili lug'ati ---
en_units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", 
            "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", 
            "seventeen", "eighteen", "nineteen"]
en_tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
en_scales = [
    "", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion",
    "sextillion", "septillion", "octillion", "nonillion", "decillion"
]

# --- Rus tili lug'ati ---
ru_units_m = ["", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
ru_units_f = ["", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
ru_teens = ["десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", 
            "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"]
ru_tens = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто"]
ru_hundreds = ["", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот"]

# Rus tili uchun guruhlarning birlik va ko'plik shakllari (1, 2-4, 5-0) va jinsi (m/f)
ru_scales = [
    ("", "", "", "m"),
    ("тысяча", "тысячи", "тысяч", "f"),
    ("миллион", "миллиона", "миллионов", "m"),
    ("миллиард", "миллиарда", "миллиардов", "m"),
    ("триллион", "триллиона", "триллионов", "m"),
    ("квадриллион", "квадриллиона", "квадриллионов", "m"),
    ("квинтиллион", "квинтиллиона", "квинтиллионов", "m"),
    ("секстиллион", "секстиллиона", "секстиллионов", "m"),
    ("септиллион", "септиллиона", "септиллионов", "m"),
    ("октиллион", "октиллиона", "октиллионов", "m"),
    ("нониллион", "нониллиона", "нониллионов", "m"),
    ("дециллион", "дециллиона", "дециллионов", "m")
]

# ==========================================
# 2. PARSER FUNKSIYALARI (Har 3 xonali son uchun)
# ==========================================

def uzbek_999(n: int) -> str:
    res = []
    h, rem = divmod(n, 100)
    if h > 0:
        if h == 1:
            res.append("bir yuz")
        else:
            res.append(f"{uz_units[h]} yuz")
    
    t, u = divmod(rem, 10)
    if t > 0: res.append(uz_tens[t])
    if u > 0: res.append(uz_units[u])
    return " ".join(res)

def english_999(n: int) -> str:
    res = []
    h, rem = divmod(n, 100)
    if h > 0:
        res.append(f"{en_units[h]} hundred")
    if rem > 0:
        if rem < 20:
            res.append(en_units[rem])
        else:
            t, u = divmod(rem, 10)
            if u > 0:
                res.append(f"{en_tens[t]}-{en_units[u]}")
            else:
                res.append(en_tens[t])
    return " ".join(res)

def russian_999(n: int, gender: str = "m") -> str:
    res = []
    h, rem = divmod(n, 100)
    if h > 0:
        res.append(ru_hundreds[h])
    if rem > 0:
        if rem < 10:
            units = ru_units_f if gender == "f" else ru_units_m
            res.append(units[rem])
        elif rem < 20:
            res.append(ru_teens[rem - 10])
        else:
            t, u = divmod(rem, 10)
            res.append(ru_tens[t])
            if u > 0:
                units = ru_units_f if gender == "f" else ru_units_m
                res.append(units[u])
    return " ".join(res)

def get_ru_plural(n: int, forms: tuple) -> str:
    if n % 100 in [11, 12, 13, 14]:
        return forms[2]
    last_digit = n % 10
    if last_digit == 1:
        return forms[0]
    elif last_digit in [2, 3, 4]:
        return forms[1]
    else:
        return forms[2]

# ==========================================
# 3. ASOSIY KONVERTER FUNKSIYA
# ==========================================

def convert_number_to_words(num: int, lang: str) -> str:
    if num == 0:
        return {"uz": "Nol", "en": "Zero", "ru": "Ноль"}.get(lang, "0")

    is_negative = num < 0
    num = abs(num)

    chunks = []
    while num > 0:
        chunks.append(num % 1000)
        num //= 1000

    if len(chunks) > len(uz_scales):
        raise ValueError("Kiritilgan son juda katta, chegaradan chiqib ketdi!")

    words = []
    for i, chunk in enumerate(chunks):
        if chunk == 0:
            continue

        if lang == "uz":
            chunk_str = uzbek_999(chunk)
            scale = uz_scales[i] if i < len(uz_scales) else ""
            if scale: chunk_str += " " + scale
            words.append(chunk_str)

        elif lang == "en":
            chunk_str = english_999(chunk)
            scale = en_scales[i] if i < len(en_scales) else ""
            if scale: chunk_str += " " + scale
            words.append(chunk_str)

        elif lang == "ru":
            scale_info = ru_scales[i] if i < len(ru_scales) else ("", "", "", "m")
            gender = scale_info[3]
            chunk_str = russian_999(chunk, gender)
            if i > 0:
                scale_word = get_ru_plural(chunk, scale_info[0:3])
                if scale_word:
                    chunk_str += " " + scale_word
            words.append(chunk_str)

    words.reverse()
    result = " ".join(words).strip()
    
    # Ortiqcha bo'sh joylarni tozalash
    result = " ".join(result.split())

    if is_negative:
        neg_word = {"uz": "minus", "en": "minus", "ru": "минус"}.get(lang, "-")
        result = f"{neg_word} {result}"

    # Birinchi harfni katta qilish
    if result:
        result = result[0].upper() + result[1:]

    return result

# ==========================================
# 4. FASTAPI ENDPOINT (API yo'li)
# ==========================================

@app.get("/")
async def home():
    return {
        "status": "Num2Words API is successfully working..."
    }

@app.get("/n2w")
async def get_number_to_words(
    num: str = Query(..., description="O'girilishi kerak bo'lgan son (butun son, musbat yoki manfiy)"),
    lang: str = Query("uz", regex="^(uz|ru|en)$", description="Tilni tanlang: uz, ru, en")
):
    try:
        # Son probellar yoki vergullar orqali yozilgan bo'lsa tozalaymiz
        clean_num = num.replace(",", "").replace(" ", "").replace("_", "")
        integer_num = int(clean_num)
    except ValueError:
        raise HTTPException(status_code=400, detail="Xatolik: Faqat butun son kiritish mumkin!")

    try:
        result = convert_number_to_words(integer_num, lang)
        return {
            "number": integer_num,
            "language": lang,
            "text": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
