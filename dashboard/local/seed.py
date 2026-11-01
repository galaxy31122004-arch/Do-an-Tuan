"""Provision this project's local ThingsBoard demo only; never targets a remote server."""
import argparse
import copy
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ORIGIN='http://127.0.0.1:18080'
SESSION=ROOT/'session.json'
AUTH=None

def api(path, body=None, method=None):
    headers={'Content-Type':'application/json'}
    if AUTH: headers['X-Authorization']='Bearer '+AUTH
    request=urllib.request.Request(ORIGIN+path, data=None if body is None else json.dumps(body).encode(),headers=headers,method=method or ('GET' if body is None else 'POST'))
    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            raw=response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'{path}: HTTP {exc.code}: '+exc.read().decode()[:600]) from None

def condition(key, operation, value, kind='NUMERIC', attribute=None):
    target={'defaultValue':value}
    if attribute: target['dynamicValue']={'sourceType':'CURRENT_DEVICE','sourceAttribute':attribute,'inherit':False}
    return {'key':{'type':'TIME_SERIES','key':key},'valueType':kind,
            'predicate':{'type':kind,'operation':operation,'value':target}}

def alarm(name, create, clear):
    def rule(conditions): return {'condition':{'condition':conditions,'spec':{'type':'SIMPLE'}},'schedule':{'type':'ANY_TIME'}}
    return {'id':str(uuid.uuid5(uuid.NAMESPACE_URL,'env-monitor/'+name)),'alarmType':name,
            'createRules':{'WARNING':rule(create)},'clearRule':rule(clear),'propagate':False}

def provision():
    global AUTH
    AUTH=api('/api/auth/login',{'username':'tenant@thingsboard.org','password':'tenant'})['token']
    profiles=api('/api/deviceProfiles?pageSize=100&page=0')['data']
    profile=next((p for p in profiles if p['name']=='ENV Monitor NTP'),None)
    if profile is None:
        profile={'name':'ENV Monitor NTP','description':'Local demo: PIC, ESP32-C3, NTP, no external RTC',
                 'type':'DEFAULT','transportType':'DEFAULT','provisionType':'DISABLED','default':False,
                 'profileData':{'configuration':{'type':'DEFAULT'},'transportConfiguration':{'type':'DEFAULT'},'provisionConfiguration':{'type':'DISABLED'}}}
        rules=[]
        valid=condition('sensor_ok','EQUAL',True,'BOOLEAN')
        for key,unit,default_min,default_max in [('temperature','Temperature',20,28),('humidity','Humidity',40,75)]:
            rules.append(alarm(unit+' high',[valid,condition(key,'GREATER',default_max,attribute=key+'_max')],[valid,condition(key,'LESS_OR_EQUAL',default_max,attribute=key+'_max')]))
            rules.append(alarm(unit+' low',[valid,condition(key,'LESS',default_min,attribute=key+'_min')],[valid,condition(key,'GREATER_OR_EQUAL',default_min,attribute=key+'_min')]))
        rules.append(alarm('Sensor fault',[condition('sensor_ok','EQUAL',False,'BOOLEAN')],[valid]))
        profile['profileData']['alarms']=rules
        profile=api('/api/deviceProfile',profile)
    # The stock demo Root Rule Chain only saves telemetry; give this profile its own
    # processing chain with the Device Profile node so native alarm rules execute.
    chains=api('/api/ruleChains?pageSize=100&page=0')['data']
    chain=next((c for c in chains if c['name']=='ENV Monitor Processing'),None)
    if chain is None:
        original=next(c for c in chains if c.get('root'))
        metadata=api('/api/ruleChain/'+original['id']['id']+'/metadata')
        chain=api('/api/ruleChain',{'name':'ENV Monitor Processing','type':'CORE','root':False,'debugMode':False})
        nodes=copy.deepcopy(metadata['nodes'])
        for node in nodes:
            for field in ['id','createdTime','ruleChainId','tenantId','externalId']: node.pop(field,None)
        first=len(nodes)
        nodes.append({'name':'Evaluate profile alarms','type':'org.thingsboard.rule.engine.profile.TbDeviceProfileNode',
                      'debugMode':False,'configuration':{'persistAlarmRulesState':False,'fetchAlarmRulesStateOnStart':False},'additionalInfo':{'layoutX':80,'layoutY':80}})
        connections=metadata['connections']+[{'fromIndex':first,'toIndex':metadata['firstNodeIndex'],'type':'Success'}]
        api('/api/ruleChain/metadata',{'ruleChainId':chain['id'],'firstNodeIndex':first,'nodes':nodes,'connections':connections,'ruleChainConnections':None})
    profile=api('/api/deviceProfile/'+profile['id']['id'])
    if profile.get('defaultRuleChainId')!=chain['id']:
        profile['defaultRuleChainId']=chain['id'];profile=api('/api/deviceProfile',profile)
    try:
        device=api('/api/tenant/devices?deviceName=ENV-MONITOR-01')
    except RuntimeError as exc:
        if 'HTTP 404' not in str(exc): raise
        device=None
    if not device:
        device=api('/api/device',{'name':'ENV-MONITOR-01','label':'PIC + ESP32-C3 — SIMULATED DATA','type':'ENV Monitor NTP','deviceProfileId':profile['id']})
    elif device.get('label')!='PIC + ESP32-C3 — SIMULATED DATA':
        device['label']='PIC + ESP32-C3 — SIMULATED DATA';device=api('/api/device',device)
    ident=device['id']['id']
    api(f'/api/plugins/telemetry/DEVICE/{ident}/SERVER_SCOPE',{'temperature_min':20,'temperature_max':28,'humidity_min':40,'humidity_max':75,'inactivityTimeout':60000})
    credentials=api(f'/api/device/{ident}/credentials')
    token=credentials['credentialsId']
    records=[]; now=int(time.time()*1000)
    for i in range(181):
        records.append({'ts':now-(180-i)*20000,'values':{'temperature':round(27+2.5*math.sin(i/12),1),'humidity':round(65+6*math.cos(i/15),1),'sensor_ok':True,'time_ok':True,'demo':True,'rssi':-55,'sequence':i}})
    api('/api/v1/'+urllib.parse.quote(token)+'/telemetry',records)
    dashboard=json.loads((ROOT.parent/'environment-monitor.json').read_text(encoding='utf-8'))
    dashboard['title']='ENV Monitor — ESP32-C3 · SIMULATED DATA'
    existing=api('/api/tenant/dashboards?pageSize=100&page=0')['data']
    old=next((d for d in existing if d['title']==dashboard['title']),None)
    if old is None and SESSION.exists():
        previous=json.loads(SESSION.read_text(encoding='utf-8'))
        old=next((d for d in existing if d['id']['id']==previous.get('dashboard_id')),None)
    if old: dashboard['id']=old['id']
    dashboard=api('/api/dashboard',dashboard)
    state={'device_id':ident,'dashboard_id':dashboard['id']['id'],'device_token':token,'url':ORIGIN+'/dashboard/'+dashboard['id']['id']}
    SESSION.write_text(json.dumps(state,indent=2),encoding='utf-8')
    print(json.dumps({'url':state['url'],'widgets':len(dashboard['configuration']['widgets']),'profile':'ENV Monitor NTP','alarm_rules':5,'demo':True},ensure_ascii=False))

def stream():
    global AUTH
    AUTH=None
    state=json.loads(SESSION.read_text(encoding='utf-8'))
    start=time.monotonic(); sequence=1000
    while True:
        elapsed=time.monotonic()-start
        payload={'temperature':round(27.5+2*math.sin(elapsed/90),1),'humidity':round(65+4*math.sin(elapsed/70),1),
                 'sensor_ok':True,'time_ok':True,'demo':True,'rssi':-55,'sequence':sequence}
        try: api('/api/v1/'+urllib.parse.quote(state['device_token'])+'/telemetry',payload)
        except Exception as exc:
            with (ROOT/'demo.log').open('a',encoding='utf-8') as log: log.write(str(exc)+'\n')
        sequence+=1; time.sleep(10)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stream',action='store_true');args=parser.parse_args()
    stream() if args.stream else provision()
