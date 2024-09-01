import wcwidth


def get_display_width(s):
    return sum(wcwidth.wcwidth(c) for c in s)


def align_strings(split_strings: list[list[str]]):

    # 计算每列的最大宽度
    max_widths: list[int] = []
    for col in zip(*split_strings):
        max_widths.append(max(get_display_width(word) for word in col))

    # 对每个单词进行填充，使其对齐
    aligned_list: list[str] = []
    for words in split_strings:
        aligned_words = [word + ' ' * (max_widths[i] - get_display_width(word))
                         for i, word in enumerate(words)]
        aligned_list.append(" ".join(aligned_words))

    return aligned_list
