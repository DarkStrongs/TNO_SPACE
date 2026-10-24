# r79：小科技（只给加成、不解锁东西）的方卡图（r80 起 72×72），照 TNO 小科技图标：左上短英文标签 + 线稿。
# 线稿从大卡科技图 rd/tech/nsp_rdart_<id>.dds（239×117）中间区域自动裁出、加粗后缩放。
# r95t 起输出单张 rd/small/nsp_rdsart_<id>.dds（不再是帧图；NSP_rd_sart 只剩数据意义）。
# 可重跑；改 SMALL 列表后要同步 NSP_rd_small_init（common/scripted_effects/NSP_rd_effects.txt）。
import os, re, struct
from PIL import Image, ImageFilter, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RD = os.path.join(ROOT, 'gfx', 'interface', 'NSP', 'rd')
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VT323-Regular.ttf')
# (项目 id, 标签)
SMALL = [(8,'J-2'),(18,'CSM II'),(21,'MERCURY'),(22,'G4C'),(24,'AMU'),(25,'A7L'),(27,'14 DAY'),(28,'RECOVERY'),
         (33,'LOR'),(34,'GEM CPU'),(35,'AGC'),(39,'DSN'),(44,'RANGER'),(46,'ORBITER'),(50,'LC-14'),(51,'LC-19'),
         (54,'MCC'),(56,'TEST STD'),(57,'MICHOUD'),(58,'VAB'),(59,'INT-21'),(62,'RIFT'),(69,'AUTODOCK'),(70,'DSN 70M'),
         (74,'LC-39B'),(75,'SLC-6'),(76,'A7LB'),(77,'NYLON'),(78,'VISOR'),(79,'LCG'),(80,'PLSS'),(81,'BETA'),
         (82,'EMU'),(84,'EVA TOOL'),(85,'GEOLOGY')]
FW = 72   # r80：和 TNO 小科技边框 nsp_rd_frame_s（72×72）同尺寸；标签 ≤ 46px，避开右上角状态方块
BG = (5, 15, 28)

def items():
    src = ''
    for f in ('NSP_rd_effects.txt',):
        src += open(os.path.join(ROOT, 'common', 'scripted_effects', f), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'# (\d+) [^\n]*\n\t+(add_to_array[^\n]+)', src):
        kv = dict(re.findall(r'NSP_rd_(\w+) = (-?[\d.]+)', m.group(2)))
        out[int(m.group(1))] = {k: int(float(v)) for k, v in kv.items()}
    return out

def dds(img, path):
    w, h = img.size
    hdr = b'DDS ' + struct.pack('<7I', 124, 0x100F, h, w, w*4, 0, 0) + b'\0'*44 \
        + struct.pack('<8I', 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000) \
        + struct.pack('<I', 0x1000) + b'\0'*16
    open(path, 'wb').write(hdr + img.convert('RGBA').tobytes('raw', 'BGRA'))

def bright(p): return p[3] > 0 and (p[0] + p[1] + p[2]) > 160

def span(counts, gap=5):
    # 最长的连续非空段（允许 gap 以内的空隙），用来甩掉引线的零星碎点
    best = (0, 0, -1); st = None; last = None; tot = 0
    for i, c in enumerate(counts + [0] * (gap + 1)):
        if c:
            if st is None or i - last > gap: st, tot = i, 0
            last = i; tot += c
            if tot > best[2]: best = (st, last, tot)
    return best[0], best[1]

def icon(art, label, font):
    # 中间区域：去掉标题行（y<34）、底部说明栏（y>94）和右侧边框线（x>228）
    reg = art.crop((4, 34, 228, 95)).convert('RGBA')
    px = reg.load(); W, H = reg.size
    for y in range(H):              # 底色抠成透明，只留线
        for x in range(W):
            if not bright(px[x, y]): px[x, y] = (0, 0, 0, 0)
    x0, x1 = span([sum(1 for y in range(H) if px[x, y][3]) for x in range(W)])
    y0, y1 = span([sum(1 for x in range(x0, x1 + 1) if px[x, y][3]) for y in range(H)], 3)
    d = reg.crop((max(0, x0 - 1), max(0, y0 - 1), min(W, x1 + 2), min(H, y1 + 2)))
    s = min(62 / d.size[0], 48 / d.size[1], 1.0)
    if s < 0.75: d = d.filter(ImageFilter.MaxFilter(3))     # 缩得多就先加粗，免得线断
    d = d.resize((max(1, round(d.size[0]*s)), max(1, round(d.size[1]*s))), Image.LANCZOS)
    f = Image.new('RGBA', (FW, FW), BG + (255,))
    f.alpha_composite(d, ((FW - d.size[0]) // 2, 19 + (48 - d.size[1]) // 2))
    ImageDraw.Draw(f).text((5, 1), label, font=font, fill=(97, 192, 187, 255))
    return f

def main():
    # r95t 不用帧图：读 rd/tech/nsp_rdart_<id>.dds（大卡单张），写 rd/small/nsp_rdsart_<id>.dds（方卡单张）
    #   新增方卡：SMALL 里加一行，再在 NSP_rd.gfx 加 GFX_NSP_rdsart_<id>、loc 加 NSP_RDSART_<id>、NSP_rd_small_init 里标 small
    font = ImageFont.truetype(FONT, 14)
    for i, lab in SMALL:
        if i == 46: continue   # r93 起月球轨道器是大卡
        art = Image.open(os.path.join(RD, 'tech', 'nsp_rdart_%02d.dds' % i)).convert('RGBA')
        dds(icon(art, lab, font), os.path.join(RD, 'small', 'nsp_rdsart_%02d.dds' % i))
    print('small icons', len(SMALL) - 1)

if __name__ == '__main__':
    main()
