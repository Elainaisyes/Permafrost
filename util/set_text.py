from classes.basic_image import Basic_Image

line_breaks = 0
line_width = 0

def get_line_breaks():
    return line_breaks

def get_line_width():
    return line_width
        


def set_text(text, x, y, letters_dict, letter_size, window, group,
             spacing, scale_factor, color=None, max_width=None, text_shadow=None):
    global line_breaks
    global line_width

    cursor_x = x
    cursor_y = y
    line_breaks = 0
    line_width = 0
    max_line_width = 0

    words = text.split(" ")

    for word_index, word in enumerate(words):
        if word == "":
            cursor_x += letter_size * spacing * scale_factor
            continue

        word_width = 0
        for character in word:
            word_width += letters_dict[character]["width"] * scale_factor / spacing

        if max_width is not None and cursor_x + word_width > x + max_width:
            max_line_width = max(max_line_width, cursor_x - x)
            cursor_x = x
            cursor_y += letter_size
            line_breaks += 1

        for character in word:
            if character == " ":
                advance = letter_size / spacing * scale_factor
            else:
                advance = letters_dict[character]["width"] * scale_factor / spacing

            draw_x = cursor_x

            if text_shadow is not None:
                Basic_Image(
                    letters_dict[character]["image"],
                    round(draw_x) + text_shadow[0],
                    round(cursor_y) + text_shadow[1],
                    letter_size,
                    letter_size,
                    scale_factor,
                    window,
                    group,
                    color=text_shadow[2]
                )

            Basic_Image(
                letters_dict[character]["image"],
                round(draw_x),
                round(cursor_y),
                letter_size,
                letter_size,
                scale_factor,
                window,
                group,
                color=color
            )

            cursor_x += advance

        if word_index < len(words) - 1:
            cursor_x += letter_size * spacing * 0.6 * scale_factor

    line_width = max(max_line_width, cursor_x - x)