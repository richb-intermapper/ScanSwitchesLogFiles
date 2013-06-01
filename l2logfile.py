class L2LogFile:
    '''
    Handle an InterMapper Layer2 log file. Returns one line at a time, concatenating lines that begin with white space,
        and keeps track of the "real" line number (e.g., the first)
    '''

    def __init__(self, thefile):
        self.thefile = thefile
        self.linect = 1
        self.prevline = thefile.readline()                          # prevline and prevlinenum go together to remember the
        self.prevline = self.prevline.rstrip("\n\r")                #    line (no line ending!) and its starting line number
        self.prevlinenum = 0
        self.linenum = 0                                            # linenum is the number of the most-recently-returned line

    def getline(self):                                              # return the next (processed) line from the file
        line = ""
        while True:
            line = self.thefile.readline()                          # read the next line
            if line == "":                                          # Is this EOF?
                break                                               # yes - just exit loop
            else:
                self.linect += 1                                    # if not, bump line number within file
                line = line.rstrip("\n\r")                          # remove line endings
                if line[0:1] == " " or line[0:1] == "\t":           # if it begins with white space
                    self.prevline += " " + line.strip()             # add a space char and the new line
                else:
                    break                                           # we have a line (prevline) to return

        retline = self.prevline                                     # got a completed line; prepare to return it
        if retline != "":
            retline += "\n"
        self.linenum = self.prevlinenum
        self.prevline = line
        self.prevlinenum = self.linect

        return retline
