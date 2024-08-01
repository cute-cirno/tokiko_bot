import unicodedata
import wcwidth

def get_display_width(s):
    return sum(wcwidth.wcwidth(c) for c in s)

def align_strings(string_list):
    # 拆分字符串列表为单词列表
    split_strings = [s.split() for s in string_list]

    # 计算每列的最大宽度
    max_widths = []
    for col in zip(*split_strings):
        max_widths.append(max(get_display_width(word) for word in col))

    # 对每个单词进行填充，使其对齐
    aligned_list = []
    for words in split_strings:
        aligned_words = [word + ' ' * (max_widths[i] - get_display_width(word)) for i, word in enumerate(words)]
        aligned_list.append(" ".join(aligned_words))

    return aligned_list