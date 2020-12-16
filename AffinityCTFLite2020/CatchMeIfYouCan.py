#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import base64
import pytesseract
from PIL import Image
import io
import requests
import cv2
from resizeimage import resizeimage


def send_request(flag):
    # remove weird byte <0xc0> at the end
    flag = flag[:-1]
    r = requests.post("http://web4.affinityctf.com/validate",
                      data={'code': flag})
    print(r.status_code, r.reason)
    print(r.text[:300])

    if "Ops, you just missed it" in r.text:
        print("NOPE" + ": \n" + flag)
        return 0
    else:
        print(r.text)

    return 1


def analyze(data):
    # del 26 from front
    data = data[26:]
    # del 16 from end
    data = data[:-15]

    imgstring = data.split('base64,')[-1].strip()
    pic = io.StringIO()
    image_string = io.BytesIO(base64.b64decode(imgstring))

    image = Image.open(image_string)
    bg = Image.new("RGB", image.size, (0, 0, 255))
    bg.paste(image, image)

# CONFIG SECTION

    # using psm 8 because we only have a single “word”
    custom_oem_psm_config = '--dpi 1000 --oem 3 --psm 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz'
    # text = pytesseract.image_to_string(gray, config=custom_oem_psm_config, timeout=2)

    bg.save('pic.png')
    # re read the image ", 0" is very important
    image = cv2.imread('pic.png', 0)

    result = pytesseract.image_to_string(
        image, config=custom_oem_psm_config).replace(" ", "").replace("\n", "")

    if send_request(result):
        print("WE HAVE A FLAG")
        exit(1)

    return 1


browser = webdriver.Firefox(executable_path="/root/Desktop/geckodriver")
browser.get('http://web4.affinityctf.com/')

source = browser.page_source

found_div = 0
found_catch = 0

try:
    sleepcounter = 0
    while 1:
        if sleepcounter >= 100000:
            break
        sleep(5)
        sleepcounter += 1

        try:
            # found_div = browser.find_element_by_xpath('//div[@id="catcher" and @class="catcher"]')
            found_div = browser.find_elements_by_css_selector('div')
            if found_div:
                innerhtml = found_div[-2].get_attribute('innerHTML')
                if 'class="catcher' in innerhtml and 'src=""' not in innerhtml:
                    found_catch = innerhtml

            if found_catch:
                result = analyze(found_catch)

        except Exception as err1:
            print("ERR1")
            print(err1)


except Exception as err2:
    print("ERR2")
    print(err2)
    pass

finally:
    browser.quit()
