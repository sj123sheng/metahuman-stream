import timeit

def remove_chars_set_gen(input_string, chars_to_remove):
    chars_set = set(chars_to_remove)
    return ''.join(char for char in input_string if char not in chars_set)

def remove_chars_translate(input_string, chars_to_remove):
    translation_table = str.maketrans('', '', ''.join(chars_to_remove))
    return input_string.translate(translation_table)

input_string = "Hello, World!" * 1000
chars_to_remove = ['l', 'o', 'H']

# 测试
time_set_gen = timeit.timeit(lambda: remove_chars_set_gen(input_string, chars_to_remove), number=1000)
time_translate = timeit.timeit(lambda: remove_chars_translate(input_string, chars_to_remove), number=1000)
time_set_gen1 = timeit.timeit(lambda: remove_chars_set_gen(input_string, chars_to_remove), number=1000)
time_translate1 = timeit.timeit(lambda: remove_chars_translate(input_string, chars_to_remove), number=1000)
print(f"time_set_gen: {time_set_gen:.6f} seconds")
print(f"Translate method: {time_translate:.6f} seconds")
print(f"time_set_gen: {time_set_gen1:.6f} seconds")
print(f"Translate method: {time_translate1:.6f} seconds")
