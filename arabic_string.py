
from dataclasses import dataclass
import string


unicode_letters_norm = "ءابتثجحخدذرزسشصضطظعغفقكلمنهويّ"
unicode_letters = unicode_letters_norm + "أؤئةىآﻻإ"

# define digits
unicode_digits = "٠١٢٣٤٥٦٧٨٩"
ascii_digits = string.digits
digits = ascii_digits + unicode_digits

# define punctuation
unicode_punctuation = "٬٪٠۰٫،؛:“”–ـ…’«»؟" + '\u065c'
ascii_punctuation = string.punctuation
punctuation = ascii_punctuation + unicode_punctuation

# define accents
accents = "\u0618\u0619\u061a\u064b\u064c\u064d\u064e\u064f\u0650\u0652"

# define whitespace
whitespace = string.whitespace

# define printable
printable = unicode_letters + digits + \
    punctuation + accents + whitespace
