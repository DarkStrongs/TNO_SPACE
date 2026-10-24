# r85：地图发射场标记 16x16 ×2 帧（1 空闲青色 / 2 占用琥珀）。输出 gfx/interface/NSP/home/solar_system/earth_map/nsp_lsite_marker.dds
import struct, os
from PIL import Image, ImageDraw
def dds(img, path):
    w, h = img.size
    hdr = b'DDS ' + struct.pack('<7I', 124, 0x100F, h, w, w*4, 0, 0) + b'\0'*44 \
        + struct.pack('<8I', 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000) \
        + struct.pack('<I', 0x1000) + b'\0'*16
    open(path, 'wb').write(hdr + img.convert('RGBA').tobytes('raw', 'BGRA'))
def frame(ring, body, glow):
    S = 4; im = Image.new('RGBA', (24*S, 24*S), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.ellipse([1*S, 1*S, 23*S-1, 23*S-1], fill=glow)
    d.ellipse([3*S, 3*S, 21*S-1, 21*S-1], fill=(2,8,10,220), outline=ring, width=int(1.5*S))
    # 火箭：箭体 + 尖头 + 尾翼 + 尾焰
    d.rectangle([11*S, 8*S, 13*S-1, 16*S-1], fill=body)
    d.polygon([(11*S, 8*S), (12*S, 5*S), (13*S, 8*S)], fill=body)
    d.polygon([(11*S, 13*S), (9*S, 17*S), (11*S, 16*S)], fill=body)
    d.polygon([(13*S, 13*S), (15*S, 17*S), (13*S, 16*S)], fill=body)
    d.polygon([(11*S+2, 16*S), (12*S, 19*S), (13*S-2, 16*S)], fill=(255,190,90,230))
    return im.resize((16, 16), Image.LANCZOS)
sheet = Image.new('RGBA', (32, 16))   # r85b：24px 太大、东海岸三个发射场糊成一团 → 16px
sheet.paste(frame((97,192,187,255), (210,245,240,255), (97,192,187,60)), (0, 0))
sheet.paste(frame((232,160,60,255), (255,215,150,255), (232,160,60,90)), (16, 0))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dds(sheet, os.path.join(root, 'gfx/interface/NSP/home/solar_system/earth_map/nsp_lsite_marker.dds'))
sheet.resize((128, 64), Image.NEAREST).save('/tmp/lsite.png')
