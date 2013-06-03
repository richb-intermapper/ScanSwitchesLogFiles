import re
from datetime import datetime

class L2HistoryBuffer():
    '''
    Collect lines of interest into a global buffer for displaying as history
    '''
    def __init__(self, thelog):
        self.clearHistory(thelog)

    def clearHistory(self, thelog):
        self.gLineBuffer = "Time, State, Line, Progress, Message\n"
        self.reason = ""
        self.prevtail = ""
        self.startdup = ""                  # First of the duplicate lines
        self.lastdup = ""                   # last of the duplicates
        self.dupcount = 0
        self.stepdev = 0
        self.totaldev = 0
        self.thelog = thelog


    def logit(self, line):
        '''
        Examine each line to see if it should be entered into the history buffer
        Set the 'reason' if the line matches one of the interesting strings
        Set the 'data' if the duplicate detection should operate on a substring of the line,
           otherwise, the entire line will be recorded.
        '''
        reason = ""
        data = line
        if "Debug: #erase" in line:
            reason = "Erasing database"
        elif "Debug: #set" in line:
            reason = "Setting flags:"
        elif "CONN:" in line:
            reason = "Connection change:"
        elif "CMD SEND:" in line:
            if "PROGRESS_REQUEST" not in line:
                reason = "Sending to GUI:"
                pos = line.find("source=")
                data = line[0:pos]
        elif "ALGORITHM" in line:
            if "computeSimpleConnection" not in line and "computeSwitchIntersection" not in line:
                reason = "Analyzing collected data:"
        elif "ANALYZE" in line:
            reason = "Starting analysis of collected data:"
        elif "<KC_login id='1'" in line:
            reason = "Restarting transaction sequence:"
        elif "<KC_export type='direct' name='devices.csv'" in line:
            reason = "Requesting poller list:"
        elif "SQL #-1: INSERT INTO device " in line:
            reason = "Adding to Devices table"
            data = line[0:24] + " Inserting into devices table\n"
        elif "CMD RECV: ABORT_POLL_REQUEST" in line:
            reason = "Aborting previous action:"
        elif "CMD RECV: POLL_NOW_REQUEST" in line:
            reason = "Manually start poll:"
        elif "<KC_opentable" in line:
            reason = "Scanning tables:"                 # pass in known 'data' so that it can collapse duplicate lines
            data = line[0:24]+" [MainThread] KALI: Issuing <KC_opentable commands...\n"
        elif "unknown" in line.lower():
            if "KU_tabledata: Unknown tableID" not in line and "DETAIL:" not in line:
                reason = "Found 'unknown'"
        # elif "ParseError" not in line:                # ignore ParseError
        #     if "error" in line.lower():               # but keep 'error' lines
        #         reason = "Found 'Error'"              # commented out - doesn't find anything useful
        elif " DETAIL:" in line:
            kvs = {k:v.strip("'") for k,v in re.findall(r"\('(\S+)', ('.*?')\)", line)}
            if  "'phase'" in line:
                self.stepdev = kvs['step']          # simply record our progress for use in subsequent report lines
                self.totaldev = kvs['total']
                reason = ""                         # but don't log the info
            elif "'alg.cdp.strict'" in line:
                reason = "Flags:"
            # elif "'_list', 'switch_to_switch'" in line:
            #     self.addTogLineBuffer("Sending switch-to-switch to GUI:", line)
        elif "EXCEPTION" in line:
            if "COMMAND_INVALID_PARAM" not in line: # ignore bad typing from customer in filter field
                reason = "Exception:"
        if reason != "":                            # no reason - don't log it
            if data[-1] != "\n":
                data += "\n"
            self.addToBuffer(reason, data)


    def addToBuffer(self, reason, line):
        l = line.replace(",","")
        tail = l[25:]
        if tail == self.prevtail:
            self.dupcount += 1
            self.lastdup = l[0:19]
        else:
            if self.dupcount != 0:              # if there were duplicated lines...
                stime = datetime.strptime(self.startdup, "%Y-%m-%d %H:%M:%S")
                etime = datetime.strptime(self.lastdup,  "%Y-%m-%d %H:%M:%S")
                delta = etime - stime
                self.gLineBuffer += " %s, %s, total %d times, until %s (%s)\n" %(self.startdup, self.reason, self.dupcount+1, self.lastdup, delta )
            self.gLineBuffer += " %s, %s, %s, %s of %s, %s" %(l[0:19], reason, self.thelog.linenum, self.stepdev, self.totaldev , tail )
            self.reason = reason
            self.prevtail = tail
            self.startdup = line[0:19]
            self.lastdup = self.startdup
            self.dupcount = 0
