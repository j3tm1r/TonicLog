__author__ = 'Jetmir'

import urllib.request as request
import json
import csv
import os
import os.path

from enum import Enum

class EventSource(Enum):
    PalazzoMadama = 'com.tonicminds.palazzomadama'
    Intrigo = 'Intrigo'
    Launcher = 'Launcher'
    SeriousGame = 'com.tonicminds.palazzomadama.seriousgame'

class DeviceId(Enum):
    deeee = 1





class EventRecord:
    def __init__(self):
        self.id
        self.args
        self.timestamp
        self.device_id
        self.type
        self.source = EventSource.Launcher

def downloadEvents(source):
    url = "http://www.tonicminds.com/log/log.php?iDisplayLength="
    data = request.urlopen(url+'5').read().decode('utf-8')
    data = json.loads(data)

    records = data['iTotalRecords']

    data = request.urlopen(url+str(records)).read().decode('utf-8')
    data = json.loads(data)
    data = data['events']
    events_list = []
    for event in data:
        if (event['event'])['source']  == source.value :
            events_list.append(event)
    return  events_list

def getRows(data, source):
    events_list = []
    for event in data:
        if (event['event'])['source']  == source.value :
            events_list.append(event)
    print(len(events_list))

    return []

intrigo_logs = "intrigo.logs"

if os.path.isfile(intrigo_logs) and os.access(intrigo_logs, os.R_OK):
    print("File exists and is readable")
else:
    data = downloadEvents(EventSource.Intrigo)
    file = open(intrigo_logs,"w")
    file.write('{"events":[')
    notFirst = False
    for line in data:
        if notFirst :
            file.write(',\n')
        else:
            notFirst = True
        file.write(json.dumps(line))
    file.write('\n]}')
    file.close();

fname = "intrigo.csv"
with open(fname,'wb') as outf:
    outcsv = csv.writer(outf)
   # outcsv.writerows(getRows(data,EventSource.Intrigo))
