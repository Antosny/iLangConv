# -*- coding:utf-8 -*-

import sys
import xlrd
import xlwt
from xlutils.copy import copy
from xlutils.filter import process,XLRDReader,XLWTWriter
from format_checker import check_format

#
# suggested patch by John Machin
# http://stackoverflow.com/a/5285650/2363712
# 
def copy2(wb):
    w = XLWTWriter()
    process(
        XLRDReader(wb,'unknown.xls'),
        w
        )
    return w.output[0][1], w.style_list

font0 = xlwt.easyfont('')
font2 = xlwt.easyfont('color_index red')

def build_seg(line, line_set):
    result = []
    for i in range(0, len(line)):
        if i in line_set:
            result.append((line[i], font2))
        else:
            result.append((line[i], font0))
    return result

if __name__ == '__main__':
    in_book = xlrd.open_workbook(sys.argv[1], formatting_info=True)
    table = in_book.sheet_by_index(0)
    wb = copy(in_book)
    ws = wb.get_sheet(0)
    outBook, outStyle = copy2(in_book)

    for i in range(0, table.nrows):
        print "LINE:" + str(i)
        for j in range(2, 4):
            cell = table.cell(i, j)
            xf_index = table.cell_xf_index(0, 0)
            saved_style = outStyle[xf_index]
            cell = str(cell.value.encode('utf-8')).decode('utf-8')
            cell_wrong_set, newline = check_format(cell)
            seg = build_seg(cell, cell_wrong_set)
            ws.write(i, j, seg, saved_style)
            ws.write(i, j + 5, newline, saved_style)

    wb.save(sys.argv[2])
