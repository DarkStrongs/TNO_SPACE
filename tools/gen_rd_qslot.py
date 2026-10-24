# 研发页底部研发槽格子：
#   nsp_rd_qslot.dds   3 帧 126×40：1 空闲 / 2 研发中 / 3 未解锁（斜线底纹 + 锁头，仿规划器修正槽锁定格）
#   nsp_rd_qbar_s.dds  11 帧 72×6：进度 0..100%，24 段竖条（2 亮 1 空），配色同 nsp_rd_qbar
import struct, os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUT=os.path.join(ROOT,'gfx/interface/NSP/rd/drawer')
def save_dds(im,p):
    w,h=im.size
    hdr=b'DDS '+struct.pack('<7I',124,0x100F,h,w,w*4,0,0)+b'\0'*44+struct.pack('<8I',32,0x41,0,32,0xFF0000,0xFF00,0xFF,0xFF000000)+struct.pack('<5I',0x1000,0,0,0,0)
    open(p,'wb').write(hdr+im.convert('RGBA').tobytes('raw','BGRA'))
W,H=126,40
BG=(9,22,24,255); IN=(6,18,20,255)
BORD={1:(52,82,80,255),2:(125,173,169,255),3:(30,44,46,255)}
HATCH=(20,38,40,255)
LOCK=(96,120,118,255)
PAD=["..####..",".#....#.",".#....#.","########","###..###","###..###","########"]
sheet=Image.new('RGBA',(W*3,H),(0,0,0,0)); px=sheet.load()
for f in (1,2,3):
    ox=(f-1)*W
    for y in range(H):
        for x in range(W):
            if x in (0,W-1) or y in (0,H-1): c=BORD[f]
            elif x in (1,W-2) or y in (1,H-2): c=IN
            else:
                c=BG
                if f==3 and (x+y)%6==0: c=HATCH
            px[ox+x,y]=c
    if f==3:   # 锁头：第二行居中
        lx=ox+W//2-4; ly=24
        for j,row in enumerate(PAD):
            for i,ch in enumerate(row):
                if ch=='#': px[lx+i,ly+j]=LOCK
save_dds(sheet,os.path.join(OUT,'nsp_rd_qslot.dds'))
sheet.resize((W*3*3,H*3),Image.NEAREST).save('/tmp/qslot_prev.png')
ON=(240,208,80,255); OFF=(14,28,32,255)
BW,SEG=72,24
bar=Image.new('RGBA',(BW*11,6),(0,0,0,0)); bp=bar.load()
for k in range(11):
    lit=round(SEG*k/10)
    for s in range(SEG):
        c=ON if s<lit else OFF
        for dx in (0,1):
            for y in range(6): bp[k*BW+s*3+dx,y]=c
save_dds(bar,os.path.join(OUT,'nsp_rd_qbar_s.dds'))
