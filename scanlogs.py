'''
Scan a switches.log file, concatenating all lines that begin with ' ' to the previous line
 It's a filter - reads stdin, writes to stdout
'''

import os
import sys
import re
import socket
import struct


tablelist = []                              # a list of dictionaries - one for each table (9 tables/poller)
labeldict = {}                              # names (actually icon labels), indexed by imid
adrsdict = {}                               # IP addresses, indexed by imid

def processOpentable(line):
    pos = line.find('id=')
    line = line.replace("id=","kcid=")      # change "id" to "kcid" on <KC_opentable
    t = line[0:24]
    kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

    tbl = {}
    tbl['startTime'] = t
    tbl['imid'] = kvs['target']
    tbl['kcid'] = kvs['kcid']
    tbl['tableid'] = "-"
    tbl['endTime'] = "                        " # 24 spaces
    tbl['tableName'] = '-'
    tbl['rows'] = 0
    tablelist.append(tbl)


def processKR(line):
    line = line.replace('KR id','KR kcid')   # change "id" to "kcid" on <KR id...
    kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

    for l in tablelist:
        if l['kcid'] == kvs['kcid']:
            l['kcid'] += "+"                # mark the KCid as having received a KR
            l['tableid'] = kvs['id']        # record the corresponding id= for the table
            l['tableName'] = kvs['title']   # and the table name
            l['rows'] = 0                   # zero out the row count
            break


def processTableData(line):
    t = line[0:24]                          # get the time stamp from the line
    kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

    for l in tablelist:
        if l['tableid'] == kvs['id']:       # found matching table entry
            if 'ParseError' in line:        # 'ParseError' indicates this is the last line of the table
                l['tableid'] += '+'         # mark it so it no longer matches
                l['endTime'] = t            # save the end time
            else:
                l['rows'] += 1              # otherwise, bump the row count
            break                           # and exit


def processSQLline(line):
    pos = line.find('VALUES (')
    part = line[pos+len('VALUES ('):]
    ary = part.split(",")
    imid = ary[0].strip("'")
    label = ary[1].strip("' ")
    ip = ary[2].strip("'x ")
    labeldict[imid] = label
    adrsdict[imid] = ip


def printTables(fo):
    fo.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % ("Start", "End", "IMID", "HexIP", "KCid", "TableID", "IP", "Label", "TableName", "Rows", "Diag"))
    for l in tablelist:
        st = l['startTime']
        et = l['endTime']
        imid = l['imid']
        kcid = l['kcid']
        tn = l['tableName']
        tid = l['tableid']
        r = l['rows']
        lbl = labeldict[imid]
        hexip = adrsdict[imid]
        addr_long = int(hexip,16)
        ip = socket.inet_ntoa(struct.pack(">L", addr_long))
        diag = ""
        if not "+" in kcid:
            diag += "Never received matching 'KR'; "
        if not "+" in tid and r != 0:
            diag += "Never received end of table data; "
        fo.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (st, et, imid, hexip, kcid, tid, ip, lbl, tn, r, diag))


def processLine(line):
    if 'KALI: <' in line:
        line = line.replace(">"," >")
        if '<KC_opentable' in line:
            processOpentable(line)
        elif 'KR id' in line:
            processKR(line)
        elif '<KU_tabledata' in line:
            processTableData(line)
    elif 'SQL #-1: INSERT INTO device' in line:
        processSQLline(line)


def main(argv=None):

    f = sys.stdin                                   # open the files to read and write
    fo = sys.stdout

    # f = open('switches.log.2013_05_23.txt','r')                      # debugging input & output files
    # fo = open('junk3.csv','w')
    # fe = sys.stderr

    fo.write("Reading switches.log from: %s\n" % os.path.abspath(f.name))

    prevline = f.readline()                         # read the first line

    for line in f.readlines():                      # read the next line
        if line[0:1] == " " or line[0:1] == "\t":   # if it begins with white space
            prevline = prevline[:-1]                # chop off the \n from prevline
            prevline += " " + line.strip() + "\n"   # add a space char, tack on new line, and add back \n
        else:
            # fo.write(prevline)
            processLine(prevline)                   # process a completed line
            prevline = line                         # and save the current line for further processing

    # fo.write(prevline)
    processLine(prevline)                           # finally, process this last line

    printTables(fo)

if __name__ == "__main__":
    sys.exit(main())
