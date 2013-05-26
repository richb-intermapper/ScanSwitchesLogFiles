'''
Scan a switches.log file to prepare a history of the InterMapper Layer2 scan/harvest operation

The program is a filter - it reads stdin and writes to stdout.
These can be overridden by -i and -o arguments.


There are four important pieces of information garnered from the file.
They require that log.kali and log.sql both be true before beginning the scan
As scanlogs.py reads the input file it detects:

SQL "INSERT INTO device" lines contain data about the IMID, the IP address, name/label, and sysSvcs for all "pollers"
<KC_opentable lines that contain an IMID for a device and the KCid to link it to the following "<KR"
<KR with a matching KCid that also contains a "table id" and a tableTitle (ifIndex, ifAddrTable, etc.)
<KU_tabledata lines with the same "table ID" to data, or to a "ParseError" to indicate that it's the last line.

'''

import os
import sys
import re
import socket
import struct
import argparse

tablelist = []                              # a list of dictionaries - one for each table (9 tables/poller)
labeldict = {}                              # names (actually icon labels), indexed by imid
adrsdict = {}                               # IP addresses, indexed by imid
syssvcdict = {}                             # and the system services

syssvclookup = {
    '1': "Hub",
    '2': "Sw",
    '4': "Rtr",
    '6': "L3 Sw",
    '7': "L3 SwHub",
    '64': "Host (64)",
    '72': "Host (72)",
    '76': "Host (76)",
    '78': "Host (78)"
}

gLineNumber = 0                             # line number of each (concatenated) line being processed


def getLogLine(f):
    '''
    Get the next line from the input log file.
    Increment the global line counter
    '''
    global gLineNumber
    gLineNumber += 1
    return f.readline()

def processOpentable(line):
    pos = line.find('id=')
    line = line.replace("id=","kcid=")      # change "id" to "kcid" on <KC_opentable
    t = line[0:19]
    kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

    tbl = {}                            # fill in all possible fields
    tbl['startTime'] = t
    tbl['endTime'] = "                   "  # 19 spaces
    tbl['startLine'] = gLineNumber
    tbl['endLine'] = "-"
    tbl['imid'] = kvs['target']
    tbl['kcid'] = kvs['kcid']
    tbl['tableName'] = '-'
    tbl['tableid'] = "-"
    tbl['rows'] = 0
    tablelist.append(tbl)

    # ensure IMID is in other data structures
    imid = kvs['target']
    labeldict.setdefault(imid, "-")
    syssvcdict.setdefault(imid, "")
    adrsdict.setdefault(imid, "0")


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
    t = line[0:19]                          # get the time stamp from the line
    kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

    for l in tablelist:
        if l['tableid'] == kvs['id']:       # found matching table entry
            if 'ParseError' in line:        # 'ParseError' indicates this is the last line of the table
                l['tableid'] += '+'         # mark it so it no longer matches
                l['endTime'] = t            # save the end time
                l['endLine'] = gLineNumber
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
    svcs = ary[6].strip("' ")
    svc = syssvclookup.get(svcs, str(svcs))

    syssvcdict[imid] = svc
    labeldict[imid] = label
    adrsdict[imid] = ip


def printTables(fo):
    fo.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % ("Start Time", "End Time", "Start Line", "End Line","IMID", "HexIP", "KCid", "TableID", "IP", "Label", "SysSvc", "TableName", "Rows", "Diag"))
    for l in tablelist:
        st = l['startTime']
        et = l['endTime']
        sl = l['startLine']
        el = l['endLine']
        imid = l['imid']
        kcid = l['kcid']
        tn = l['tableName']
        tid = l['tableid']
        r = l['rows']
        lbl = labeldict[imid]
        svc = syssvcdict[imid]
        hexip = adrsdict[imid]
        addr_long = int(hexip,16)
        ip = socket.inet_ntoa(struct.pack(">L", addr_long))
        diag = ""
        if not "+" in kcid:
            diag += "Never received matching 'KR'; "
        if not "+" in tid and r != 0:
            diag += "Never received end of table data; "
        fo.write(" %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (st, et, sl, el, imid, hexip, kcid, tid, ip, lbl, svc, tn, r, diag))


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

    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", '--infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        theArgs = parser.parse_args()
    except Exception, err:
        return str(err)

    f = theArgs.infile
    fo = theArgs.outfile
    # f = open('switches.log', 'r')
    # fo = open('switches.csv', 'w')

    # Now to the meat of the program

    prevline = getLogLine(f)                        # read the first line

    while True:
        line = getLogLine(f)                        # read the next line
        if line == "":
            break                                   # an empty line signals EOF
        if line[0:1] == " " or line[0:1] == "\t":   # if it begins with white space
            prevline = prevline[:-1]                # chop off the \n from prevline
            prevline += " " + line.strip() + "\n"   # add a space char, tack on new line, and add back \n
        else:
            processLine(prevline)                   # process a completed line
            prevline = line                         # and save the current line for further processing

    processLine(prevline)                           # finally, process this last line

    fo.write("Reading switches.log, %s\n" % os.path.abspath(f.name))

    printTables(fo)                                 # print the relevant information

if __name__ == "__main__":
    sys.exit(main())
