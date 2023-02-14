#!/usr/bin/env python
 
import sys
import select
 
def processSomething():
    print("Do something")
 
while True:
    input = select.select([sys.stdin], [], [], 1)[0]
    if input:
        value = sys.stdin.readline().rstrip()
 
        if (value == "q"):
            print("Exiting")
            sys.exit(0)
        else:
            print(f"You entered: {value}")
    else:
        processSomething()