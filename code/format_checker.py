# -*- coding:utf-8 -*-

import sys
from openpyxl import load_workbook
import xlwt
import re
import editdistance as ed
import g
import urllib2
from bs4 import BeautifulSoup
import json

chinese_word_pattern = ur'[\u4e00-\u9fa5]+' 
c_with_e = ur'[\u4e00-\u9fa5][a-zA-Z0-9]'
e_with_c = ur'[a-zA-Z0-9][\u4e00-\u9fa5]'
english_word_pattern = '[a-zA-Z ]+'
replace_dict = {u'您':u'你'}
eng = open('english').read().split('\n')[:-1]
w = open('english', 'a')
eng_dict = {}
for line in eng:
    line = line.strip()
    info = line.split('#@#')
    print info
    if len(info) < 2:
        eng_dict[info[0]] = info[0]
    else:
        eng_dict[info[0]] = info[1]
print len(eng_dict)

def check_format(line):
    wrong_idx_list = []
    del_idx = []
    newline = line
    #rule 0, replace some words
    for key in replace_dict:
        rp = [m.start() for m in re.finditer(key, line)]
        if len(rp) > 0:
            wrong_idx_list += rp
            print key
            newline = line.replace(key, replace_dict[key])
        

    #rule 1, no space between Chinese chars
    for i in range(2, len(line)):
        if re.match(chinese_word_pattern, line[i]) and re.match(chinese_word_pattern, line[i-2]) and line[i-1] == ' ':
            print line[i-2].encode('utf-8') + ' '  + line[i].encode('utf-8')
            del_idx.append(i-1)
            wrong_idx_list += [i-2, i-1, i]

    #rule 2, space between full notes;
    notes = set([u'（', u'）', u'《', u'》', u'」', u'「', u'。', u'，', u'！', u'：', u'；', u'？', u'⋯', u'、'])
    for i in range(1, len(line) - 1):
        if line[i] in notes:
            if line[i-1] == ' ' or line[i+1] == ' ':
                print line.encode('utf-8')
                wrong_idx_list += [i-1, i, i+1]
                if line[i-1] == ' ':
                    del_idx.append(i-1)
                else:
                    del_idx.append(i+1)

    #rule 2.1 () with Chinese or （）with english
    e_bracket = ur'（[a-zA-Z &\.]+）|（[a-zA-Z &\.]+\)|\([a-zA-Z &\.]+）'
    wrong_bracket = re.findall(e_bracket, line)
    if len(wrong_bracket) > 0:
        for word in wrong_bracket:
            idx = line.find(word)
            wrong_idx_list += range(idx, idx + len(word))
        print line + ' bracket'
        

#    #rule 2.1, no space between chinese and english(numbers)
#    for i in range(0, len(line) - 1):
#        if re.match(e_with_c, line[i:i+2]) and line[i+1] not in notes:
#            print line + "english chinese" + " " + line[i:i+2]
#        if re.match(c_with_e, line[i:i+2]) and line[i] not in notes:
#            print line + "CHINESE english" + " " + line[i:i+2]
    
    del_idx.sort()
    if len(del_idx) == 0:
        new_line_part = [newline]
    else:
        new_line_part = [newline[0:del_idx[0]]]
    for i in range(0, len(del_idx)):
        if i < len(del_idx) - 1:
            new_line_part.append(newline[del_idx[i] + 1:del_idx[i+1]])
        else:
            new_line_part.append(newline[del_idx[i] + 1:])
    #rule 3, wrong english name
    cand_english_name = re.findall('[a-zA-Z&0-9 \']+', line)
    newline = ''.join(new_line_part)
    for s in cand_english_name:
        slen = len(s)
        s = s.strip()
        if len(s) < 2 or s.find(' ') == -1:
            continue
        if s in eng_dict:
            if s != eng_dict[s]:
                print 'replace' + s + ' to ' + eng_dict[s]
                wrong_idx_list += [line.find(s) + sl for sl in range(0, slen)]
                newline = newline.replace(s, eng_dict[s])
            continue
        search_url = 'http://www.baidu.com/s?wd=' + s.replace(' ', '+') + '+wikipedia' + '&sl_lang=en&rsv_srlang=en&rsv_rq=en'
        print search_url
        res = urllib2.urlopen(search_url)
        html = res.read()
        soup = BeautifulSoup(html, 'html.parser')
        all_result = soup.findAll('div', {'class':'c-tools'})
        if len(all_result) == 0:
            continue
        all_result = all_result[0]['data-tools'].replace('\\', '\\\\')
#        cnt = 0
##        wiki_name = ''
#        print 'search:' + s
#        for title in g.search(s + ' wikipedia', stop = 1):
#            if cnt == 0:
#                wiki_name = title.split('-')[0].strip()
#                cnt += 1
#            else:
#                break
#        print 'search result:' + wiki_name
        wiki_name = json.loads(all_result)['title'].split('-')[0].strip()
        dist = ed.eval(wiki_name.lower(), s.lower())
        if dist > 0 and dist < 2 and s.count(' ') != wiki_name.count(' '):
            wrong_idx_list += [line.find(s) + sl for sl in range(0, slen)]
            print 'ENGLISH NAME ERROR: "' +  s + '" ->  "' + wiki_name + '"'
            w.write(s + '#@#' + wiki_name + '\n')
            eng_dict[s] = wiki_name
            w.flush()
        else:
            if dist == 0:
                print 'ORIGIN' + s
                eng_dict[s] = s
                w.write(s + '\n')
                w.flush()
    return set(wrong_idx_list), newline


if __name__ == '__main__':
    f = open(sys.argv[1]).read().split('\n')[:-1]
    cnt = 0
    i = 0
    for line in f:
        print i
        i += 1

        wrong_set, newline = check_format(line.decode('utf-8'))
        if len(wrong_set) > 0:
            cnt += 1

    print cnt
    w.close()
