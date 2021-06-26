import socket
import requests
import json
import datetime
from requests.auth import HTTPBasicAuth
from logs import log_writer
from application import load_config


def checkError(response):
    checkOn = json.loads(response.content)
    try:
        if checkOn["error"]:
            
            msg = "Elasticsearch Request/Response error. Reason: --> {}".format(checkOn['error'])
            log_writer(msg=msg, level="Error")
            return True
    except:
        pass


def authenticate_user(IPAddr):
    global userUrl, Auth, ESuser, ESpassword

    user_info_q = {
            "query": {
            "match": {
            "ip": IPAddr
            }
        }
    }

    if Auth:
        response = requests.get(userUrl, 
                                auth=HTTPBasicAuth(ESuser, ESpassword),
                                headers={"content-type":"application/json"}, 
                                data=json.dumps(user_info_q))

    else:
        response = requests.get(userUrl,
                                headers={"content-type":"application/json"}, 
                                data=json.dumps(user_info_q))

    err = checkError(response)
    if err:
        return

    user_info = json.loads(response.content)
    
    if len(user_info['hits']['hits']) != 0:
        try:
            if len(user_info['hits']['hits']) == 1:
                user = user_info['hits']['hits'][0]['_source']['user']
                return user
            else:
                log_writer(msg="More than one user. Configuration Error", level="Fatal")
                return

        except:
            log_writer(msg="Unable to parse user from recieved logs.", level="Fatal")
            return
    
    else:
        log_writer(msg="User not found on elasticsearch database.", level="Error")
        return

def check_update(recieved_log):

    new = False
    with open('log.json', 'r') as logfile:
            data=logfile.read()
            # Loading configuration setting
            log = json.loads(data)
    
    if len(log) >= 5:
        log = log[len(log)-5:]

    recieved_log = recieved_log['hits']['hits']

    now = datetime.datetime.now()
    yes = now - datetime.timedelta(days=1)
    dayB = now - datetime.timedelta(days=2)

    today = now.strftime("%Y-%m-%d")
    yesterday = yes.strftime("%Y-%m-%d")
    day_before = dayB.strftime("%Y-%m-%d")

    # Formatting recieved log for comparison
    r_dates = []
    r_content = []
    for i in recieved_log:
        r_dates.append(i['_source']['date'])
        i['_source'].pop('user')
        r_content.append(i['_source'])
    
    log_to_update = []
    push_on_day = []

    if today not in r_dates:
        for i in log:
            if i['date'] == today:
                log_to_update.append(i)
                new = True
                push_on_day.append(i['date'])

    if yesterday not in r_dates:
        for i in log:
            if i['date'] == yesterday:
                log_to_update.append(i)
                new = True
                push_on_day.append(i['date'])
    
    if day_before not in r_dates:
        for i in log:
            if i['date'] == day_before:
                log_to_update.append(i)
                new = True
                push_on_day.append(i['date'])

    check = [] 

    for i in log:
        if i['date'] in r_dates:
            check.append(i)
    
    for j in check:
        if j not in r_content:
            log_to_update.append(j)

    return log_to_update , new, push_on_day



def send_logs():
    global Auth, ESpassword, ESuser, logUpdateUrl, logSearchUrl, logPostUrl

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPAddr = s.getsockname()[0]

    # -- Date Formatting --
    now = datetime.datetime.now()
    yes = now - datetime.timedelta(days=1)
    dayB = now - datetime.timedelta(days=2)
    today = now.strftime("%Y-%m-%d")
    yesterday = yes.strftime("%Y-%m-%d")
    day_before = dayB.strftime("%Y-%m-%d")

    # User Authentication
    user = authenticate_user(IPAddr)
    
    if user == None:
        log_writer(msg="User authentication failed. Not sending logs.", level="Error")
        return

    user = user.lower()
    
    get_query =   {
        "query": { 
            "bool" : {
                "must" : [ {                    
                    "terms" : {
                        "user" : [user]
                        }
                        }, 
                        {
                            "terms" : {
                                "date" : [today,yesterday,day_before]
                            }
                        } 
                        ]
                    }
                }
             }

    if Auth:
        response = requests.get(logSearchUrl,
                                headers={"content-type":"application/json"},
                                auth=HTTPBasicAuth(ESuser, ESpassword),
                                data = json.dumps(get_query))
    
    else:
        response = requests.get(logSearchUrl,
                                headers={"content-type":"application/json"},
                                data = json.dumps(get_query))


    err = checkError(response)
    if err:
        return

    get_response = json.loads(response.content)
    
    log_to_update, new_log , missing_log_date = check_update(get_response)

    if new_log:
        for i in missing_log_date:
            for j in log_to_update:
                if j['date'] == i:
                    j['user'] = user

                    if Auth:
                        response = requests.post(logPostUrl,
                                headers={"content-type":"application/json"},
                                auth=HTTPBasicAuth(ESuser, ESpassword),
                                data = json.dumps(j))

                    else:
                        response = requests.post(logPostUrl,
                                headers={"content-type":"application/json"},
                                data = json.dumps(j))

                    
                    err = checkError(response)
                    if err:
                        return

                    log_to_update.remove(j) # Remove the posted log from date
    
    
    for j in log_to_update:
        update_source= ""
        params = {}
        for k in j['application']:
            key = k.replace(' ','')
            update_source = update_source + "ctx._source.application." + key + "= params." + key +"; " 
            params[key] = j['application'][k]

        update_source = update_source + "ctx._source.idletime=" + str(j['idletime'])
        
        
        update_query={
        "query": { 
            "bool" : {
                "must" : [ {                    
                    "terms" : {
                        "user" : [user]
                        }
                        }, 
                        {
                            "terms" : {
                                "date" : [j['date']]
                            }
                        } 
                        ]
                    }
                },

        "script" : {
            "source": update_source,
            "lang": "painless",
            "params":params
        }
        }

        if Auth:
            response = requests.post(logUpdateUrl,
                                headers={"content-type":"application/json"},
                                 auth=HTTPBasicAuth(ESuser, ESpassword),
                                data = json.dumps(update_query))
        else:
            response = requests.post(logUpdateUrl,
                                headers={"content-type":"application/json"},
                                data = json.dumps(update_query))

       
        err = checkError(response)
        if err:
            return
    
   
if __name__ == "__main__":
    configsetting = load_config()
    
    Auth = configsetting['Auth']
    if Auth:
        ESuser = configsetting['ESuser']
        ESpassword = configsetting['ESPassword']

    url = configsetting['Protocol'] + "://" + configsetting['ElasticsearchIP'] + ":" + configsetting["ElasticsearchPort"] + "/"
    userUrl = url + configsetting['AuthIndex'] + "/_search"
    logSearchUrl = url + configsetting['LogIndex'] + "/_search"
    logPostUrl = url + configsetting['LogIndex'] + "/_doc"
    logUpdateUrl = url + configsetting['LogIndex'] + "/_update_by_query"

    send_logs()
    
    

    
    

