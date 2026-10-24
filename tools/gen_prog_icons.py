# ⚠ r93b：4 个 48×48 徽章已改由 work/r93/badges.py 按原徽章风格重画；重跑本脚本会把徽章覆盖回旧画法，重跑后需再跑 badges.py。
# r92：新增计划 3..6 的页签帧（28×28，帧 = 图标*2+1 / +2 选中）和 48×48 徽章。
# 页签：复制双子星页签帧（图标 5）擦掉字形再画；徽章：复制阿波罗徽章擦掉 Ⓐ 再画金色字形。只读原 dds，可重跑。
from PIL import Image, ImageDraw
import struct, shutil, os
B='gfx/interface/NSP/'
def load(p):
    d=open(p,'rb').read(); h,w=struct.unpack('<II',d[12:20])
    return Image.frombytes('RGBA',(w,h),d[128:128+w*h*4],'raw','BGRA')
def save(im,p):
    w,h=im.size
    hdr=struct.pack('<4sIIIIIII44sIIIIIIIIIIIII',b'DDS ',124,0x100F,h,w,w*4,0,1,b'\0'*44,32,0x41,0,32,0xFF0000,0xFF00,0xFF,0xFF000000,0x1000,0,0,0,0)
    assert len(hdr)==128
    open(p,'wb').write(hdr+im.tobytes('raw','BGRA'))
G={
'sat':["............","###......###","#.#......#.#","#.#.####.#.#","#.###..###.#","#.#.#..#.#.#","###.#..#.###","....####....",".....##.....","....#..#....","...#....#...","............"],
'lander':[".....##.....","....#..#....","...#....#...","..########..","..#.#..#.#..","..########..","..#......#..",".#........#.",".#........#.","#..........#","##........##","............"],
'planet':["............","....####....","..##....##..",".#........#.","############","#.#......#.#","############",".#........#.","..##....##..","....####....","............","............"],
'station':[".....##.....","####.##.####","#..#.##.#..#","#..######..#","#..#.##.#..#","####.##.####",".....##.....","....####....","....#..#....","....#..#....","....####....","............"],
}
ORDER=['sat','lander','planet','station']   # 计划 3 应用卫星 / 4 勘测者 / 5 水手 / 6 天空实验室
def glyph(dr,g,x0,y0,s,col,outline=None):
    if outline:
        for r,row in enumerate(g):
            for c,ch in enumerate(row):
                if ch=='#': dr.rectangle([x0+c*s-1,y0+r*s-1,x0+c*s+s,y0+r*s+s],fill=outline)
    for r,row in enumerate(g):
        for c,ch in enumerate(row):
            if ch=='#': dr.rectangle([x0+c*s,y0+r*s,x0+c*s+s-1,y0+r*s+s-1],fill=col)
src=os.path.join(B,'mission/nsp_program_tabs.dds')
bak='/workspace/work/r92/bak/nsp_program_tabs_r91.dds'
if not os.path.exists(bak): shutil.copy(src,bak)
tabs=load(bak); FW=28; n0=tabs.width//FW; assert n0==14
out=Image.new('RGBA',(FW*(n0+8),FW),(0,0,0,0)); out.paste(tabs,(0,0))
for k,name in enumerate(ORDER):
    for sel in (0,1):
        f=tabs.crop((FW*(10+sel),0,FW*(11+sel),FW)).copy()
        # 字形颜色 = 中心区最亮像素；底色 = (3,3)
        px=[f.getpixel((x,y)) for x in range(6,22) for y in range(5,22)]
        col=max(px,key=lambda p:p[0]+p[1]+p[2]+p[3]); bg=f.getpixel((4,4))
        d=ImageDraw.Draw(f); d.rectangle([5,4,22,22],fill=bg)
        glyph(d,G[name],8,8,1,col)
        out.paste(f,(FW*(14+k*2+sel),0))
save(out,src)
for k,name in enumerate(ORDER):
    b=load(os.path.join(B,'badges/nsp_badge_apollo.dds')).copy()
    from collections import Counter; navy=Counter(b.getpixel((x,y)) for x in range(10,38) for y in range(16,44)).most_common(1)[0][0]; gold=max([b.getpixel((x,y)) for x in range(16,32) for y in range(20,40)],key=lambda p:p[0]+p[1])
    dark=(int(gold[0]*0.45),int(gold[1]*0.4),int(gold[2]*0.3),255)
    d=ImageDraw.Draw(b); d.ellipse([11,17,37,43],fill=navy)
    glyph(d,G[name],12,18,2,gold)
    save(b,os.path.join(B,f'badges/nsp_badge_{name}.dds'))
print('ok', out.size)
