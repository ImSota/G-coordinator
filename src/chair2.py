# -*- coding: utf-8 -*-
import numpy as np
import gcoordinator as gc

TOTAL_HEIGHT = 350
BASE_RADIUS = 125
WALL_THICKNESS = 50
LAYER_HEIGHT = 12.5

WAVE_COUNT = 25
WAVE_DEPTH = 5
LAYER = int(TOTAL_HEIGHT // LAYER_HEIGHT)

# New constant for enlarging the base ellipse
ENLARGEMENT_FOR_BASE = WAVE_DEPTH + 15

# New constant for desired infill line spacing
INFILL_LINE_SPACING = 100 # mm

full_object = []

def generate_interweaving_r_sqrt_theta_infill(radius_x, radius_y, center_x, center_y, z_height, start_point_x, start_point_y, desired_spacing):
    max_overall_radius = max(radius_x, radius_y)

    num_turns = int(np.ceil(max_overall_radius / desired_spacing)) 
    if num_turns == 0:
        num_turns = 1 

    num_points_per_turn = 50 
    total_points = num_turns * num_points_per_turn

    theta_max_extent = num_turns * 2 * np.pi

    a_coeff = max_overall_radius / theta_max_extent 

    # Spiral 1: Inward-bound (ê∂ê¨ÇÕäOë§Ç©ÇÁçsÇ¢ÅAå„Ç≈îΩì])
    theta_base_s1 = np.linspace(0.01, theta_max_extent, total_points) 
    
    current_end_angle_outward_s1 = theta_base_s1[-1] 
    
    target_start_angle = np.arctan2((start_point_y - center_y) / radius_y, (start_point_x - center_x) / radius_x)
    
    angle_offset_s1 = target_start_angle - current_end_angle_outward_s1
    
    theta_s1_adjusted = theta_base_s1 + angle_offset_s1
    
    r_vals_s1 = a_coeff * theta_base_s1

    x_s1_outward = center_x + (r_vals_s1 / max_overall_radius) * radius_x * np.cos(theta_s1_adjusted)
    y_s1_outward = center_y + (r_vals_s1 / max_overall_radius) * radius_y * np.sin(theta_s1_adjusted)

    infill_path_inward = gc.Path(x_s1_outward[::-1], y_s1_outward[::-1], np.full_like(x_s1_outward, z_height))

    # Spiral 2: Outward-bound (êDÇËåÇ∫ÇÈóÜê˘)
    theta_base_s2 = np.linspace(0.01, theta_max_extent, total_points)
    theta_s2_adjusted = theta_base_s2 + (theta_s1_adjusted[0] + np.pi)

    r_vals_s2 = a_coeff * theta_base_s2

    x_s2_outward = center_x + (r_vals_s2 / max_overall_radius) * radius_x * np.cos(theta_s2_adjusted)
    y_s2_outward = center_y + (r_vals_s2 / max_overall_radius) * radius_y * np.sin(theta_s2_adjusted)

    infill_path_outward = gc.Path(x_s2_outward, y_s2_outward, np.full_like(x_s2_outward, z_height))
    
    all_x = np.concatenate((infill_path_inward.x, infill_path_outward.x[1:]))
    all_y = np.concatenate((infill_path_inward.y, infill_path_outward.y[1:]))
    all_z = np.concatenate((infill_path_inward.z, infill_path_outward.z[1:]))

    return gc.Path(all_x, all_y, all_z)


for height in range(LAYER):
    arg_wavy = np.linspace(0, 2 * np.pi, int(WAVE_COUNT * 8.5 + 1))
    taper = -0.2
    rad_base_for_wavy = BASE_RADIUS + taper * height * LAYER_HEIGHT
    rad_wavy_amplitude = 20 * np.sin(arg_wavy * 2 + 0.1 * height)
    wave_offset_wavy = WAVE_DEPTH * np.sin(arg_wavy * (WAVE_COUNT + 1) + height * np.pi)
    
    rad_final_wavy = rad_base_for_wavy + rad_wavy_amplitude + wave_offset_wavy

    x_wavy_contour = rad_final_wavy * np.cos(arg_wavy)
    y_wavy_contour = (rad_final_wavy + 25) * np.sin(arg_wavy)

    z_top = (height + 1) * LAYER_HEIGHT

    if height == 0:
        prev_last_x = None 
        prev_last_y = None
    else:
        prev_last_x = full_object[-1].x[-1]
        prev_last_y = full_object[-1].y[-1]


    current_contour_x = []
    current_contour_y = []
    
    if height < 3: 
        # Elliptical outer wall for the "seat" layers, enlarged
        current_radius_x_ellipse = BASE_RADIUS + ENLARGEMENT_FOR_BASE
        current_radius_y_ellipse = (BASE_RADIUS + 25) + ENLARGEMENT_FOR_BASE
        
        angles_full_circle = np.linspace(0, 2 * np.pi, 400, endpoint=False)
        current_contour_x = current_radius_x_ellipse * np.cos(angles_full_circle)
        current_contour_y = current_radius_y_ellipse * np.sin(angles_full_circle)
        
    else: # height >= 3 (Wavy layers)
        current_contour_x = x_wavy_contour
        current_contour_y = y_wavy_contour


    if height == 0:
        start_idx = 0 
    else:
        distances_to_prev_end = np.sqrt((current_contour_x - prev_last_x)**2 + (current_contour_y - prev_last_y)**2)
        start_idx = np.argmin(distances_to_prev_end)
    
    x_reordered_contour = np.concatenate((current_contour_x[start_idx:], current_contour_x[:start_idx]))
    y_reordered_contour = np.concatenate((current_contour_y[start_idx:], current_contour_y[:start_idx]))
    
    x_reordered_contour = np.append(x_reordered_contour, x_reordered_contour[0])
    y_reordered_contour = np.append(y_reordered_contour, y_reordered_contour[0])
    
    # Spiral mode applies for height >= 3 and before the very last layer
    if height >= 3 and height < (LAYER - 1): 
        num_points = len(x_reordered_contour)
        z_offset_amount = LAYER_HEIGHT / 2 
        z_start = ((height + 1) * LAYER_HEIGHT) - z_offset_amount 
        z_end = z_start + LAYER_HEIGHT 
        z_reordered_contour = np.linspace(z_start, z_end, num_points)
    else: # height < 3 ÇÃëwÅAÇ‹ÇΩÇÕç≈å„ÇÃëw (height == LAYER - 1)
        # ç≈å„ÇÃëwÇÃèÍçáÇÃÇ›ZÇí≤êÆÇµÇƒïΩÇÁÇ…Ç∑ÇÈ
        if height == (LAYER - 1):
            # ç≈èIëwÇÃZç¿ïWÇ0.5 * LAYER_HEIGHTÇæÇØâ∫Ç∞ÇÈ
            z_fixed_for_last_layer = z_top - (LAYER_HEIGHT / 2)
            z_reordered_contour = np.full_like(x_reordered_contour, z_fixed_for_last_layer)
        else: # 3ëwñ⁄ÇÊÇËëOÇÃÉtÉâÉbÉgÇ»ëw
            z_reordered_contour = np.full_like(x_reordered_contour, z_top)

    outer_wall_path = gc.Path(x_reordered_contour, y_reordered_contour, z_reordered_contour)
    full_object.append(outer_wall_path)

    if height < 3: 
        infill_path = generate_interweaving_r_sqrt_theta_infill(
            current_radius_x_ellipse, current_radius_y_ellipse, 0, 0, z_top, outer_wall_path.x[-1], outer_wall_path.y[-1], INFILL_LINE_SPACING
        )
        
        full_object.append(infill_path)

gc.gui_export(full_object)