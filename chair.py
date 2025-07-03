import numpy as np
import gcoordinator as gc

# �֎q�̃T�C�Y�p�����[�^
TOTAL_HEIGHT = 350  # mm
BASE_RADIUS = 175   # mm�i���a350mm�j
WALL_THICKNESS = 50  # mm�i����3cm�j
LAYER_HEIGHT = 12.5 # mm

# �g�͗l�̐ݒ�
WAVE_COUNT =25         # �������̔g�̐� 2�̔{����
WAVE_DEPTH = 10          # mm
LAYER = int(TOTAL_HEIGHT // LAYER_HEIGHT)

# ���ʂ��������Ɍ����Ĉ������̂ŁA�� �f���ł͉�������
full_object = []

for height in range(LAYER):
    # �g�̌`��i���˂�j
    arg = np.linspace(0, np.pi*2, int(WAVE_COUNT*8.5+1))
    # ���a�F�ꂪ�����A��֍s���قǏ����ׂ��Ȃ�i����{������j
    taper = -0.2  # �e�[�p�p�i�X�΁j
    rad = BASE_RADIUS + taper * height * LAYER_HEIGHT
    # sin�g�𔼌a�ɂQ�����t�^
    rad +=  20 * np.sin(arg*2 + 0.1*height)

    # �҂ݍ��݌`��̂��߂�sin�g
    wave_offset = WAVE_DEPTH * np.sin(arg*(WAVE_COUNT+0.5) + height*np.pi)
    rad += wave_offset

    # �~�`�̊O�ǃp�X�i�O����`��j
    #x = rad * np.cos(arg)
    #y = rad * np.sin(arg)
    
    # �ȉ~�`�̊O�`�p�X
    x = rad * np.cos(arg)
    y = (rad+50) * np.sin(arg)

    if height >= 4:
        # 5�w����̓X�p�C�������[�h�ŊO�ǂ̂�
        z = np.linspace(height*LAYER_HEIGHT+0.15, (height+1)*LAYER_HEIGHT+0.15, int(WAVE_COUNT*8.5+1))
        outer_path = gc.Path(x, y, z)
        full_object.append(outer_path)
    
    else:
        # 4�w�܂ł͍��ʂ����
        z = np.full_like(x, (height+1)*LAYER_HEIGHT)
        outer_path = gc.Path(x, y, z)
        full_object.append(outer_path)

        bottom = gc.line_infill(outer_path, infill_distance = WALL_THICKNESS*0.8, angle = np.pi/4 + np.pi/4 *height)
        full_object.append(bottom)

gc.gui_export(full_object)
