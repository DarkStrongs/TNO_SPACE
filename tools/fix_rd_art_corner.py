# r80：给 TNO 科技边框右上角的状态方块（帧内 x216..236、y3..22）让位。
# 处理 nsp_rd_tech_0..5.dds 每帧（239×117）：
#   - 右上第一行注释（y14..23）整体左移 16px；
#   - 擦掉科技图自带竖线在 y0..23 那段（x229..236），竖线从 y24 往下保留。
# 只跑一次！处理过的分类记在 tools/fix_rd_art_corner.done，再跑会跳过。原图备份在 work/r80/bak/art/。
import os, struct
from PIL import Image
RD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gfx', 'interface', 'NSP', 'rd')
def dds(img, path):
    w, h = img.size
    hdr = b'DDS ' + struct.pack('<7I', 124, 0x100F, h, w, w*4, 0, 0) + b'\0'*44 \
        + struct.pack('<8I', 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000) \
        + struct.pack('<I', 0x1000) + b'\0'*16
    open(path, 'wb').write(hdr + img.convert('RGBA').tobytes('raw', 'BGRA'))
DONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fix_rd_art_corner.done')
done = set(open(DONE).read().split()) if os.path.exists(DONE) else set()
for t in range(6):
    p = os.path.join(RD, 'nsp_rd_tech_%d.dds' % t)
    if str(t) in done: continue
    im = Image.open(p).convert('RGBA'); px = im.load()
    for f in range(im.size[0] // 239):
        ox = f * 239; bg = px[ox + 200, 5]
        band = im.crop((ox + 30, 14, ox + 230, 24))
        for y in range(14, 24):
            for x in range(ox + 14, ox + 237): px[x, y] = bg
        im.paste(band, (ox + 14, 14))
        for y in range(0, 24):
            for x in range(ox + 229, ox + 237): px[x, y] = bg
    dds(im, p); open(DONE, 'a').write('%d\n' % t)
    print('fixed', p)
