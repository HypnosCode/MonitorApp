
# Application Monitoring

The following github repository contains scripts intended to monitor
application usage and idle-time spent by user.

#### works in integration with: -- EMS link --

Their are three folders which equivalents to respective Operating System. Clone 
the corresponding folder accordingly.

Note:
Scripts work in iteration of for loop executed every 2 min so expected stat error is 2 min.



## Installation 

Clone from github

```bash 
  git clone -- link -- 
```
After cloning, go to corresponding folder. All folders have same file 
underneath. 
```
Windows
        - application.py
        - elasticsearch.py
        - logs.py

```
Now it is as easy as

```
python application.py
```

Note: For linux please pre install "xprintidle"

```bash
sudo apt install xprintidle
```




    
## Usage and Example

After executing application.py, you should have 3 additional file created namely,

<sub> Note: The file will only be created if executed for first time else same file will be used for further executions. </sub>
```
- config.json
- log.json
- runtime.log
```
- "config.json" holds configuration setting.
- "log.json" is where actual monitored logs are written.
- "runtime.log" logs runtime information for debugging purposes.

Your config file will have following structure:

```json
{
      "Applications": [],
      "ElasticsearchIP": "-",
      "ElasticsearchPort": "-",
      "AuthIndex": "-",
      "LogIndex": "-",
      "Protocol": "-",
      "Auth": false,
      "ESuser": "-",
      "ESPassword": "-"
}
```
To monitor application usage of any application 
just append it to application list likewise.
Make sure that application names are Case sensitive so configure accordingly.


```json
{
      "Applications": ["Brave Browser"],
      "ElasticsearchIP": "-",
      "ElasticsearchPort": "-",
      "AuthIndex": "-",
      "LogIndex": "-",
      "Protocol": "-",
      "Auth": false,
      "ESuser": "-",
      "ESPassword": "-"
}
```

Your "log.json" file will be updated accordingly.

```json
[
      {
            "date": "2021-06-26",
            "application": {
                  "BraveBrowser": 2
            },
            "idletime": 0
      }
]
```
If you want these logs to be updated to elasticsearch add 
params to "config.json" accordingly and execute "elasticsearch.py"

configuration file with elasticsearch config might 
resemble something like this

```json
{
      "Applications": ["Brave Browser"],
      "ElasticsearchIP": "localhost", # where elasticsearch server is hosted
      "ElasticsearchPort": "9200", # port likewise
      "AuthIndex": "user-information", # authenticate if current pc is allowed to post log to LogIndex 
      "LogIndex": "application-information", # where monitored logs are pushed
      "Protocol": "http", # or https 
      "Auth": false, # if you have configured username and password for elasticsearch set this to true
      "ESuser": "-", # elasticsearch username for authentication
      "ESPassword": "-" # elasticsearch password for authentication
}
```



## Tech Stack

**Language:** Python \
**Client:** : Python \
**Server:** Elasticsearch (if configured) \
**Issues Expected:** True \
**Currently Maintained:** True

For any issues encountered during execution, reach out to one of 
following contributor via mail. 

- gsakshyam3@gmail.com
- prayagpiya12@gmail.com
- amulshrestha.com@gmail.com




  