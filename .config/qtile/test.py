import psutil

binfo = psutil.sensors_battery()
print(binfo.percent)