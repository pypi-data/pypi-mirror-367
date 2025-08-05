# `limipy` – The LimiPlake Python Package

Welcome to **limipy**, the official Python package from **LimiPlake**!  
This package is made for **students** and **teachers** learning computer science and programming in fun and easy levels.

🌐 Visit [limiplake.com](https://limiplake.com) to learn more.

---

## 🚀 Features

- 🔐 Ask for PIN codes (student or teacher)
- 📚 Show descriptions of LimiPlake levels (ScratchJr to Web Dev!)
- 🧠 Fun mini-quizzes for each level
- 🎓 Create PINs for students
- 🏫 Make class lists with student names and their PINs

---

## 🧪 Levels Available

```
1. ScratchJr
2. Scratch
3. Logo
4. Python
5. Grodemate
6. AppLab (Code.org)
7. HTML, CSS, JS (Web Dev)
```

## 📦 How to Install

```
pip install limipy
```

## ✨ Example Usage

```
import limipy

limipy.ask_PIN()
print(limipy.get_README_level_description(3))
limipy.level_quiz(4)

students = ["Avi", "Vihaan", "Arrya"]
print(limipy.create_class_list(students))
```
