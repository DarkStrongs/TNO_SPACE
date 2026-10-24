# r87：Mission Control 任务卡（照 TNO 原版任务卡：方角双线框 + 方形图标框 + 虚线分隔 + 粗分格进度条）
# 输出 gfx/interface/NSP/home/mission_control/nsp_mc_card.dds / nsp_mc_iconbox.dds / nsp_mc_dash.dds / nsp_mc_bar.dds（21 帧）
from PIL import Image
import struct, os
OUT='gfx/interface/NSP/home/mission_control/'
def save_dds(im,path):
    im=im.convert('RGBA'); w,h=im.size
    hdr=(b'DDS '+struct.pack('<7I',124,0x100F,h,w,w*4,0,0)+b'\0'*44
         +struct.pack('<8I',32,0x41,0,32,0x00FF0000,0x0000FF00,0x000000FF,0xFF000000)
         +struct.pack('<I',0x1000)+b'\0'*16)
    assert len(hdr)==128   # r87b：原写法多 8 字节 → 像素整体错位 2 px
    px=bytearray()
    for r,g,b,a in im.get_flattened_data(): px+=bytes((b,g,r,a))
    open(path,'wb').write(hdr+bytes(px))
BG=(7,18,22,236); LINE=(146,179,175,255); LINE2=(96,138,136,255); WHITE=(226,236,234,255); DIM=(64,86,86,255)
# 卡片：外线 1px 亮 → 2px 空 → 内线 1px 暗；borderSize 5
c=Image.new('RGBA',(32,32),BG)
for i in range(32):
    for (x,y) in ((i,0),(i,31),(0,i),(31,i)): c.putpixel((x,y),LINE)
    for (x,y) in ((i,3),(i,28),(3,i),(28,i)):
        if 3<=x<=28 and 3<=y<=28: c.putpixel((x,y),LINE2)
save_dds(c,OUT+'nsp_mc_card.dds')
# 图标框 28×28：2px 亮框
b=Image.new('RGBA',(28,28),(6,17,21,255))
for i in range(28):
    for t in (0,1):
        for (x,y) in ((i,t),(i,27-t),(t,i),(27-t,i)): b.putpixel((x,y),LINE)
save_dds(b,OUT+'nsp_mc_iconbox.dds')
# 虚线 180×2：4 实 3 空
d=Image.new('RGBA',(180,2),(0,0,0,0))
for x in range(180):
    if x%7<4:
        for y in (0,1): d.putpixel((x,y),LINE)
save_dds(d,OUT+'nsp_mc_dash.dds')
# 进度条 214×24 × 21 帧：2px 白框，41 格（宽 4 间隔 1，1px 描边空心）
W,H,N=214,24,41
bar=Image.new('RGBA',(W*21,H),(0,0,0,0))
for f in range(21):
    fr=Image.new('RGBA',(W,H),(4,12,15,255))
    for x in range(W):
        for t in (0,1): fr.putpixel((x,t),WHITE); fr.putpixel((x,H-1-t),WHITE)
    for y in range(H):
        for t in (0,1): fr.putpixel((t,y),WHITE); fr.putpixel((W-1-t,y),WHITE)
    fill=round(N*f/20)
    for k in range(N):
        col=WHITE if k<fill else DIM
        x0=5+k*5; y0=5; y1=H-6
        for y in range(y0,y1+1):
            for x in range(x0,x0+4):
                if y in (y0,y1) or x in (x0,x0+3): fr.putpixel((x,y),col)
    bar.paste(fr,(W*f,0))
save_dds(bar,OUT+'nsp_mc_bar.dds')
print('ok')
