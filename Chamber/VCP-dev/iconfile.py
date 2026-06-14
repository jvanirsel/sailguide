import re
import base64

print('starting icon conversion')
open_icon=open("C:/Users/jonas/Documents/Github/SETL/Python/setl_icon.ico", "rb")
b64_str = base64.b64encode(open_icon.read())
open_icon.close()
write_data = "img=%s" % b64_str
f=open("icon.py", "w+")
f.write(write_data)
f.close()
