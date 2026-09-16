from classes.letter import Letter

def set_text(text, x, y, letters_dict, letter_size, spacing, window, group):
    space_multiplier = 1
    for i in range(len(text)):
        if text[i] == " ":
            space_multiplier = 2
        else: 
            space_multiplier = 1
            Letter(letters_dict[text[i]], x + letter_size * i * space_multiplier // spacing , y, letter_size, 1, window, group)

