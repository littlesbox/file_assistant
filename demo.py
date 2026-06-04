import os
try:
    import readline
except ImportError:
    # Windows 下可以试试 pyreadline3
    try:
        import pyreadline3 as readline
    except ImportError:
        pass


while True:
    text = input("用户：")
    if text == "exit":
        break
    print(text)