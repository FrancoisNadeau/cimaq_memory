#!/usr/bin/env python3

'''
    Source: https://codereview.stackexchange.com/questions/215360/python-code-to-identify-structure-of-a-text-file
'''    

def identify_fixed_width(filepath):
    # Re-use the same file-handle with fh.seek(0)
    with open(filepath) as fh:
        number_lines, avg_chars, max_length = get_avg_chars(fh)
        fh.seek(0)
        counter = find_header(fh, avg_chars)
        fh.seek(0)
        col_pos = get_row_counter(fh, counter)
    common = list(set.intersection(*map(set, col_pos)))
    new_common = [x for x in common if (x-1) not in common]
    new_common.append(max_len)
    _range = len(new_common)
    width = []
    for i, _ in enumerate(new_common[0:_range-1]):
        width.append(new_common[i+1] - new_common[i])
    return counter, width  

def get_avg_chars(fh):
    """
    Use enumerate to track the index here and
    just count how much you want to decrement from the index
    at the end
    """
    decrement, max_len, total_chars = 0, 0, 0
    for idx, line in enumerate(fh, start=1):
        total_chars += len(line)
        if len(line) <= 2:
            decrement += 1
        # this can be evaluated with a ternary expression
        max_len = len(line) if len(line) > max_len else max_len
    # at the end of the for loop, idx is the length of the file
    num_lines = idx - decrement
    avg_chars = total_chars / num_lines
    return num_lines, avg_chars, max_len

def find_header(fh):
    counter = 0
    avg_chars = get_avg_chars(fh)
    for line in fh:
        lower = len(line) <= avg_chars * 0.9
        upper = len(line) >= avg_chars * 1.1
        if upper or lower:
            counter += 1
        else:
            break
    return counter

def get_row_counter(fh, counter):
    """
    Use enumerate for row_counter
    """ 
    col_pos = []
    for row_counter, line in enumerate(fh):
        if row_counter <= counter:
             continue
        blanks = [m.start() for m in re.finditer(' ', line)]
        if len(blanks) > 2:
            col_pos.append(blanks)
            if row_counter <= 5:
                logger.debug(col_pos[-1])
    return col_pos
