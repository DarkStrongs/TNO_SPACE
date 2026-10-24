# r92b：规划器补「试验性载荷」(payload 帧 10) 和「试验性火箭」(vehicle 帧 9)。只读 work/r92b/bak 原图，可重跑。
from PIL import Image, ImageDraw
import struct
B='gfx/interface/NSP/planner/'; BAK='/workspace/work/r92b/bak/'
def load(p):
    d=open(p,'rb').read(); h,w=struct.unpack('<II',d[12:20]); return Image.frombytes('RGBA',(w,h),d[128:128+w*h*4],'raw','BGRA')
def save(im,p):
    w,h=im.size
    hdr=struct.pack('<4sIIIIIII44sIIIIIIIIIIIII',b'DDS ',124,0x100F,h,w,w*4,0,1,b'\0'*44,32,0x41,0,32,0xFF0000,0xFF00,0xFF,0xFF000000,0x1000,0,0,0,0)
    assert len(hdr)==128; open(p,'wb').write(hdr+im.tobytes('raw','BGRA'))
OUT=(18,30,30,255); TEAL=(77,190,190,255)
SH=[(236,244,240),(206,222,214),(206,222,214),(198,214,208),(198,214,208),(160,180,174),(146,166,162),(146,166,162),(112,132,128)]
def shade(n):  # n 行的竖向渐变
    return [SH[min(len(SH)-1,int(i*len(SH)/n))]+(255,) for i in range(n)]
def cyl(d,x0,x1,yc,h):
    y0=yc-h//2; S=shade(h)
    d.rectangle([x0-1,y0-1,x1+1,y0+h],fill=OUT)
    for i in range(h): d.line([x0,y0+i,x1,y0+i],fill=S[i])
def nose(d,x0,length,yc,h):  # 向右的锥
    y0=yc-h//2; S=shade(h)
    for i in range(h):
        t=abs(i-(h-1)/2)/((h-1)/2+0.01)
        xe=x0+int(length*(1-t)); d.line([x0,y0+i,xe,y0+i],fill=S[i])
        d.point((xe+1,y0+i),fill=OUT)
# ---- 试验性载荷：探险者 1 号式细长圆柱 + 鞭状天线 ----
pa=load(BAK+'nsp_payload_art.dds'); FW,FH=240,80; assert pa.width==FW*9
f=Image.new('RGBA',(FW,FH),(0,0,0,0)); d=ImageDraw.Draw(f)
cyl(d,78,150,40,10); nose(d,151,14,40,10)
for x in (96,118,140): d.line([x,35,x,45],fill=(112,132,128,255))
d.rectangle([100,36,112,44],fill=TEAL); d.rectangle([100,36,112,36],fill=(150,230,230,255))
for (x,y,dx,dy) in [(84,34,-10,-12),(84,46,-10,12),(92,34,-6,-14),(92,46,-6,14)]:
    d.line([x,y,x+dx,y+dy],fill=(190,205,200,255))
d.line([60,40,77,40],fill=(190,205,200,255))
pa2=Image.new('RGBA',(FW*10,FH),(0,0,0,0)); pa2.paste(pa,(0,0)); pa2.paste(f,(FW*9,0)); save(pa2,B+'nsp_payload_art.dds')
# ---- 试验性火箭：朱诺 I / 木星-C 式（红石一级 + 旋转上面级桶）----
va=load(BAK+'nsp_vehicle_art.dds'); FW,FH=240,70; assert va.width==FW*8
f=Image.new('RGBA',(FW,FH),(0,0,0,0)); d=ImageDraw.Draw(f)
yc=35
cyl(d,40,118,yc,14)
d.polygon([(40,yc-7),(52,yc-7),(40,yc-12)],fill=(146,166,162,255),outline=OUT)   # 尾翼
d.polygon([(40,yc+7),(52,yc+7),(40,yc+12)],fill=(112,132,128,255),outline=OUT)
for x in (66,94): d.line([x,yc-7,x,yc+6],fill=(112,132,128,255))
cyl(d,119,132,yc,10)       # 仪器舱
cyl(d,133,148,yc,12)       # 旋转桶
for x in range(136,148,4): d.line([x,yc-6,x,yc+5],fill=(77,150,150,255))
cyl(d,149,155,yc,6); nose(d,156,7,yc,6)
va2=Image.new('RGBA',(FW*9,FH),(0,0,0,0)); va2.paste(va,(0,0)); va2.paste(f,(FW*8,0)); save(va2,B+'nsp_vehicle_art.dds')
c=Image.new('RGBA',(480,160),(10,22,26,255)); c.alpha_composite(pa2.crop((FW*0,0,240*1,80)),(0,0)); c.alpha_composite(pa2.crop((2160,0,2400,80)),(240,0)); c.alpha_composite(va2.crop((960,0,1200,70)),(0,85)); c.alpha_composite(va2.crop((1920,0,2160,70)),(240,85))
c.resize((960,320),Image.NEAREST).save('/workspace/work/r92b/art_new.png'); print('ok')
