ur_pyfile = open("سامپل۔پے")

language_dict = {
    "۔":          ".",
    "،":          ",",
    "۱":          "1",
    "۲":          "2",
    "۳":          "3",
    "۴":          "4",
    "۵":          "5",
    "۶":          "6",
    "۷":          "7",
    "۸":          "8",
    "۹":          "9",
    "۰":          "0",
    "لکھو":       "print",
    "ورنہ اگر":   "elif",
    "اگر":        "if",
    "ورنہ":       "else",
    "جبتک":       "while",
    "جو":         "for",
    "اندر":       "in", 
    "داخلہ":      "input",
    "توڑ":        "break",
    "جاری":       "continue",
    "گزر":        "pass",
    "حق":         "True",
    "باطل":       "False",
    "ہے":         "is",
    "طبقہ":       "class",
    "وضح":        "def",
    "ابتدا":      "init",
    "خود":        "self",
    "واپس":       "return",
    "ستلی":       "string",
    "ستل":        "str",
    "شامل":       "append",
    "نکل":        "pop",
    "اور":        "and",
    "یا":         "or",    
    "سب":         "all",
    "کوئ":        "any",
    "ندارد":      "None",    
}

words = ur_pyfile.read()

for key, value in language_dict.items():
    words = words.replace(key, value)
    words = re.sub(p, subst, words)

eng_pyfile = open("eng.py", "wt")
n = eng_pyfile.write(words)
eng_pyfile.close()

import eng

import os
if os.path.exists("eng.py"):
  os.remove("eng.py")
else:
  print("The file does not exist")