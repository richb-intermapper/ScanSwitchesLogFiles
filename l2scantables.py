import re
import socket
import struct

class L2ScanTables:
    '''
    Saves the detailed information about the various table scan/harvest.
    '''
    def __init__(self, thelog):
        '''
        Clear out all the global variables so they can be used for next harvest
        '''
        self.tablelist = []                              # a list of dictionaries - one for each table (9 tables/poller)
        self.labeldict = {}                              # names (actually icon labels), indexed by imid
        self.adrsdict = {}                               # IP addresses, indexed by imid
        self.syssvcdict = {}                             # and the system services
        self.thelog = thelog
        self.diaglines = ""
        self.tablelines = ""

        self.syssvclookup = {
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


    def processOpentable(self, line):
        # pos = line.find('id=')
        line = line.replace("id=","kcid=")      # change "id" to "kcid" on <KC_opentable
        t = line[0:19]
        kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

        tbl = {}                            # fill in all possible fields
        tbl['startTime'] = t
        tbl['endTime'] = "                   "  # 19 spaces
        tbl['startLine'] = self.thelog.linenum
        tbl['endLine'] = "-"
        tbl['imid'] = kvs['target']
        tbl['kcid'] = kvs['kcid']
        tbl['tableName'] = '-'
        tbl['tableid'] = "-"
        tbl['rows'] = 0
        self.tablelist.append(tbl)

        # ensure IMID is in other data structures
        imid = kvs['target']
        self.labeldict.setdefault(imid, "-")
        self.syssvcdict.setdefault(imid, "")
        self.adrsdict.setdefault(imid, "0")


    def processKR(self, line):
        line = line.replace('KR id','KR kcid')   # change "id" to "kcid" on <KR id...
        kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}
        if kvs['kcid'] == "274":
            pass

        for l in self.tablelist:
            if l['kcid'] == kvs['kcid']:
                l['kcid'] += "+"                # mark the KCid as having received a KR
                l['tableid'] = kvs['id']        # record the corresponding id= for the table
                l['tableName'] = kvs['title']   # and the table name
                l['rows'] = 0                   # zero out the row count
                break


    def processTableData(self, line):
        t = line[0:19]                          # get the time stamp from the line
        kvs = {k:v.strip("'") for k,v in re.findall(r'(\S+)=(".*?"|\S+)', line)}

        for l in self.tablelist:
            if l['tableid'] == kvs['id']:       # found matching table entry
                if 'done' in kvs:
                    l['tableid'] += " "+kvs['done'] # mark it so it no longer matches
                    l['endTime'] = t            # save the end time
                    l['endLine'] = self.thelog.linenum
                else:
                    l['rows'] += 1              # otherwise, bump the row count
                break                           # and exit
        pass


    def processSQLline(self, line):
        pos = line.find('VALUES (')
        part = line[pos+len('VALUES ('):]
        ary = part.split(",")
        imid = ary[0].strip("'")
        label = ary[1].strip("' ")
        ip = ary[2].strip("'x ")
        svcs = ary[6].strip("' ")
        svc = self.syssvclookup.get(svcs, str(svcs))

        self.syssvcdict[imid] = svc
        self.labeldict[imid] = label
        self.adrsdict[imid] = ip


    def printL2Tables(self):

        self.diaglines = ""
        self.tablelines = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % ("Start Time", "End Time", "Start Line", "End Line","IMID", "HexIP", "KCid", "TableID", "IP", "Label", "SysSvc", "TableName", "Rows", "Diag")
        for l in self.tablelist:
            st = l['startTime']
            et = l['endTime']
            sl = l['startLine']
            el = l['endLine']
            imid = l['imid']
            kcid = l['kcid']
            tn = l['tableName']
            tid = l['tableid']
            r = l['rows']
            lbl = self.labeldict[imid]
            svc = self.syssvcdict[imid]
            hexip = self.adrsdict[imid]
            addr_long = int(hexip,16)
            ip = socket.inet_ntoa(struct.pack(">L", addr_long))
            diag = ""
            if not "+" in kcid:
                diag += "Never received matching 'KR'; "
            if "No" in tid:
                diag += "Received NoAnswer; "
            elif not "Pa" in tid and r != 0:
                diag += "Never received end of table data; "
            if diag != "":
                self.diaglines += ", Error during scan:, , , Device %s (%s); table %s:; KCID %s; %s \n" % (ip, imid, tn, kcid, diag)
            self.tablelines += " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (st, et, sl, el, imid, hexip, kcid, tid, ip, lbl, svc, tn, r, diag)
        return (self.diaglines, self.tablelines)

    def processLine(self, line):
        '''
        Process each line of the file, triggering on interesting states/info
        '''
        if 'KALI: <' in line:
            line = line.replace(">"," >")
            if '<KC_opentable' in line:
                self.processOpentable(line)
            elif 'KR id' in line:
                self.processKR(line)
            elif '<KU_tabledata' in line:
                self.processTableData(line)
        elif 'SQL #-1: INSERT INTO device' in line:
            self.processSQLline(line)

    def isNewScan(self, line):
        '''
        Examine the passed-in line to see if it signals the beginning of a new scan.
        If the line contains one of several strings, *and* if the tablelist has entries,
        then it's a new scan.
        '''
        startStrings = [
            "Debug: #erase",
            "<KC_login id='1'",
            "CMD RECV: POLL_NOW_REQUEST",
            " KALI: <KC_export type='direct' name='devices.csv'"
        ]

        newScan = False
        for s in startStrings:
            if s in line:
                newScan = True
                break
        return newScan and (len(self.tablelist) > 0)