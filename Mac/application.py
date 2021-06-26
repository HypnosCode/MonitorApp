import subprocess
import json
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import psutil
from logs import log_writer

def load_config():
    # Check if config file exists
    try:
        configfile = open('config.json', 'r')
    except:
        log_writer(msg="Configuration file not found. Creating new configuration file instance.", level="Info")
        config_file = open('config.json','w')
        f_log = { "Applications":[], "ElasticsearchIP":"-", "ElasticsearchPort":"-", "AuthIndex":"-", "LogIndex":"-", "Protocol":"-", "Auth":False, "ESuser":"-", "ESPassword":"-"}
        json.dump(f_log, config_file, indent=6)
        config_file.close()
        configfile = open('config.json', 'r')
    
    # reading contents of configuration file
    try:
        data=configfile.read()
        # Loading configuration setting
        configsetting = json.loads(data)
        return configsetting
    
    except:
        log_writer(msg="Unable to read configuration file", level="Fatal")
        return



def update_log(date,applicationList,idleTime):
    
    try:
        log_file = open('log.json','r')
    except:
        log_file = open('log.json','w')
        f_log = '[]'
        log_file.write(f_log)
        log_file.close()
        log_writer(msg="No previous log file found. Assuming first time installation and creating new log file.", level="Info")
        log_file = open('log.json','r')

    
    # loading previous log file
    try:
        read_logs = log_file.read()
        log_file.close()
        logs = json.loads(read_logs)
    
    except:
        log_writer(msg="Unable to read log file.", level="Fatal")
        return

    # checking if newly installed
    if len(logs) != 0:
        # checking if last log is of today or other day
        if date == logs[-1]['date']:
            print('date matched')
            for i in applicationList:
                i = i.replace(' ','')
                print('adding log for {}'.format(i))
                try:
                    logs[-1]['application'][i] += 2
                    print('s')
                except:
                    logs[-1]['application'][i] = 2
                    print('e')

            logs[-1]['idletime'] += idleTime
            
            log_file = open('log.json', 'w')
            json.dump(logs, log_file, indent=6)
            log_file.close()
            return
    
    
    new_log = {}
    new_log['date'] = date
    new_log['application'] = {}
    for i in applicationList:
        i.replace(' ','')
        new_log['application'][i] = 2
    new_log['idletime'] = idleTime
    logs.append(new_log)

    log_file = open('log.json', 'w')
    json.dump(logs, log_file, indent=6)
    log_file.close()
    return 




def activity_monitoring():
    print('call',+1)
    current_running_application = []
    applications_to_update = []
    
    for proc in psutil.process_iter():
        current_running_application.append(proc.name())

    configsetting = load_config()

    if configsetting == None:
        log_writer(msg="Configuration file error. Abandonig monitoring activity", level="Fatal")
        return 

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    
    for i in current_running_application:
        if i in configsetting['Applications']:
            applications_to_update.append(i)
    
    idleTime = float(get_idle_duration())
    if idleTime >= 120:
        idleTime = 2
    else:
        idleTime = 0

    print("date: {} \n applications: {} \n idletime: {} \n".format(date,applications_to_update,idleTime))
    update_log(date,applications_to_update,idleTime)


        
def get_idle_duration():
    import subprocess
    ' -- run the command -- I would but i have no way of checking'
    pass 


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(activity_monitoring, 'interval', minutes=2)
    scheduler.start()   
