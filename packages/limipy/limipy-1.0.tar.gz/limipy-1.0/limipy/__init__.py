print("LimiPlake: package.See limiplake website at limiplake.com\n")
print("Thank you for using limipy. \nSTUDENT OR TEACHERS At LIMIPLAKE")
def ask_PIN():
    while True:
        pin = input("/npin> ")
        lenpn = len(pin)
        if lenpn == 6:
            print("Teacher/staff/employee pin found.")
            break
        elif lenpn == 4:
            print("Student pin found.")
            break
        else:
            print("""
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            ValidationError: invalid LimiPlake PIN length""")


def get_README_level_description(level):
    description = """"""
    lvl = str(level)
    if lvl == "1":
        description = """
            # Level 1: ScratchJr
            A simpler version of **Scratch**, a block-based programming language accessed at [scratch.mit.edu](scratch.mit.edu)<br>
            It is made for very small children and is easy to learn!
            See its website by clicking [here](scratchjr.org).
            <br><br>
            *This is from `limipy`, the LimiPlake Python package.*
        """
    elif lvl == "2":
        description = """
            # Level 2: Scratch
            The popular language **Scratch** is the language where you drag blocks to make your program like ScratchJr, but only these blocks are up and down, not side to side.
            ## New stuff from ScratchJr:
            - **More blocks:** More blocks than ScratchJr
            - Sensing blocks
            - Operators blocks
            - Variables blocks
            - Subprograms allowed
            - **Extensions*:** Brand new categories that you can add.
            <br><br>
            *This is from `limipy`, the LimiPlake Python package
        """
    elif lvl == "3":
        description = """
         # Level 2: Logo
         The coding language **Logo** is where you type commands to move a turtle around and make pictures. It's kind of like Scratch, but instead of blocks, you use words like `FD` and `RT`.

         ## New stuff from Scratch:
         - **Text-based:** You type instead of dragging blocks
         - Turtle draws with a pen
         - Commands like `REPEAT` for loops
         - You can make your own functions
         - Math and angle-based movement
         - No sprites—just one turtle!
         <br><br>
         *This is from `limipy`, the LimiPlake Python package*
        """
    elif lvl == "4":
        description = """# Level 4: Python
            **Python** is a typed language where you write everything using your keyboard. It's super powerful and can be used to build games, apps, and even control real-world robots.

            ## New stuff from Logo:
            - **Shell:** You can run Python in the terminal or VSCode
            - **Tkinter:** A way to make windows and buttons (GUIs)
            - **PyInstaller:** Turns your `.py` file into an app or `.exe`
            - You can import other Python files or libraries
            - Can read and write to files
            - Way more powerful math and logic

            <br><br>
            *This is from `limipy`, the LimiPlake Python package*"""
    elif lvl == "5":
        description = """
            # Level 5: Grodemate
            **Grodemate** is an advanced grid-based programming language made by our very own Founder & CEO.
        """
    elif lvl == "6":
        description = """
        # Level 6: AppLab
        Code.org's **AppLab** block-and-text based programming language/app gets you started with JavaScript.
        Something good before Level 7, making websites!"""
    elif lvl == "7":
        description = """
          # Level 7: HTML, CSS, and JavaScript  
          These three languages work together to make websites. You learn them after App Lab to build things that go on the real internet!

          ## New stuff from AppLab:  
          - **HTML:** Builds the structure (like a skeleton) of your page  
          - **CSS:** Styles your page (colors, fonts, sizes, layout)  
          - **JavaScript:** Adds actions, animations, and logic  
          - You can link files together: `index.html`, `style.css`, `script.js`  
          - Works inside real browsers  
          - Used by almost every website in the world!  

          <br><br>  
          *This is from `limipy`, the LimiPlake Python package*"""
    else:
        description = """
        Traceback (most recent call last)
          File "<stdin>", Ln 1, in <module>
        ValidationError: Not valid level number.
        """
    
    return description

def generate_student_pin(name: str):
    pin = sum(ord(c) for c in name.lower()) % 10000
    pin = str(pin).zfill(4)
    final_pin = int(pin) + 1
    full_pin = str(final_pin)
    return full_pin

def create_class_list(names: list):
    return {name: generate_student_pin(name) for name in names}

def level_quiz(level):
    if level == "1":
        answer = input("Is ScratchJr block-based or text-based?")
        if "block" in answer.lower():
            print("✅ Correct!")
        else:
            print("❌ Try again next time!")
    elif level == "4":
        answer = input("What do you type in to run Python in terminal? ")
        if "python" in answer.lower():
            print("✅ Nice job!")
        else:
            print("❌ Oops! It's usually 'python3' or 'python'")

        if level == "2":
            print("🎮 Scratch Quiz")
            q1 = input("Q1: What color are motion blocks in Scratch? ").strip().lower()
            if "blue" in q1:
             print("✅ Correct!")
        else:
            print("❌ They're usually blue!")

        q2 = input("Q2: What block repeats code? ").strip().lower()
        if "repeat" in q2 or "forever" in q2:
            print("✅ Yep!")
        else:
            print("❌ It's 'repeat' or 'forever'.")

    elif level == "3":
        print("🐢 Logo Quiz")
        q1 = input("Q1: What command moves the turtle forward? ").strip().upper()
        if q1 == "FD":
            print("✅ Correct!")
        else:
            print("❌ It's forward.")

        q2 = input("Q2: What does right mean? ").strip().upper()
        if q2 == "RIGHT" or q2 == "TURN RIGHT" or q2 == "RT":
            print("✅ Nice!")
        else:
            print("❌ right = Right Turn")

    elif level == "5":
        print("🟩 Grodemate Quiz")
        q1 = input("Q1: What symbol makes a grid block? ").strip()
        if "▣" in q1 or "square" in q1.lower():
            print("✅ That's right!")
        else:
            print("❌ It's ▣ or 'square'.")

        q2 = input("Q2: Who made Grodemate? ").strip().lower()
        if "anhad jain" in q2:
            print("✅ Correct! You made it!")
        else:
            print("❌ Nope! Anhad Jain, our Founder and CEO made Grodemate.")

    elif level == "6":
        print("🧩 App Lab Quiz (Code.org)")
        q1 = input("Q1: What language is used in App Lab? ").strip().lower()
        if "javascript" in q1:
            print("✅ Yup!")
        else:
            print("❌ It’s JavaScript.")

        q2 = input("Q2: What does `setProperty()` do? ").strip().lower()
        if "change" in q2 or "set" in q2 or "style" in q2:
            print("✅ That works!")
        else:
            print("❌ It sets a property like color or text.")

    elif level == "7":
        print("🌐 Web Quiz (HTML, CSS, JS)")
        q1 = input("Q1: What tag shows text in HTML? ").strip().lower()
        if "<p>" in q1 or "paragraph" in q1:
            print("✅ That’s right!")
        else:
            print("❌ Usually we use the <p> tag.")

        q2 = input("Q2: What does CSS do? ").strip().lower()
        if "style" in q2 or "design" in q2:
            print("✅ Correct!")
        else:
            print("❌ CSS makes websites look good!")

        q3 = input("Q3: What language makes things move or do actions on a website? ").strip().lower()
        if "javascript" in q3:
            print("✅ Exactly!")
        else:
            print("❌ It’s JavaScript.")

    else:
        print("⚠️ No quiz for that level yet!")

def show_available_levels():
    print("Levels in LimiPlake:")
    print("1. ScratchJr")
    print("2. Scratch")
    print("3. Logo")
    print("4. Python")
    print("5. Grodemate")            