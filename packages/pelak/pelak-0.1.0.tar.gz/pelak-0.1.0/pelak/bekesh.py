# pelak/bekesh.py

from PIL import Image, ImageDraw, ImageFont
import re
import os
from .assets import resource_path

def bekesh(
    plate_code: str,
    out_path: str = None,
    show_img: bool = False
):
    """
    Generate an Iranian license plate image based on code.
    :param plate_code: e.g., '12پ34511', '91معلول12347', ...
    :param out_path: Output path to save image (optional)
    :param show_img: Show output image if True (default False)
    :return: PIL.Image instance
    """

    # Plate input validation
    if not isinstance(plate_code, str):
        raise ValueError("plate_code must be a string.")
    if len(plate_code) < 6 or len(plate_code) > 13:
        raise ValueError("plate_code length is invalid. Expected 6 to 13 characters.")

    data_dir = resource_path('data')
    templates = {
        'normal' : os.path.join(data_dir, 'gha.png'),
        'aleph'  : os.path.join(data_dir, 'alef.png'),
        'malul'  : os.path.join(data_dir, 'malul.png'),
        'teh'    : os.path.join(data_dir, 'taxi.png'),
        'ain'    : os.path.join(data_dir, 'ain.png'),
        'police' : os.path.join(data_dir, 'police.png'),
        'sepah'  : os.path.join(data_dir, 'sepah.png')
    }
    font_path = os.path.join(data_dir, 'Far_RoyaBd.ttf')
    letter_type = None

    # Plate regexes
    regex_structures = [
        ("malul",  r"^(\d{2})معلول(\d{3})(\d{2,3})$"),
        ("aleph",  r"^(\d{2})الف(\d{3})(\d{2,3})$"),
        ("teh",    r"^(\d{2})ت(\d{3})(\d{2,3})$"),
        ("ain",    r"^(\d{2})ع(\d{3})(\d{2,3})$"),
        ("police", r"^(\d{2})پ(\d{3})(\d{2,3})$"),
        ("sepah",  r"^(\d{2})ث(\d{3})(\d{2,3})$"),
        ("normal", r"^(\d{2})([آ-ی])(\d{3})(\d{2,3})$"),
    ]

    for l_type, regex in regex_structures:
        match = re.match(regex, plate_code)
        if match:
            letter_type = l_type
            parts = match.groups()
            break

    if not letter_type:
        raise ValueError("Invalid plate_code format or unsupported middle letter.")

    # Parse extracted parts for image logic
    if letter_type == "normal":
        number_left, letter, number_right, state_code = parts
    else:
        number_left, number_right, state_code = parts

    # Range check for numeric parts
    for num in [number_left, number_right, state_code]:
        if not num.isdigit():
            raise ValueError("Invalid numeric part detected in plate_code.")

    # Layout definitions (unchanged)
    layout_normal = {
        "font_size": 103, "state_ratio": 0.95, "white_x1_ratio": 0.052, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 24, "num_y_offset": 17,
        "letter_offset_y": -22, "space1": 22, "space2": 22, "state_offset_x": -20, "font_color": "black"
    }
    layout_aleph = {
        "font_size": 100, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 18, "num_y_offset": 16,
        "aleph_space": 120, "state_offset_x": -22, "font_color": "white"
    }
    layout_malul = {
        "font_size": 103, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 10, "num_y_offset": 16,
        "malul_space": 120, "state_offset_x": -22, "font_color": "black"
    }
    layout_teh = {
        "font_size": 103, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 10, "num_y_offset": 16,
        "teh_space": 120, "state_offset_x": -22, "font_color": "black"
    }
    layout_ain = {
        "font_size": 103, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 10, "num_y_offset": 16,
        "ain_space": 120, "state_offset_x": -22, "font_color": "black"
    }
    layout_police = {
        "font_size": 103, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 10, "num_y_offset": 16,
        "police_space": 120, "state_offset_x": -22, "font_color": "white"
    }
    layout_sepah = {
        "font_size": 103, "state_ratio": 1.02, "white_x1_ratio": 0.051, "white_x2_ratio": 0.87,
        "white_y1_ratio": 0.01, "white_y2_ratio": 0.99, "main_offset_x": 10, "num_y_offset": 16,
        "sepah_space": 120, "state_offset_x": -22, "font_color": "white"
    }

    layout_dict = {
        'normal' : layout_normal,
        'aleph'  : layout_aleph,
        'malul'  : layout_malul,
        'teh'    : layout_teh,
        'ain'    : layout_ain,
        'police' : layout_police,
        'sepah'  : layout_sepah
    }
    layout = layout_dict[letter_type]

    # Load image template
    if not os.path.isfile(templates[letter_type]):
        raise FileNotFoundError(f"Template file '{templates[letter_type]}' not found.")
    img = Image.open(templates[letter_type])
    width, height = img.size
    draw = ImageDraw.Draw(img)

    white_x1 = int(width * layout["white_x1_ratio"])
    white_x2 = int(width * layout["white_x2_ratio"])
    white_y1 = int(height * layout["white_y1_ratio"])
    white_y2 = int(height * layout["white_y2_ratio"])
    white_width = white_x2 - white_x1

    font_main = ImageFont.truetype(font_path, layout["font_size"])
    font_state = ImageFont.truetype(font_path, int(layout["font_size"] * layout["state_ratio"]))
    main_h_center = white_y1 + ((white_y2 - white_y1) - layout["font_size"]) // 2

    just_num_types = ['aleph', 'malul', 'teh', 'ain', 'police', 'sepah']

    if letter_type in just_num_types:
        num_left_bbox  = draw.textbbox((0, 0), number_left, font=font_main)
        num_right_bbox = draw.textbbox((0, 0), number_right, font=font_main)
        space_key = [k for k in ['aleph_space','malul_space','teh_space','ain_space','police_space','sepah_space'] if k in layout][0]
        side_space = layout.get(space_key, 100)
        main_w = (num_left_bbox[2] - num_left_bbox[0]) + side_space + (num_right_bbox[2] - num_right_bbox[0])
        main_x = white_x1 + (white_width - main_w) // 2 - layout["main_offset_x"]
        num_y = main_h_center + layout["num_y_offset"]
        num_left_x = main_x
        num_right_x = num_left_x + (num_left_bbox[2] - num_left_bbox[0]) + side_space
        draw.text((num_left_x, num_y), number_left, font=font_main, fill=layout["font_color"])
        draw.text((num_right_x, num_y), number_right, font=font_main, fill=layout["font_color"])
    else:
        num_left_bbox  = draw.textbbox((0, 0), number_left, font=font_main)
        letter_bbox    = draw.textbbox((0, 0), letter, font=font_main)
        num_right_bbox = draw.textbbox((0, 0), number_right, font=font_main)
        main_w = (num_left_bbox[2] - num_left_bbox[0]) + layout["space1"] + \
                (letter_bbox[2] - letter_bbox[0]) + layout["space2"] + \
                (num_right_bbox[2] - num_right_bbox[0])
        main_x = white_x1 + (white_width - main_w) // 2 - layout["main_offset_x"]
        num_y = main_h_center + layout["num_y_offset"]
        num_left_x  = main_x
        letter_x    = num_left_x + (num_left_bbox[2] - num_left_bbox[0]) + layout["space1"]
        num_right_x = letter_x + (letter_bbox[2] - letter_bbox[0]) + layout["space2"]
        draw.text((num_left_x, num_y), number_left, font=font_main, fill=layout["font_color"])
        draw.text((letter_x, num_y + layout["letter_offset_y"]), letter, font=font_main, fill=layout["font_color"])
        draw.text((num_right_x, num_y), number_right, font=font_main, fill=layout["font_color"])

    # State code (city/state)
    state_x1 = int(width * layout["white_x2_ratio"])
    state_x2 = width
    state_y1 = 0
    state_y2 = height
    state_w = state_x2 - state_x1
    state_h = state_y2 - state_y1
    state_bbox = draw.textbbox((0,0), state_code, font=font_state)
    state_text_w = state_bbox[2] - state_bbox[0]
    state_text_h = state_bbox[3] - state_bbox[1]
    state_text_x = state_x1 + (state_w - state_text_w)//2 + layout["state_offset_x"]
    state_text_y = state_y1 + (state_h - state_text_h)//2
    draw.text((state_text_x, state_text_y), state_code, font=font_state, fill=layout["font_color"])

    if out_path:
        img.save(out_path)
    if show_img:
        img.show()
    return img



#RezaGooner
