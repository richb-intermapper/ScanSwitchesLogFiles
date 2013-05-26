#ScanL2Logs.py

This program scans InterMapper Layer2 log files to give a view of what occurred.

The Layer2 discovery process is a series of SNMP table walks for each device. The L2 code asks for the following tables in sequence:

 * dot1d_Info
 * ifTable
 * ipAddrTable
 * dot1dBasePortTable_csi
 * dot1dstp_Info_csi
 * dot1dStpPortTable_csi
 * cdpCacheTable
 * lldpRemManAddrTable
 * lldpRemTable
 
 The scanl2logs.py program collates all the information about these requests to create the output file (CSV) that looks like this:

	Reading switches.log, /Users/richb/Documents/SwitchesLogFiles/switches.log
	Start Time, End Time, Start Line, End Line, IMID, HexIP, KCid, TableID, IP, Label, SysSvc, TableName, Rows, Diag
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1614, 1645, zzzzzQzzzud, 0a000016, 7+, t27216a8+, 10.0.0.22, NPIF5E00D, Host (64), dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1615, 1649, zzzzzQzzzwd, 0a000018, 8+, t27215c8+, 10.0.0.24, dt151, Host (64), dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1616, 1631, zzzzzQzzz0d, 0a000019, 9+, t2721788+, 10.0.0.25, iR C4080, Host (72), dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1617, 1630, zzzzzQzzz2d, 0a00001b, 10+, t2721868+, 10.0.0.27, 10.0.0.27, Host (72), dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1618, 1632, zzzzzQzzzPd, 0a00001c, 11+, t2721a28+, 10.0.0.28, CANONA34BEE, 0, dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1619, 1644, zzzzzQzzzQd, 0a00001d, 12+, t2721948+, 10.0.0.29, CANONA36E6F, 0, dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1620, 1635, zzzzzQzzz4d, 0a00001e, 13+, t2721b08+, 10.0.0.30, ZBR3822532, L3 SwHub, dot1d_Info, 0, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1654, 1674, zzzzzQzzz4d, 0a00001e, 14+, t27215c8+, 10.0.0.30, ZBR3822532, L3 SwHub, ifTable, 1, 
	 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1663, 1689, zzzzzQzzzud, 0a000016, 15+, t27216a8+, 10.0.0.22, NPIF5E00D, Host (64), ifTable, 2, 
	...
	 2013-05-23 14:20:17,                    , 6905, -, zzzzzQzzCdd, 0a0000d5, 247, -, 10.0.0.213, durham-switch04, 74, -, 0, Never received matching 'KR'; 
	...
	 2013-05-23 14:20:25, 2013-05-23 14:20:25, 9787, 9802, zzzzzOzzzBd, 0a0001d2, 347+, t2721788+, 10.0.1.210, redding-switch01, Host (78), lldpRemManAddrTable, 0, 
	 2013-05-23 14:20:25,                    , 9797, -, zzzzzOzzzBd, 0a0001d2, 348+, t2721788, 10.0.1.210, redding-switch01, Host (78), lldpRemTable, 0, 
	 2013-05-23 14:20:26, 2013-05-23 14:20:38, 9908, 10574, zzzzzOzzzDd, c0a802d2, 349+, t2721948+, 192.168.2.210, sac-switch01, Host (78), cdpCacheTable, 5, 
	 2013-05-23 14:20:26,                    , 9936, -, zzzzzOzzzDd, c0a802d2, 350+, t2721948, 192.168.2.210, sac-switch01, Host (78), lldpRemManAddrTable, 0, 
	 2013-05-23 14:20:26, 2013-05-23 14:20:31, 10034, 10366, zzzzzOzzzCd, 0a0002d2, 351+, t2721b08+, 10.0.2.210, eureka-switch01, Host (78), ipAddrTable, 28, 
	 2013-05-23 14:20:27, 2013-05-23 14:20:31, 10066, 10412, zzzzzOzzzCd, 0a0002d2, 352+, t2721b08+, 10.0.2.210, eureka-switch01, Host (78), dot1dBasePortTable_csi, 0, 
	 2013-05-23 14:20:29,                    , 10099, -, zzzzzQzzCbd, 0a0000d4, 353+, t2721a28, 10.0.0.212, durham-switch03, Host (78), lldpRemTable, 0, 

* The first line gives the path and file name of the file being scanned.
* The second line is a list of the headings for the CSV columns
	* Start Time and End Time show the beginning and end time stamps required to collect this table's data
	* Start Line and End Line are the line numbers of the file that show the line for the start of the table data, and the final line for it.
	* IMID is the InterMapper IMID for the device
	* HexIP is the hexadecimal value of the IP address (*)
	* KCid is the Kali protocol ID that ties together the <KC_opentable command and its resulting <KR response
	* TableID tags each of the <KU_tabledata lines that have an entry for this table
	* IP is the dotted-quad IP address (derived to the HexIP) (*)
	* Label is the first line of the icon's Label (*)
	* TableName is the name of the table being fetched
	* Rows is the number of rows returned for the table
	* Diag contains diagnostic info, if any
	
(*) NB: the fields labelled with an asterisk have been retrieved from an SQL command inserting the data into the database
	
There are several additional flags in the columns of the CSV data:

* KCid is created when the log file contains a <KC_opentable; the KCid gets a "+" appended when the corresponding <KR appears.
* TableID holds the id=... for the table (set in the <KR response) for all related table entries. TableID gets a "+" appended when a "ParseError" appears, indicating the end of that table.
