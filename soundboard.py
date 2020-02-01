#!/usr/bin/python

from gpiozero import Button
from time import sleep
import requests

if __name__ == '__main__':
    button = Button(17)
    while True:
        if button.is_pressed:
            r = requests.get('http://127.0.0.1:6969/play')
            print (r)
    sleep(1)
