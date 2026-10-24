import os
# r95b：乘组选拔窗口贴图，照 TNO 最高法院面板（亮青双线框 + 分区框 + 黄字列表行 + 分段条）。可重跑。
from PIL import ImageOps
from PIL import Image, ImageDraw
import struct
OUT='gfx/interface/NSP/crew/'
def save_dds(im,path):
    im=im.convert('RGBA'); w,h=im.size
    hdr=(b'DDS '+struct.pack('<7I',124,0x100F,h,w,w*4,0,0)+b'\0'*44
         +struct.pack('<8I',32,0x41,0,32,0x00FF0000,0x0000FF00,0x000000FF,0xFF000000)
         +struct.pack('<I',0x1000)+b'\0'*16)
    assert len(hdr)==128
    px=bytearray()
    for r,g,b,a in im.get_flattened_data(): px+=bytes((b,g,r,a))
    open(path,'wb').write(hdr+bytes(px))
BG=(6,17,21,255); CY=(84,196,190,255); CY2=(52,128,124,255); DARK=(9,22,26,255)
GRN=(60,150,70,255); RED=(150,40,44,255); REDL=(100,24,28,255); GRNF=(40,120,60,255); GRNL=(26,80,40,255)
def dbl(d,x0,y0,x1,y1,c=CY,c2=CY,gap=4,w=2):
    for i in range(w): d.rectangle([x0+i,y0+i,x1-i,y1-i],outline=c)
    d.rectangle([x0+gap,y0+gap,x1-gap,y1-gap],outline=c2)
W,H=1060,610   # r95h 头像显示缩到 0.75（贴图仍 156×210），窗口压到 610；r95f：照 TNO New Mission Concept 面板（顶部标题栏 + 编号分区 + 表格行 + START MISSION 式大按钮）
bg=Image.new('RGBA',(W,H),BG); d=ImageDraw.Draw(bg)
GB=(120,220,120,255); GB2=(60,130,64,255)
def sec(x0,y0,x1,y1):   # 编号分区头：左侧数字格 46 宽
    d.rectangle([x0,y0,x1,y1],outline=CY); d.line([x0+46,y0,x0+46,y1],fill=CY)
for i in range(2): d.rectangle([i,i,W-1-i,H-1-i],outline=CY)
d.rectangle([8,8,W-9,H-9],outline=CY)
d.line([8,66,W-9,66],fill=CY); d.line([8,68,W-9,68],fill=CY2)       # 顶部标题栏 8..66
d.line([596,68,596,H-9],fill=CY); d.line([598,68,598,H-9],fill=CY2) # 左右分栏
# 左：任务框 / 1 飞行乘组 / 卡牌区 / 大按钮区
d.rectangle([16,76,588,150],outline=CY)
sec(16,158,588,206)
d.rectangle([16,214,588,488],outline=CY)
# r95n 卡牌区照 TNO el_tapado_background：三段 × 九宫格青线 + 每段一枚淡色线稿水印（NASA 徽标 / 火箭 / 月球轨道）
import math
WM=(22,58,60,255); GQ=(30,84,84,255)
sx=[16,207,398,588]
for i in range(3):
    x0,x1=sx[i],sx[i+1]; cw=(x1-x0)/3
    for k in (1,2): d.line([int(x0+k*cw),215,int(x0+k*cw),487],fill=GQ)
    if i: d.line([x0,215,x0,487],fill=CY2); d.line([x0+1,215,x0+1,487],fill=CY2)
for y in (305,396): d.line([17,y,587,y],fill=GQ)
def wm_meatball(cx,cy):
    d.ellipse([cx-80,cy-80,cx+80,cy+80],outline=WM,width=3)
    d.ellipse([cx-110,cy-30,cx+110,cy+30],outline=WM,width=3)
    d.line([cx-70,cy+40,cx+20,cy-10,cx+90,cy-60],fill=WM,width=4)
    for (a,b) in ((-40,-45),(30,40),(-10,55),(50,-30)): d.ellipse([cx+a-3,cy+b-3,cx+a+3,cy+b+3],fill=WM)
def wm_rocket(cx,cy):
    d.polygon([(cx,cy-120),(cx+16,cy-90),(cx+16,cy+70),(cx-16,cy+70),(cx-16,cy-90)],outline=WM,width=3)
    d.polygon([(cx-16,cy+30),(cx-40,cy+90),(cx-16,cy+70)],outline=WM,width=3); d.polygon([(cx+16,cy+30),(cx+40,cy+90),(cx+16,cy+70)],outline=WM,width=3)
    for y in (-60,-20,20): d.line([cx-16,cy+y,cx+16,cy+y],fill=WM,width=2)
    d.polygon([(cx-10,cy+70),(cx+10,cy+70),(cx,cy+110)],outline=WM,width=3)
def wm_moon(cx,cy):
    d.ellipse([cx-60,cy-60,cx+60,cy+60],outline=WM,width=3)
    for (a,b,r) in ((-20,-15,12),(25,20,9),(-15,30,7),(28,-28,6)): d.ellipse([cx+a-r,cy+b-r,cx+a+r,cy+b+r],outline=WM,width=2)
    d.arc([cx-120,cy-50,cx+120,cy+50],200,340,fill=WM,width=3); d.arc([cx-120,cy-50,cx+120,cy+50],0,160,fill=WM,width=3)
    d.ellipse([cx+100,cy-22,cx+112,cy-10],fill=WM)
# r95o 水印被不透明卡牌挡住只露碎线，取消：wm_meatball(111,351); wm_rocket(302,351); wm_moon(493,351)
d.rectangle([16,214,588,488],outline=CY)
# 右：2 待命宇航员 + FROM 式药丸分隔
sec(606,76,1044,124)
d.line([612,138,1038,138],fill=CY); d.line([612,142,1038,142],fill=CY)
d.rounded_rectangle([680,128,970,152],radius=12,fill=BG,outline=CY)
d.rectangle([606,160,1044,H-12],outline=CY2)
save_dds(bg,OUT+'nsp_crew_bg.dds')
# 宇航员行 210×28：细框 + 左侧方格（飞行次数），照 New Mission Concept 的发射场列表行
r=Image.new('RGBA',(210,26),DARK); d=ImageDraw.Draw(r)   # r95h 行高 26
d.rectangle([0,0,209,25],outline=CY2); d.rectangle([0,0,25,25],outline=CY); d.rectangle([2,2,23,23],outline=CY2)
save_dds(r,OUT+'nsp_crew_row.dds')
# r95q 确定 572×80 × 2 帧（1 可点 2 未选满）：照 El Tapado 标题格 / map_bg 线稿 — 直角双线框 + 两端柱头玫瑰饰（取自 map_bg.dds 456..473,14..31，×2）+ 竖分隔线
#   去掉 r95f 的两侧横线和中央内框（用户：按钮要优化）
_ros=Image.open('tools/crew_frame_src/map_bg.dds').convert('RGBA').crop((456,14,473,32))
_ros=_ros.crop(_ros.getbbox()).resize((_ros.getbbox()[2]*2-_ros.getbbox()[0]*2,_ros.getbbox()[3]*2-_ros.getbbox()[1]*2),Image.NEAREST)
def _tint(im,c):
    t=im.copy(); px=t.load()
    for y in range(t.size[1]):
        for x in range(t.size[0]):
            if px[x,y][3]>0: px[x,y]=c[:3]+(px[x,y][3],)
    return t
ok=Image.new('RGBA',(1144,80),(0,0,0,0))
for f,(c,c2,fill) in enumerate((((89,199,194,255),(60,135,131,255),(10,32,34,255)),((52,92,92,255),(34,58,58,255),(8,16,18,255)))):
    a=Image.new('RGBA',(572,80),fill); d=ImageDraw.Draw(a)
    d.rectangle([0,0,571,79],outline=c); d.rectangle([3,3,568,76],outline=c)          # 双线框（照 EL TAPADO 标题格）
    for x in (60,511): d.line([x,4,x,75],fill=c2); d.line([x+3 if x<300 else x-3,4,x+3 if x<300 else x-3,75],fill=c2)
    r=_tint(_ros,c); rw,rh=r.size
    for cx in (32,540): a.alpha_composite(r,(cx-rw//2,40-rh//2))
    ok.paste(a,(f*572,0))
save_dds(ok,OUT+'nsp_crew_ok.dds')
# 座位分段条 300×24 × 9 帧：座位 1（空/满）、2（0..2）、3（0..3）。红条纹 = 空座，绿条纹 = 已选
BW,BH=300,24; bar=Image.new('RGBA',(BW*9,BH),(0,0,0,0)); f=0
for seats in (1,2,3):
    for filled in range(seats+1):
        im=Image.new('RGBA',(BW,BH),DARK); d=ImageDraw.Draw(im)
        seg=BW/seats
        for k in range(seats):
            x0=int(k*seg); x1=int((k+1)*seg)-1
            fill,line=((GRNF,GRNL) if k<filled else (RED,REDL))
            d.rectangle([x0+2,2,x1-2,BH-3],fill=fill)
            for x in range(x0+3,x1-2,3): d.line([x,3,x,BH-4],fill=line)
            d.rectangle([x0,0,x1,BH-1],outline=CY)
        bar.paste(im,(f*BW,0)); f+=1
# r95e retired：save_dds(bar,OUT+'nsp_crew_bar.dds')
# r95c 头像 156×210 × 32 帧：1 空座（r95m 起为空头盔宇航服线稿）2 不适用（暗）3.. = 宇航员 0..29（tools/crew_portraits_src/k.png，维基百科 NASA 官方照，公有领域）
FW,FH=156,210; faces=Image.new('RGBA',(FW*32,FH),(0,0,0,0))
# r95m 空座：照 TNO El Tapado（无头西装线稿）画「空头盔宇航服」— 1px 青色线稿、无抗锯齿，只有国旗臂章 / NASA 徽标上色；底衬暗格线
e=Image.new('RGBA',(FW,FH),DARK); d=ImageDraw.Draw(e)
GL=(16,44,46,255)
for x in (52,104): d.line([x,0,x,FH],fill=GL)
for y in (70,140): d.line([0,y,FW,y],fill=GL)
SB=(4,8,10,255); WH=(226,232,232,255); FR=(198,64,70,255); FB=(44,72,160,255)
d.polygon([(56,104),(30,116),(20,140),(16,209),(140,209),(136,140),(126,116),(100,104)],fill=DARK,outline=CY)   # 躯干
d.line([36,150,38,209],fill=CY); d.line([120,150,118,209],fill=CY)              # 手臂内线
d.line([78,152,78,209],fill=CY2)                                                # 拉链
d.rectangle([62,128,94,152],outline=CY); d.rectangle([66,132,74,138],outline=CY2); d.rectangle([82,132,90,138],outline=CY2)   # 胸前控制盒
d.line([62,146,50,166],fill=CY); d.line([50,166,50,186],fill=CY); d.line([94,146,106,166],fill=CY); d.line([106,166,106,186],fill=CY)  # 软管
d.rectangle([56,98,100,108],fill=DARK,outline=CY)                               # 颈环
d.ellipse([44,28,112,100],fill=DARK,outline=CY)                                 # 头盔
d.ellipse([54,42,102,88],fill=SB,outline=CY2)                                   # 空面罩（无头，照 El Tapado）
d.arc([60,48,96,82],200,250,fill=WH)                                            # 面罩反光
d.rectangle([26,122,42,132],fill=WH,outline=CY)                                 # 星条旗臂章
for y in (124,128): d.line([27,y,41,y],fill=FR)
d.line([27,131,41,131],fill=FR); d.rectangle([27,123,33,127],fill=FB)
d.ellipse([104,122,118,136],fill=FB,outline=CY); d.line([106,132,116,126],fill=FR); d.point([(109,127),(113,131)],fill=WH)   # NASA 徽标
faces.paste(e,(0,0))
n=Image.new('RGBA',(FW,FH),(10,14,16,255)); d=ImageDraw.Draw(n); d.line([20,30,136,180],fill=(40,52,52,255),width=2); d.line([136,30,20,180],fill=(40,52,52,255),width=2)
faces.paste(n,(FW,0))
for k in range(30):
    g=ImageOps.autocontrast(Image.open('tools/crew_portraits_src/%d.png'%k).convert('L'),cutoff=1)   # r95d 黑白照，照 TNO 五月风暴卡牌
    faces.paste(g.convert('RGBA'),((k+2)*FW,0))
# r95t 用户：不要帧图 → 每张头像单独一个 dds，放 crew/faces/；GUI 用 properties image = "[GetNSPCrewFaceN]" 换 sprite（同 NSP_prog_badge 先例）
SUR=['shepard', 'grissom', 'glenn', 'carpenter', 'schirra', 'cooper', 'slayton', 'armstrong', 'borman', 'conrad', 'lovell', 'mcdivitt', 'see', 'stafford', 'white', 'young', 'aldrin', 'anders', 'bassett', 'bean', 'cernan', 'chaffee', 'collins', 'cunningham', 'eisele', 'freeman', 'gordon', 'schweickart', 'scott', 'williams']
os.makedirs(OUT+'faces',exist_ok=True)
for i,nm in enumerate(['nsp_crew_face_empty','nsp_crew_face_na']+['nsp_astro_%02d_%s'%(k,s) for k,s in enumerate(SUR)]):
    save_dds(faces.crop((i*FW,0,(i+1)*FW,FH)),OUT+'faces/'+nm+'.dds')
# r95h 卡框 133×244 × 2 帧（1 红 = 空座/不适用，2 青 = 已选；r95n 起直角双线框）：头像按钮 scale = 0.75 显示 117×158，贴图本身仍是原版 156×210
CW,CH=133,244
cf=Image.new('RGBA',(CW*2,CH),(0,0,0,0))
for f,(c,c2) in enumerate((((214,120,124,255),(120,60,64,255)),(CY,CY2))):
    cd=Image.new('RGBA',(CW,CH),(0,0,0,0)); d=ImageDraw.Draw(cd)
    d.rectangle([0,0,CW-1,CH-1],fill=(8,12,14,255),outline=c); d.rectangle([1,1,CW-2,CH-2],outline=c)   # r95n 直角双线框（照 El Tapado 肖像框）
    d.rectangle([3,3,CW-4,CH-4],outline=c2)
    for (a,b) in ((6,26),(192,214),(218,238)): d.rectangle([6,a,CW-7,b],fill=(4,6,8,255),outline=c,width=1)
    d.rectangle([7,29,125,188],outline=c,width=1)
    d.rectangle([8,30,124,187],fill=(0,0,0,0))
    cf.paste(cd,(f*CW,0))
save_dds(cf,OUT+'nsp_crew_card.dds')
print('ok')
# r95p 两侧装饰柱：取自用户提供的 TNO 原图 tools/crew_frame_src/map_bg.dds（墨西哥面板 487×295 线稿框）左右柱条 x 0..49 / 437..486
#   飘带 绿→蓝（星条旗），红白不动；柱身轮廓内填窗口底色（否则透明线稿压在地图上看不清）；最近邻 ×2 → 100×590
#   （r95l/r95o 脚本手画柱子已作废：用户说难看）
SRC=Image.open('tools/crew_frame_src/map_bg.dds').convert('RGBA')
REMAP={(36,95,61):(44,66,138)}
def strip(x0,x1):
    t=SRC.crop((x0,0,x1,SRC.size[1])); px=t.load(); w,h=t.size
    for y in range(h):
        xs=[x for x in range(w) if px[x,y][3]>0]
        for x in range(w):
            r,g,b,a=px[x,y]
            if a>0 and (r,g,b) in REMAP: px[x,y]=REMAP[(r,g,b)]+(a,)
        if xs:
            for x in range(xs[0],xs[-1]+1):
                if px[x,y][3]==0: px[x,y]=BG
    return t.resize((w*2,h*2),Image.NEAREST)
save_dds(strip(0,50),OUT+'nsp_crew_pillar.dds'); save_dds(strip(437,487),OUT+'nsp_crew_pillar_r.dds')
