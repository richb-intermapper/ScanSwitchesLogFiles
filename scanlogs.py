'''
Scan a switches.log file, concatenating all lines that begin with ' ' to the previous line
 It's a filter - reads stdin, writes to stdout
'''

import sys
import re


tablelist = []                              # a list of dictionaries - one for each table (9 tables/poller)


def processOpentable(line):
    pos = line.find('id=')
    line = line.replace("id=","rid=")       # change "id" to "rid" on <KC_opentable
    t = line[0:24]
    kvs = dict(re.findall(r'(\S+)=(".*?"|\S+)', line))

    tbl = {}
    tbl['startTime'] = t
    tbl['imid'] = kvs['target']
    tbl['rid'] = kvs['rid']
    tablelist.append(tbl)


def processKR(line):
    line = line.replace('KR id','KR rid')   # change "id" to "rid" on <KR id...
    kvs = dict(re.findall(r'(\S+)=(".*?"|\S+)', line))

    for l in tablelist:
        if l['rid'] == kvs['rid']:
            l['tableid'] = kvs['id']
            l['tableName'] = kvs['title']
            l['rows'] = 0
            break


def processTableData(line):
    t = line[0:24]                          # get the time stamp from the line
    kvs = dict(re.findall(r'(\S+)=(".*?"|\S+)', line))
    eotbl = 'ParseError' in line            # 'ParseError' indicates this is the last line of the table

    for l in tablelist:
        if l['tableid']==kvs['id']:         # found matching table entry
            if eotbl:                       # it's the end of the entries for this table
                l['tableid'] += 'X'         # mark it so it never matches
                l['endTime'] = t            # save the end time
            else:
                l['rows'] += 1              # otherwise, bump the row count
            break                           # and exit


def printTables(fo):
    fo.write("%s, %s, %s, %s, %s, %s, %s\n" % ("Start", "End", "IMID", "rid", "tableName", "tid", "rows"))
    for l in tablelist:
        fo.write("%s, %s, %s, %s, %s, %s, %s\n" % (l['startTime'], l['endTime'], l['imid'], l['rid'], l['tableName'], l['tableid'], l['rows']))


def processLine(line):
    if 'KALI: <' in line:
        line = line.replace(">"," >")
        if '<KC_opentable' in line:
            processOpentable(line)
        elif 'KR id' in line:
            processKR(line)
        elif '<KU_tabledata' in line:
            processTableData(line)


def main(argv=None):

    # f = sys.stdin                                   # open the files to read and write
    # fo = sys.stdout

    f = open('junk1.txt','r')                      # debugging input & output files
    fo = open('junk2.txt','w')

    prevline = f.readline()                         # read the first line

    for line in f.readlines():                      # read the next line
        if line[0:1] == " " or line[0:1] == "\t":   # if it begins with white space
            prevline = prevline[:-1]                # chop off the \n from prevline
            prevline += " " + line.strip() + "\n"   # add a space char, tack on new line, and add back \n
        else:
            # fo.write(prevline)
            processLine(prevline)                   # process a completed line
            prevline = line                         # and save the current line for further processing

    #fo.write(prevline )
    processLine(prevline)                           # finally, process this last line

    printTables(fo)

if __name__ == "__main__":
    sys.exit(main())
