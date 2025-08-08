#

from buildz import fz

import re
pt = "\.*\d{0,1}\.*"

fp = "./kl.js"
ofp = "./okl.js"
s= fz.read(fp).decode()
rst = re.findall(pt, s)
rst = [k for k in rst if k.find(".")>=0]
s = s.replace(".", "^")
for k in rst:
    src = k.replace(".", "^")
    if k[0]=='.':
        tgt = k[-1]+k[:-1]
    else:
        tgt = k[1:]+k[0]
    s = s.replace(src, tgt)

print(s)
fz.write(s.encode(), ofp)
'''
python test.py

'''