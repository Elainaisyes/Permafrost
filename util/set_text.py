from classes.basic_image import Basic_Image

m_multiplier = 16 / 10.6
w_multiplier = 26 / 10.6

line_breaks = 0
line_width = 0

def get_side_spacing(default_amount, multiplier):
    return default_amount / multiplier / 2

def get_line_breaks():
    return line_breaks

def get_line_width():
    return line_width
        


def set_text(text, x, y, letters_dict, letter_size, window, group,
             spacing, scale_factor, color=None, max_width=None):
    global line_breaks 
    global line_width

    cursor_x = x
    cursor_y = y
    default_amount = letter_size * scale_factor / spacing
    line_breaks = 0
    line_width = 0

    m_side_spacing = get_side_spacing(default_amount, m_multiplier)
    w_side_spacing = get_side_spacing(default_amount, w_multiplier)


    current_line_width = 0
    max_line_width = 0

    words = text.split(" ")

    for word_index, word in enumerate(words):
        if word == "":
            cursor_x += default_amount
            current_line_width = cursor_x - x
            continue

        word_width = 0
        for character in word:
            if character in {"m", "M"}:
                word_width += default_amount + (m_side_spacing * 2)
            elif character in {"w", "W"}:
                word_width += default_amount + (w_side_spacing * 2)
            else:
                word_width += default_amount


        if max_width is not None and cursor_x + word_width > x + max_width:
            max_line_width = max(max_line_width, current_line_width)
            cursor_x = x
            cursor_y += letter_size
            line_breaks += 1
            current_line_width = 0

        for character in word:
            if character in {"m", "M"}:
                cursor_x += m_side_spacing
            elif character in {"w", "W"}:
                cursor_x += w_side_spacing

            Basic_Image(
                letters_dict[character],
                round(cursor_x),
                round(cursor_y),
                letter_size,
                letter_size,
                scale_factor,
                window,
                group,
                color=color
            )

            cursor_x += default_amount

            if character in {"m", "M"}:
                cursor_x += m_side_spacing
            if character in {"w", "W"}:
                cursor_x += w_side_spacing

        current_line_width = cursor_x - x

        if word_index < len(words) - 1:
            cursor_x += default_amount
            current_line_width = cursor_x - x

    line_width = max(max_line_width, current_line_width)