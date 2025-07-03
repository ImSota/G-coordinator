import numpy as np
import gcoordinator as gc

TOTAL_HEIGHT = 350  # mm
BASE_RADIUS = 175   # mm
WALL_THICKNESS = 50  # mm
LAYER_HEIGHT = 12.5 # mm

WAVE_COUNT =25
WAVE_DEPTH = 10
LAYER = int(TOTAL_HEIGHT // LAYER_HEIGHT)

full_object = []

for height in range(LAYER):
    arg = np.linspace(0, np.pi*2, int(WAVE_COUNT*8.5+1))
    taper = -0.2
    rad = BASE_RADIUS + taper * height * LAYER_HEIGHT
    rad +=  20 * np.sin(arg*2 + 0.1*height)

    wave_offset = WAVE_DEPTH * np.sin(arg*(WAVE_COUNT+0.5) + height*np.pi)
    rad += wave_offset

    #x = rad * np.cos(arg)
    #y = rad * np.sin(arg)
    
    x = rad * np.cos(arg)
    y = (rad+50) * np.sin(arg)

    if height >= 4:
        z = np.linspace(height*LAYER_HEIGHT+0.15, (height+1)*LAYER_HEIGHT+0.15, int(WAVE_COUNT*8.5+1))
        outer_path = gc.Path(x, y, z)
        full_object.append(outer_path)
    
    else:
        z = np.full_like(x, (height+1)*LAYER_HEIGHT)
        outer_path = gc.Path(x, y, z)
        full_object.append(outer_path)

        bottom = gc.line_infill(outer_path, infill_distance = WALL_THICKNESS*0.8, angle = np.pi/4 + np.pi/4 *height)
        full_object.append(bottom)

gc.gui_export(full_object)
