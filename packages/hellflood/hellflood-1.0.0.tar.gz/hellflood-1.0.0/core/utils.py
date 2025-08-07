import os
import sys
import time

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def loading():
    for i in range(3):
        sys.stdout.write("\rLoading" + "." * (i + 1))
        sys.stdout.flush()
        time.sleep(0.5)
    print("\n")
