"""Generate a native ThingsBoard dashboard from official widget defaults.

No account access or external writes. Network reads only; committed output imports offline.
Schema reference: RSCH-20261101-0003. Upstream: Apache-2.0, ThingsBoard Authors.
"""
import copy
import json
import uuid
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 'https://raw.githubusercontent.com/thingsboard/thingsboard/master/application/src/main/data/json/'
ALIAS = 'eab25daf-e089-44a4-b1f9-84fb5431b250'

def fetch(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as response:
        return json.load(response)

def key(name, label, color='#2563eb', kind='timeseries'):
    return dict(name=name, label=label, color=color, type=kind, settings={})

def datasource(keys):
    return [dict(type='entity', entityAliasId=ALIAS, name='Environment monitor', dataKeys=keys)]

def main():
    reference = fetch('demo/dashboards/thermostats.json')
    templates = list(reference['configuration']['widgets'].values())
    value = fetch('system/widget_types/value_card.json')
    table = fetch('system/widget_types/timeseries_table.json')
    widgets, layout = {}, {}

    def add(widget, name, x, y, width, height):
        ident = str(uuid.uuid5(uuid.NAMESPACE_URL, 'env-monitor/' + name))
        widget = copy.deepcopy(widget)
        widget.update(id=ident, sizeX=width, sizeY=height, col=x, row=y)
        widget['config'].update(title=name, titleColor='#0f172a', borderRadius='12px', margin='0px')
        widgets[ident] = widget
        layout[ident] = dict(sizeX=width, sizeY=height, col=x, row=y, mobileOrder=len(widgets), mobileHeight=height)
        return widget['config']

    def card(name, telemetry, units, x, y, color, kind='timeseries', icon='sensors'):
        cfg = json.loads(value['descriptor']['defaultConfig'])
        cfg.update(datasources=datasource([key(telemetry, name, color, kind)]), units=units, decimals=1 if units else 0)
        cfg['settings'].update(icon=icon, showDate=True)
        cfg['settings']['iconColor']['color'] = color
        add(dict(typeFullFqn='system.'+value['fqn'], type='latest', config=cfg), name, x,y,8,4)

    card('Nhiệt độ', 'temperature', '°C', 0,0,'#ef6c38',icon='thermostat')
    card('Độ ẩm', 'humidity', '%RH', 8,0,'#0284c7',icon='water_drop')
    card('Thiết bị hoạt động (true/false)', 'active', '',16,0,'#059669','attribute','wifi')
    for title,telemetry,x,color,unit in [('Lịch sử nhiệt độ','temperature',0,'#ef6c38','°C'),('Lịch sử độ ẩm','humidity',12,'#0284c7','%RH')]:
        template = next(w for w in templates if w.get('typeFullFqn')=='system.time_series_chart')
        cfg = add(template,title,x,4,12,7)
        data_key=key(telemetry,title,color)
        # Points make an offline interval visible without drawing an interpolated bridge.
        data_key['settings']={'type':'line','yAxisId':'default','showInLegend':True,'lineSettings':{'showLine':False,'showPoints':True,'pointSize':4,'smooth':False}}
        cfg.update(datasources=datasource([data_key]),useDashboardTimewindow=True,displayTimewindow=True,enableDataExport=True,units=unit)
    cfg=json.loads(table['descriptor']['defaultConfig'])
    cfg.update(datasources=datasource([key('temperature','Nhiệt độ'),key('humidity','Độ ẩm'),key('sensor_ok','Cảm biến hợp lệ'),key('rtc_ok','RTC hợp lệ'),key('demo','Dữ liệu giả lập')]),useDashboardTimewindow=True,enableDataExport=True)
    add(dict(typeFullFqn='system.'+table['fqn'],type='timeseries',config=cfg),'Lịch sử đo / xuất CSV',0,11,14,8)

    template=next(w for w in templates if 'update_multiple_attributes' in w.get('typeFullFqn',''))
    cfg=add(template,'Cấu hình ngưỡng cảnh báo',14,11,10,8)
    fields=[]
    for name,label,low,high in [('temperature_min','Nhiệt độ thấp (°C)',0,50),('temperature_max','Nhiệt độ cao (°C)',0,50),('humidity_min','Độ ẩm thấp (%RH)',0,100),('humidity_max','Độ ẩm cao (%RH)',0,100)]:
        item=key(name,label,kind='attribute')
        item['settings']={'dataKeyType':'server','dataKeyValueType':'double','required':True,'isEditable':'editable','dataKeyHidden':False,'step':1,'min':low,'max':high}
        fields.append(item)
    cfg.update(datasources=datasource(fields))
    cfg['settings'].update(showActionButtons=True,showResultMessage=True,widgetTitle='Ngưỡng trên nền tảng',groupTitle='ENV-MONITOR-01',fieldsInRow=1)

    template=next(w for w in templates if w.get('type')=='alarm')
    cfg=add(template,'Lịch sử cảnh báo',0,19,24,7)
    cfg['alarmSource']['entityAliasId']=ALIAS
    cfg.update(useDashboardTimewindow=True)
    card('Cảm biến hợp lệ (true/false)','sensor_ok','',0,26,'#059669')
    card('RTC hợp lệ (true/false)','rtc_ok','',8,26,'#7c3aed')
    card('Giả lập (true/false)','demo','',16,26,'#d97706')

    result=dict(title='ENV Monitor — PIC + ESP32',image=None,mobileHide=False,mobileOrder=0,
        configuration=dict(description='DHT11 / DS1307 / SSD1315 — One-device IoT monitoring',
            widgets=widgets,entityAliases={ALIAS:dict(id=ALIAS,alias='ENV-MONITOR-01',filter=dict(type='entityName',entityType='DEVICE',resolveMultiple=False,entityNameFilter='ENV-MONITOR-01'))},
            timewindow=dict(displayValue='',selectedTab=0,realtime=dict(interval=1000,timewindowMs=3600000),aggregation=dict(type='NONE',limit=2000)),
            settings=dict(stateControllerId='entity',showTitle=True,showDashboardsSelect=False,showDashboardTimewindow=True,showDashboardExport=True,toolbarAlwaysOpen=True),
            states=dict(default=dict(name='Giám sát môi trường',root=True,layouts=dict(main=dict(widgets=layout,gridSettings=dict(columns=24,backgroundColor='#f1f5f9',margin=12,outerMargin=True,mobileRowHeight=55,layoutType='default')))))))
    (ROOT/'environment-monitor.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Generated {len(widgets)} native widgets; device name ENV-MONITOR-01')

if __name__=='__main__': main()
