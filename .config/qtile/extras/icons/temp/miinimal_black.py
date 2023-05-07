import iwlib
import cv2
import numpy as np

def get_status(interface_name):
    interface = iwlib.get_iwconfig(interface_name)
    if "stats" not in interface:
        return None, None
    return interface["stats"]["quality"]

imagen = cv2.imread('./wifi.png')
imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGBA)
result = np.zeros(imagen.shape,dtype=np.uint8)
gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5,5), 0)
_, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contornos, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
quality = get_status('wlo1')
for i, contorno in enumerate(contornos):
    if quality < (17.5 * (i + 1)):
        cv2.drawContours(result, [contorno], -1, (0, 0, 0, 0.7*255), -1)
    else:
        cv2.drawContours(result, [contorno], -1, (0, 0, 0, 1*255), -1)

result = cv2.bitwise_and(imagen, result)

cv2.imshow('wifi', result)
cv2.waitKey(0)
cv2.imwrite("wifitemp.png", result)