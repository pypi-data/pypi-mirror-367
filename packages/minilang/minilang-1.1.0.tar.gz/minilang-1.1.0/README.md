# minilang

**minilang** is a lightweight Python library that lets you make a simple programing language.


## 📦 Installation

```bash
pip install minilang
or:
pip3 install minilang


## usage
from minilang import MiniLang
lang = MiniLang()
lang.add_function("greet", lambda: print("Hello from MiniLang!"))
lang.run("""
x = 3 * 4;
print x;
greet;
""")


