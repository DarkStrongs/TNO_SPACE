# r78b：研发树动态连线贴图生成器（可重跑）。照 TNO 科技树：2px 实线、无端点、颜色 = 子项目状态。
# 只有改线条样式 / 颜色才需要重跑；改前置不用。
# r79：加 TAIL = 小科技（方卡 x10..83）的出线，从卡右缘 x84 补到 x252，接上 H 段的起点（父卡格位 x253）。
#   帧 = 1 空 + c(0..3)，元素在小卡条目 (84,67)。
# 输出 gfx/interface/NSP/rd/links/nsp_rdl_{h,vu,vd,lu,ld}.dds（未压缩 A8R8G8B8，无 mip）
# 颜色 c（子项目状态）：0 锁定 TNO 红 / 1 可研发 TNO 青 / 2 研发中 黄 / 3 已完成 TNO 绿（取自 TNO 科技树实机录屏）
# r80：卡片换成 TNO 科技边框（大卡 239×117 在 (10,12) → x10..248、y12..128；小卡 72×72 在 (10,34) → x10..81），
#   H 起点改成 x249，L 竖干从 y129 / y11 起，TAIL 改成 x82..248（167 宽）。
# 几何（相对子卡片条目原点；格位 263×139，旧卡片 x10..252、y10..130，中线 y69..70）：
#   Z 形（dx >= 2，或 L 形路上有卡）：H = 父卡右缘沿父行到拐点 x-4..-3；VU / VD = 拐点竖线 + 进卡短线
#     H  帧 = 1 空 + c×dx(1..4)，元素 x-802，y = 67 - dy*139（每个 dy 一个元素）
#     VU 帧 = 1 空 + c×dy(0..3)，元素 (-4,-349)；VD 帧 = 1 空 + c×|dy|(1..3)，元素 (-4,67)
#   L 形（dx = 1，TNO 分叉写法）：从父卡底边 / 顶边 x = 父卡左缘 + 200 竖直落下，再横着进子卡左边中线
#     LU（父在上）帧 = 1 空 + c×dy(1..3)，元素 (-54,-286)；LD（父在下）帧 = 1 空 + c×|dy|(1..3)，元素 (-54,67)
import struct, os
from PIL import Image, ImageDraw
SW, SH = 263, 139
COL = [(212,133,137,255), (97,192,187,255), (220,218,80,255), (139,228,147,255)]
NC = len(COL)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gfx', 'interface', 'NSP', 'rd', 'links')

def dds(img, path):
    w, h = img.size
    hdr = b'DDS ' + struct.pack('<7I', 124, 0x100F, h, w, w*4, 0, 0) + b'\0'*44 \
        + struct.pack('<8I', 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000) \
        + struct.pack('<I', 0x1000) + b'\0'*16
    open(path, 'wb').write(hdr + img.convert('RGBA').tobytes('raw', 'BGRA'))

def strip(frames, fw, fh, name):
    assert fw*len(frames) <= 16384, name
    im = Image.new('RGBA', (fw*len(frames), fh), (0,0,0,0))
    for i, fn in enumerate(frames):
        if fn: fn(ImageDraw.Draw(im), i*fw)
    dds(im, os.path.join(OUT, name))
    return len(frames)

R = lambda d, c, x0, y0, x1, y1: d.rectangle([x0, y0, x1, y1], fill=COL[c])

# H：帧宽 800，右缘 = 条目 x -2；线占帧内 y 2..3
def h(c, dx):
    def f(d, ox):
        R(d, c, ox + 800 - (dx*SW - 251), 2, ox + 799, 3)   # r80：父卡右缘 x248 → 从 x249 起
    return f
# VU：帧顶 = 条目 y -349，子中线在帧内 y 418；帧宽 14 = 条目 x -4..9
def vu(c, dy):
    def f(d, ox):
        R(d, c, ox, 418 - dy*SH, ox+1, 419); R(d, c, ox, 418, ox+13, 419)
    return f
def vd(c, a):
    def f(d, ox):
        R(d, c, ox, 2, ox+1, 3 + a*SH); R(d, c, ox, 2, ox+13, 3)
    return f
# LU：帧顶 = 条目 y -286，帧左 = 条目 x -54；竖线 x -54..-53；父卡底边下一行 = 条目 y 131 - dy*139
def lu(c, dy):
    def f(d, ox):
        R(d, c, ox, 129 - dy*SH + 288, ox+1, 70 + 288); R(d, c, ox, 69 + 288, ox+63, 70 + 288)   # r80：帧顶改 -288
    return f
# LD：帧顶 = 条目 y 67；父卡顶边上一行 = 条目 y 9 + |dy|*139
def ld(c, a):
    def f(d, ox):
        R(d, c, ox, 2, ox+1, 11 + a*SH - 67); R(d, c, ox, 2, ox+63, 3)
    return f

n = [strip([None] + [h(c, x) for c in range(NC) for x in range(1, 5)], 800, 6, 'nsp_rdl_h.dds'),
     strip([None] + [vu(c, y) for c in range(NC) for y in range(0, 4)], 14, 423, 'nsp_rdl_vu.dds'),
     strip([None] + [vd(c, y) for c in range(NC) for y in range(1, 4)], 14, 423, 'nsp_rdl_vd.dds'),
     strip([None] + [lu(c, y) for c in range(NC) for y in range(1, 4)], 64, 360, 'nsp_rdl_lu.dds'),
     strip([None] + [ld(c, y) for c in range(NC) for y in range(1, 4)], 64, 362, 'nsp_rdl_ld.dds'),
     strip([None] + [(lambda c: (lambda d, ox: R(d, c, ox, 2, ox+166, 3)))(c) for c in range(NC)], 167, 6, 'nsp_rdl_tail.dds')]
print('frames h/vu/vd/lu/ld/tail', n)
