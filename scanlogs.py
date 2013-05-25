'''
Scan a switches.log file, concatenating all lines that begin with ' ' to the previous line
 It's a filter - reads stdin, writes to stdout
'''

import sys

f = sys.stdin
fo = sys.stdout
#fo = open('junk2.txt','w')
#fo.write("Hi Rich!"+"\n")

#f = open('junk1.txt','r')

prevline = f.readline()

for line in f.readlines():
    if line[0:1] == " " or line[0:1] == "\t":
        if prevline[-1] == '\n':
            prevline = prevline[:-1]            # chop off the \n
        prevline += " " + line.strip() + "\n"   # and add a space char, tack on new line, and add back \n
    else:
        fo.write(prevline)
        prevline = line

fo.write(prevline )