#-*- coding:utf-8 -*-

import sys
import re

chinese_word_pattern = ur'[\u4e00-\u9fa5]+' 

def check_format(line):
    #rule 1, no space between Chinese chars
    for i in range(2, len(line)):
        if re.match(chinese_word_pattern, line[i]) and re.match(chinese_word_pattern, line[i-2]) and line[i-1] == ' ':
            print line[i-2] + ' '  + line[i]

    #rule 2, space between （ ）
    for i in range(1, len(line) - 1):
        if line[i] == u'（' or line[i] == u'）':
            if line[i-1] == ' ' or line[i+1] == ' ':
                print line


if __name__ == '__main__':
    f = open(sys.argv[1]).read().split('\n')[:-1]
    for line in f:
        check_format(line.decode('utf-8'))
