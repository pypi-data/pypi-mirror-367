import os
import time

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def banner():
    clear()
    print("""
╔════════════════════════════════════╗
║           HELLFLOOD ⚠️            ║
║      DDOS Tool | Dark Edition      ║
╚════════════════════════════════════╝
""")
    time.sleep(1)

def menu():
    banner()
    print("[1] Start Attack")
    print("[2] HellMode")
    print("[3] Exit")
    return input("\n> ")
