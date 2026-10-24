# r81b：帮助遮罩去掉青色高亮框（青框被 scale=2 拉伸后边缘发虚很显眼，暗底边缘发虚看不出）。
# 保持 r69 半分辨率 550x359/帧 + gui scale = 2（贴图宽 3850，不占 8192 上限）。
# 青框像素改成暗底色 (2,8,10,190)。只从 work/r81/bak 读原图，可重复运行。
import struct, numpy as np
from PIL import Image
SRC='/workspace/work/r81/bak/nsp_help_overlay.dds'
DST='gfx/interface/NSP/help/nsp_help_overlay.dds'
a=np.array(Image.open(SRC).convert('RGBA'))
cy=(a[...,0]==132)&(a[...,1]==220)&(a[...,2]==210)
a[cy]=(2,8,10,190)
H,W=a.shape[:2]
hdr=struct.pack('<4s31I',b'DDS ',124,0x100F,H,W,W*4,0,1,*([0]*11),32,0x41,0,32,0xFF0000,0xFF00,0xFF,0xFF000000,0x1000,0,0,0,0)
open(DST,'wb').write(hdr+a[...,[2,1,0,3]].tobytes())
print(W,H,int(cy.sum()))
