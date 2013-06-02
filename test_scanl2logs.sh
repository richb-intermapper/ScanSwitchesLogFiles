# Shell script to run scanl2logs.py on each of the sample log files

python scanl2logs.py -i "CustomerInfo/DD/com.dartware.switches/switches.log.2013_05_23" -o CustomerInfo/Results/dd.csv

python scanl2logs.py -i "CustomerInfo/PQ#2/166.77.200.105-8181-switches.log" -o CustomerInfo/Results/pq.csv

python scanl2logs.py -i "CustomerInfo/EM/192.168.100.26-8181-switches.log" -o CustomerInfo/Results/em.csv

python scanl2logs.py -i "CustomerInfo/AL/com.dartware.switches/switches.log" -o CustomerInfo/Results/al.csv

python scanl2logs.py -i "CustomerInfo/RB/127.0.0.1-8181-switches.log" -o CustomerInfo/Results/rb.csv

python scanl2logs.py -i "CustomerInfo/MVS/127.0.0.1-8181-switches.log" -o CustomerInfo/Results/mvs.csv

python scanl2logs.py -i "CustomerInfo/Splunk/com.dartware.switches/switches.log" -o CustomerInfo/Results/Splunk.csv

