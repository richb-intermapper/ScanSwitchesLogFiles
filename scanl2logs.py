'''
Scan a switches.log file to prepare a history of the InterMapper Layer2 scan/harvest operation

The program is a filter - it reads stdin and writes to stdout.
These can be overridden by -i and -o arguments.


There are four important pieces of information garnered from the file.
They require that log.kali and log.sql both be true before beginning the scan
As scanlogs.py reads the input file it detects:

SQL "INSERT INTO device" lines that contain data about the IMID, the IP address, name/label, and sysSvcs for all "pollers"
<KC_opentable lines that contain an IMID for a device and the KCid to link it to the following "<KR"
<KR with a matching KCid that also contains a "table id" and a tableTitle (ifIndex, ifAddrTable, etc.)
<KU_tabledata lines with the same "table ID" to data, or to a "ParseError" or "NoAnswer" to indicate that it's the last line.

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
gLineBuffer = ""

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

thelog = None                               # Global

def initGlobals():
    '''
    Clear out all the global variables so they can be used for next harvest
    '''
    global tablelist, labeldict, adrsdict, syssvcdict, gLineBuffer
    tablelist = []                              # a list of dictionaries - one for each table (9 tables/poller)
    labeldict = {}                              # names (actually icon labels), indexed by imid
    adrsdict = {}                               # IP addresses, indexed by imid
    syssvcdict = {}                             # and the system services
    gLineBuffer = ""


class L2Log:
    '''
    Class to return a line from the log file. Concatenates lines that begin with white space,
        and keeps track of the "real" line number (e.g., the first)
    '''

    def __init__(self, thefile):
        self.thefile = thefile
        self.linect = 1
        self.prevline = thefile.readline()                          # prevline and prevlinenum go together to remember the
        self.prevlinenum = 0                                        #    line and its starting line number
        self.linenum = 0                                            # linenum is the number of the most-recently-returned line

    def getline(self):                                              # return the next (processed) line from the file
        retline = ""
        while True:
            line = self.thefile.readline()                          # read the next line
            if line == "":                                          # Is this EOF?
                retline = self.prevline                             #   then simply return the previous line
                self.prevline = ""
                break
            else:                                                   # got a new line
                self.linect += 1                                    # bump line number within file
                if line[0:1] == " " or line[0:1] == "\t":           # if it begins with white space
                    self.prevline = self.prevline[:-1]              # chop off the \n from previous line
                    self.prevline += " " + line.strip() + "\n"      # add a space char, tack on new line, and add back \n
                else:
                    retline = self.prevline                         # got a completed line; prepare to return it
                    self.linenum = self.prevlinenum                 #    and remember its line number for the world
                    self.prevline = line                            # Save this new line for next time
                    self.prevlinenum = self.linect                  #    and remember its line number
                    break
        return retline                                          # finally, hand it back for processing


def processOpentable(line):
    pos = line.find('id=')
    line = line.replace("id=","kcid=")      # change "id" to "kcid" on <KC_opentable
    t = line[0:19]
    kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

    tbl = {}                            # fill in all possible fields
    tbl['startTime'] = t
    tbl['endTime'] = "                   "  # 19 spaces
    tbl['startLine'] = thelog.linenum
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
    if kvs['kcid'] == "274":
        pass

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
            if 'done' in kvs:
                l['tableid'] += " "+kvs['done'] # mark it so it no longer matches
                l['endTime'] = t            # save the end time
                l['endLine'] = thelog.linenum
            else:
                l['rows'] += 1              # otherwise, bump the row count
            break                           # and exit
    pass


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

    fo.write(gLineBuffer+"\n")
    fo.write("Resulting Table Info\n")
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
        if "No" in tid:
            diag += "Received NoAnswer; "
        elif not "Pa" in tid and r != 0:
            diag += "Never received end of table data; "
        fo.write(" %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (st, et, sl, el, imid, hexip, kcid, tid, ip, lbl, svc, tn, r, diag))

def addTogLineBuffer(reason, line):
    global gLineBuffer
    l = line.replace(",","")
    tail = l[25:]
    if len(tail) > 75:
        tail = tail[:75] + "..."
    gLineBuffer += " %s, %s,, %s\n" %(l[0:19], reason , tail )

def processLine(line):
    global gLineBuffer
    if "#erase" in line:
        addTogLineBuffer("Erasing database:", line)
    elif "AlGORITHM" in line:
        addTogLineBuffer("Processing data:", line)
    elif "ANALYZE" in line:
        addTogLineBuffer("Starting analysis of collected data:", line)
    elif "id='1'" in line:
        addTogLineBuffer("Restarting transaction sequence:", line)
    elif "<KC_export type='direct' name='devices.csv'" in line:
        addTogLineBuffer("Requesting poller list:", line)
    # elif "DETAIL" in line:
    #     addTogLineBuffer(line)
    # elif "'phase'" in line:
    #     addTogLineBuffer(line)

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

    f = theArgs.infile                      # the argument parsing returns open file objects
    fo = theArgs.outfile

    # Now to the meat of the program

    global thelog
    thelog = L2Log(f)                       # initialize the file object

    while True:
        line = thelog.getline()
        if line == "":
            break
        processLine(line)

    fo.write("Reading switches.log, %s\n" % os.path.abspath(f.name))

    printTables(fo)                         # print the relevant information

if __name__ == "__main__":
    sys.exit(main())
