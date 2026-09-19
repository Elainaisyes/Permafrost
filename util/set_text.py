from classes.basic_image import Basic_Image

def set_text(text, x, y, letters_dict, letter_size, window, group,
             spacing, scale_factor, color=None):
    cursor_x = x
    default_amount = letter_size * scale_factor / spacing

    # Letter m is much bigger than the others by a ratio of 16/10.6, hence the multiplier is needed
    m_multiplier = 1.50943396
    m_side_spacing = default_amount / m_multiplier / 2

    for character in text:
        if character == " ":
            cursor_x += default_amount
            continue

        if character in {"m", "M"}:
            cursor_x += m_side_spacing

        Basic_Image(
            letters_dict[character],
            round(cursor_x),
            y,
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