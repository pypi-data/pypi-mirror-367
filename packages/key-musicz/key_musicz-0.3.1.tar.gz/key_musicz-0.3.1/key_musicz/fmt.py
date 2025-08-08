#

from buildz import Base, dz, fz, xf
from buildz.xf.readz import *
import time,threading, numpy as np
def build_mcfmt(as_bytes=False):
    mgs = mg.Manager(as_bytes)
    # mgs.add(setz.SetDeal(':'))
    # mgs.add(setz.SetDeal('='))
    mgs.add(spt.PrevSptDeal(",",1))
    mgs.add(spt.PrevSptDeal(';',1))
    mgs.add(spt.PrevSptDeal(" "))
    mgs.add(spt.PrevSptDeal("|",0,"|","|"))
    mgs.add(spt.PrevSptDeal('\n'))
    mgs.add(listz.ListDeal("(", ")"))
    mgs.add(listz.ListDeal("[", "]"))
    #mgs.add(mapz.MapDeal("{", "}"))
    #1,0,0,1: 没引号当r"..."
    #1,0,1,1: 没引导当"..."
    mgs.add(strz.PrevStrDeal('r"""','"""',0,0,0))
    mgs.add(strz.PrevStrDeal('r"','"',1,0,0,1))
    mgs.add(strz.PrevStrDeal("/*","*/",0,1))
    mgs.add(strz.PrevStrDeal('"""','"""',0,0,1))
    mgs.add(strz.PrevStrDeal("//","\n",1,1))
    mgs.add(strz.PrevStrDeal('"','"',1,0,1))
    mgs.add(nextz.PrevNextDeal())
    return mgs

pass
def loads(s):
    mgs = build_mcfmt(type(s)==bytes)
    #input = buffer.BufferInput(s)
    return mgs.loads(s)

pass
s = r"""
//卡龙
|3. - - - | 2. - - - | 1. - - - | 7 - - -  |
|1 3 5 -  |.5 .7 2 - |.6 1 3 -  |.3 .5 .7 -|

|6 - - -  | 5 - - -  | 6 - - -  | 7 - - -  |
|.4 .6 1 -|.1 .3 .5 -|.4 .6 1 - |.5 .7 2 -|

| 3. 0 3. 1. | 2. 0 0 7|1. 0 1. 6|7 0 0 5|
|1 3 5 -|.5 .7 2 -|.6 1 3 -|.3 .5 .7 -|

"""
def load_fmt(s):
    rst = loads(s)
    info = {}
    if len(rst)>0 and rst[0].find("{")>=0:
        #print("loads:", rst[0])
        #exit()
        info = xf.loads(rst[0])
        rst = rst[1:]
    outs = []
    curr = []
    for k in rst:
        if k == "|":
            if len(curr)>0:
                outs.append(curr)
                curr = []
        else:
            curr.append(k)
    if len(curr)>0:
        outs.append(curr)
    return outs, info

def build_fmt(arr, channels=2, channel_unit=4):
    outs = []
    for i in range(channels):
        outs.append([])
    #print(f"outs:", outs)
    #exit()
    i_channel = 0
    for i in range(0, len(arr), channel_unit):
        dts = arr[i:i+channel_unit]
        outs[i_channel]+=dts
        i_channel = (i_channel+1)%channels
    return outs

pass
def spt_ks(ks, spt):
    rst = []
    for k in ks:
        rst+=k.split(spt)
    return rst
def spts_ks(k):
    ks = [k]
    ks = spt_ks(ks, "&")
    ks = spt_ks(ks, "/")
    ks = spt_ks(ks, "+")
    return ks
def build_rate(arr, unit=1.0):
    rst = []
    single = unit/len(arr)
    for k in arr:
        if type(k)==list:
            rst+=build_rate(k, single)
        else:
            rst.append([k, single])
    return rst


def build_rates(arr, unit=1.0):
    rst = []
    for k in arr:
        rst+=build_rate(k, unit)
    return rst
pass
def build_channels_rates(arr,unit=1.0):
    arr = [build_rates(k, unit) for k in arr]
    return arr
pass
def inc(arr):
    curr = 0
    rst = []
    for k, r in arr:
        rst.append([curr, k])
        curr+=r
    return rst
def combine(arr):
    arr = [inc(k) for k in arr]
    rst = []
    for k in arr:
        rst+=k
    rst.sort(key = lambda x:x[0])
    outs = []
    curr=None
    tmp = []
    for rate, k in rst:
        if rate==curr:
            tmp.append(k)
        else:
            if len(tmp)>0:
                outs.append(tmp)
            tmp = [rate, k]
            curr = rate
    if len(tmp)>0:
        outs.append(tmp)
    return outs
def loads_and_build(s, conf = {}):
    arr, info = load_fmt(s)
    dz.fill(info, conf)
    channels,channel_unit = dz.g(info, channels=2,channel_unit=4)
    arr = build_fmt(arr, channels,channel_unit)
    arr = build_channels_rates(arr)
    arr = combine(arr)
    return arr, info
def test():
    import os
    dp = os.path.dirname(__file__)
    fp = os.path.join(dp, 'conf', 'kl1.js')
    s = fz.read(fp).decode()
    arr, info = load_fmt(s)
    print("info:", info)
    channels,channel_unit = dz.g(info, channels=2,channel_unit=4)
    arr = build_fmt(arr, channels,channel_unit)
    for k in arr:
        print(k)
    #exit()
    arr = build_channels_rates(arr)
    arr = combine(arr)
    print("combine:")
    print(arr)
    #print(arr)

pass

from buildz import pyz
pyz.lc(locals(), test)

'''
python -m key_musicz.fmt

from key_musicz import fmt


fmt.loads(r"[.1,2,3..,4.']")

'''

bases = "1,#1,2,#2,3,4,#4,5,#5,6,#6,7".split(",")
#pfxs = "...ab,..ab,.ab,ab,a.b,a..b,a...b".split(",")
#pfxs = "a...b,a..b,a.b,ab,.ab,..ab,...ab".split(",")
pfxs = "ba...,ba..,ba.,ba,b.a,b..a,b...a".split(",")
base_offset=36
keys = []
for pfx in pfxs:
    for key in bases:
        a = key[-1:]
        b = key[:-1]
        c = pfx.replace("a",a).replace("b",b)
        keys.append(c)

pass
key2offset = {}
for i in range(len(keys)):
    key2offset[keys[i]] = i

emptys = set('0,_,-'.split(","))
def check_empty(c):
    return c in emptys

pass
class FileRead(Base):
    def load(self):
        if self.fp is None:
            self.datas = None
            return
        s = fz.read(self.fp).decode()
        datas, info = loads_and_build(s, self.info)
        self.datas = datas
        #dz.fill(info, self.info, replace=1)
        loop, stop,base,sec,power = dz.g(self.info, loop=True, stop=False, base=72,sec=4,power=100)
        self.loop = loop
        self.stop_after_play = stop
        self.base = base
        self.sec = sec
        self.power = power
    def init(self, maps, obj):
        self.th = None
        self.running = True
        self.obj = obj
        self.fp = dz.g(maps, fp=None)
        self.info = maps
        self.load()
    def presses(self, arr):
        rst = []
        for k in arr:
            rst+= spts_ks(k)
        for k in rst:
            if check_empty(k):
                continue
            n = key2offset[k]-base_offset+self.base
            self.obj.dv_sound(True,n,self.power)
    def single(self):
        curr=None
        for dt in self.datas:
            if not self.running:
                break
            rate = dt[0]
            if curr is None:
                curr = rate
            diff = rate-curr
            curr=rate
            #print(f"rate:", rate, "curr:", curr, "diff:", diff, "sec:", diff*self.sec)
            if diff>0:
                sec = diff*self.sec
                time.sleep(sec)
            self.presses(dt[1:])
    def run(self):
        if self.datas is None:
            return
        self.running = True
        while self.running:
            self.single()
            if not self.loop:
                break
        if self.running and self.stop_after_play:
            time.sleep(self.sec*0.25)
            self.obj.quit()
    def stop(self):
        self.running = False
    def start(self):
        if self.th is not None:
            return
        self.th = threading.Thread(target=self.run, daemon=True)
        self.th.start()