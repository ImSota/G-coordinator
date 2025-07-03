import numpy as np
import gcoordinator as gc

# 椅子のサイズパラメータ
TOTAL_HEIGHT = 350  # mm
BASE_RADIUS = 175   # mm（直径350mm）
WALL_THICKNESS = 50  # mm（厚み3cm）
LAYER_HEIGHT = 12.5 # mm

# 波模様の設定
WAVE_COUNT =25         # 周方向の波の数 2の倍数で
WAVE_DEPTH = 10          # mm
LAYER = int(TOTAL_HEIGHT // LAYER_HEIGHT)

# 座面から上方向に向けて印刷するので、モ デルでは下が座面
full_object = []

for height in range(LAYER):
    # 波の形状（うねり）
    arg = np.linspace(0, np.pi*2, int(WAVE_COUNT*8.5+1))
    # 半径：底が厚く、上へ行くほど少し細くなる（安定＋印刷性）
    taper = -0.2  # テーパ角（傾斜）
    rad = BASE_RADIUS + taper * height * LAYER_HEIGHT
    # sin波を半径に２周期付与
    rad +=  20 * np.sin(arg*2 + 0.1*height)

    # 編み込み形状のためのsin波
    wave_offset = WAVE_DEPTH * np.sin(arg*(WAVE_COUNT+0.5) + height*np.pi)
    rad += wave_offset

    # 円形の外壁パス（外側を描画）
    #x = rad * np.cos(arg)
    #y = rad * np.sin(arg)
    
    # 楕円形の外形パス
    x = rad * np.cos(arg)
    y = (rad+50) * np.sin(arg)

    if height >= 4:
        # 5層からはスパイラルモードで外壁のみ
        z = np.linspace(height*LAYER_HEIGHT+0.15, (height+1)*LAYER_HEIGHT+0.15, int(WAVE_COUNT*8.5+1))
        outer_path = gc.Path(x, y, z)
        full_object.append(outer_path)
    
    else:
        # 4層までは座面を印刷
        z = np.full_like(x, (height+1)*LAYER_HEIGHT)
        outer_path = gc.Path(x, y, z)
        full_object.append(outer_path)

        bottom = gc.line_infill(outer_path, infill_distance = WALL_THICKNESS*0.8, angle = np.pi/4 + np.pi/4 *height)
        full_object.append(bottom)

gc.gui_export(full_object)
