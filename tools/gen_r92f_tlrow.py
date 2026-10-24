# r92f：时间线行框 6 帧 → 8 帧：插入第 5 帧「乘组」（紫）和第 8 帧「返程」（蓝），都由白色「总装」帧调色。只读 work/r92f/bak 原图，可重跑。
from PIL import Image
import struct
SRC='/workspace/work/r92f/bak/nsp_timeline_row.dds'; DST='gfx/interface/NSP/planner/timeline/nsp_timeline_row.dds'
d=open(SRC,'rb').read(); h,w=struct.unpack('<II',d[12:20]); hdr=bytearray(d[:128])
im=Image.frombytes('RGBA',(w,h),d[128:128+w*h*4],'raw','BGRA'); fw=w//6
fr=[im.crop((fw*i,0,fw*(i+1),h)) for i in range(6)]
BG=(6,17,22)
def tint(col):
    c=fr[3].copy(); px=c.load()
    for y in range(h):
        for x in range(fw):
            r,g,b,a=px[x,y]
            if (r,g,b)==BG: continue
            t=max(r,g,b)/255
            px[x,y]=(int(col[0]*t),int(col[1]*t),int(col[2]*t),a)
    return c
order=[fr[0],fr[1],fr[2],fr[3],tint((190,140,240)),fr[4],fr[5],tint((110,160,240))]
out=Image.new('RGBA',(fw*8,h)); [out.paste(f,(fw*i,0)) for i,f in enumerate(order)]
W=fw*8; struct.pack_into('<I',hdr,16,W); struct.pack_into('<I',hdr,20,W*4)
assert len(hdr)==128
open(DST,'wb').write(bytes(hdr)+out.tobytes('raw','BGRA'))
out.resize((W,h*3),0).save('/workspace/work/r92f/tlrow.png'); print(W,h)
