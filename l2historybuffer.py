import re

class L2HistoryBuffer():
    '''
    Collect lines of interest into a global buffer for displaying as history
    '''
    def __init__(self, thelog):
        self.clearHistory(thelog)

    def clearHistory(self, thelog):
        self.gLineBuffer = ""
        self.reason = ""
        self.prevtail = ""
        self.prevtime = ""                  # end of the duplicates - remembered each time we ignore one
        self.dupcount = 0
        self.stepdev = 0
        self.totaldev = 0
        self.thelog = thelog


    def logit(self, line):
        '''
        Examine each line to see if it should be entered into the history buffer
        '''
        reason = ""
        data = line
        if "Debug: #erase" in line:
            reason = "Erasing database:"
        elif "ALGORITHM" in line:
            if "computeSimpleConnection" not in line and "computeSwitchIntersection" not in line:
                reason = "Analyzing collected data:"
        elif "ANALYZE" in line:
            reason = "Starting analysis of collected data:"
        elif "<KC_login id='1'" in line:
            reason = "Restarting transaction sequence:"
        elif "<KC_export type='direct' name='devices.csv'" in line:
            reason = "Requesting poller list:"
        elif "CMD RECV: ABORT_POLL_REQUEST" in line:
            reason = "Aborting previous action:"
        elif "CMD RECV: POLL_NOW_REQUEST" in line:
            reason = "Manually start poll:"
        elif "<KC_opentable" in line:
            reason = "Scanning tables:"
            data = line[0:24]+" [MainThread] KALI: Issuing <KC_opentable commands...\n"
        elif " DETAIL:" in line:
            kvs = {k:v.strip("'") for k,v in re.findall(r"\('(\S+)', ('.*?')\)", line)}
            if  "'phase'" in line:
                self.stepdev = kvs['step']          # simply record our progress for use in subsequent report lines
                self.totaldev = kvs['total']
                reason = ""                         # but don't log the info
            # elif "'_list', 'endpoints'" in line:
            #     self.addTogLineBuffer("Sending endpoints to GUI:", line)
            # elif "'_list', 'switch_to_switch'" in line:
            #     self.addTogLineBuffer("Sending switch-to-switch to GUI:", line)
        elif "EXCEPTION" in line:
            if "COMMAND_INVALID_PARAM" not in line: # ignore bad typing from customer in filter field
                reason = "Exception:"
        if reason != "":                            # no reason - don't log it
            self.addToBuffer(reason, data)


    def addToBuffer(self, reason, line):
        l = line.replace(",","")
        tail = l[25:]
        if tail == self.prevtail:
            self.dupcount += 1
            self.prevtime = l[0:19]
        else:
            if self.dupcount != 0:              # if there were duplicated lines...
                self.gLineBuffer += " %s, %s, repeated %d times, until %s\n" %(l[0:19], self.reason, self.dupcount, self.prevtime )
            self.gLineBuffer += " %s, %s, %s, %s of %s, %s" %(l[0:19], reason, self.thelog.linenum, self.stepdev, self.totaldev , tail )
            self.reason = reason
            self.prevtail = tail
            self.prevtime = line[0:19]
            self.dupcount = 0
