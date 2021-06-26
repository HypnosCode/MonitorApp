import datetime
import json


def log_writer(msg,level):
    level = level.lower()
    f = open('runtime.log','a+')
    now = datetime.datetime.now()
    date = now.strftime("%Y-%B-%d-%a")
    time = now.strftime("%H:%m:%S")

    dic = {
        "Date":date,
        "Time":time,
        "Level":level,
        "Message":msg
    }
    print(date,time)
    json.dump(dic,f,indent=6)
    f.close()

