import sys
import time
import os
# import Jira
# import EJmap as EJ
# import PicNumCheck as P

# jira.projects()
# project = jira.project(20483)
# project.__dict__
# for i in range(len(project.components)):
#   print(project.components)

loginJira = {
    'JiraUser': 'SESA504595',
    'JiraPasswd': 'Passwd',
}
# jira.statuses()
Jedi_components = [
    '700: FVT - Test Platform',
    '701: FVT - Test Execution',
    '702: FVT - Test Spec',
    '800: HW - Platform',
    '801: HW - Power Module 50kW',
    '802: HW - IMC',
    '803: HW - PMC',
    '804: HW - SMC',
    '805: HW - SBSC',
    '806: HW - SBS200lW',
    '807: HW - Frame',
    '900: FW - Platform',
    '901: FW - IMC',
    '902: FW - PMC',
    '903: FW - SBSC',
    '904: FW - SMC',
    '905: FW - HMI',
    '906: FW - NMC',
    '907: FW - BMC',
    '908: FW - Tuner Software',
    '910: FW - Control architecture',
    '911: FW - Data Dictionary',
    'AS-AUX',
    'AS-PCBA',
    'AS-PM50',
    'AS-SBS',
    'AS-UPS',
    'FW - Modbus Debug Tool',
    'HW - Ctrl System',
    'SHH'
]
# for i in range(len(project.versions)):
#     print(project.versions[i])
Jedi_Version = [
    'SP00',
    'SP01',
    'SP02',
    'SP03',
    'SP04',
    'SP05',
    'SP06',
    'SP07',
    'SP08',
    'SP10',
    'SP09',
    'KP1.5',
    'KP2',
    'SP11',
    'SP12',
    'SP13',
    'SP81',
    'EP1',
    'EP2',
    'SP80',
    'MP',
    'EP1.1',
    'Pilot',
    'SP14',
    'SP15'
]

IssueType = [
    'Epic',
    'SysEpic',
    'Story',
    'Task',
    'Defect',
    'Hardware',
    'Mechanical',
    'Manufacturing',
    'Change Request',
    'Process Improvement',
    'Specification',
    'New Feature',
    'Customer Request',
    'Product Quality',
    'Sub-task'
]

Priority_level = {
    '1 - Unavoidable Crash': 'high',
    '2 - Avoidable Crash': 'high',
    '3 - Functionality': 'medium',
    '5 - Enhancement': 'low',
    '4 - Customer Expectation': 'low',
}

Status_J2Z = {
    'Open': 'open',                                #1
    'In Progress': 'ongoing',                   #4
    'Reopened': 'reopened',                     #3
    'Resolved': 'resolved',                     #5
    'Closed': 'closed',                             #2
}

SeriesName_IssueType = {
    '设计相关': 'Hardware',
    '生产制造': 'Manufacturing',
    '来料相关': 'Manufacturing',
    '文件相关': 'Manufacturing',
    '待完成任务': 'Task'
}

assignee = {
    '设计相关': 'SESA428980',
    '生产制造': 'SESA472101',
    '来料相关': 'SESA508806',
    '文件相关': 'SESA508806',
    '待完成任务': 'SESA508806'
}

'''
Jira issue 创建new jira时根据需求添加需的field
'''
issue_dict = {
    'project': {'key': 'JEDI'},
    'issuetype': {'name': 'Defect'},
    'summary': 'test',                                        #Summary
    'priority': {'name': '3 - Functionality'},                             #Priority
    'customfield_10679': 0,                                    #Severity
    'customfield_10680': 0,                                     #Occurence
    'customfield_10681': 10,
    'components': [{'name': '905: FW - HMI'}],                       #Component
    'versions': [{'name': 'EP1'}],                     #Affect_Version
    'assignee': {'name': 'SESA509433'},
#   'labels': [Lablels],
    'customfield_13603': {'value': 'GPX CR1'},                  #Project_Scope
    'description': 'test',
#    'comments': 'test'
}

'''
Jira issue 更新已有jira时根据需求添加需的field
#=========================================将需要同步的field在此处修改 step 3 对应 step1
'''
issue_dict_u = {
    'summary': 'test',                                        #Summary
    'priority': {'name': '3 - Functionality'},                        #Priority
    'customfield_10679': 0,                                    #Severity
    'customfield_10680': 0,                                     #Occurence
    'customfield_10681': 10,
#    'components': [{'name': Jedi_components[1]}],                       #Component
    'versions': [{'name': 'EP1'}],                      #Affect_Version                  多版本会出问题
#   'assignee': {'name': 'test'},                             # 需要给出人名列表(sesa)
#   'labels': [Lablels],
    'customfield_13603': {'value': 'GPX CR1'},                  #Project_Scope
    'description': 'test',
#    'status': {'name': 'Open'}
#    'comments': 'test'
}

def Log(msg):
    print('Print Message: '+msg+' ,File: "'+__file__+'", Line '+str(sys._getframe().f_lineno)+' , in '+sys._getframe().f_code.co_name)

def sync_time():
    '''
    每次同步后，记录时间,写入文件sync_time.txt
    '''
    now = time.time()
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    st_log = open('sync_time.txt','a')
    st_log.write(str(dt) + '\n')
    st_log.write(str(int(now))+'\n')
    st_log.close()
    return int(time.time())
# sync_time()
def get_last_sync_time(index=-1):
    '''
    获取上次更新的时间，用于筛选问题更新列表
    这里会有一个issue，在同步的过程中同时产生的更新可能会丢失，尽管概率很低
    :type index: object
    '''
    st_log = open('sync_time.txt','r')
    last_time = st_log.readlines()[index]
    st_log.close()
    return last_time

def add_map_log(key, value, filename='EJmap.py'):
    lines = []
    f = open(filename, 'r')
    for line in f:
        lines.append(line)
    f.close()
    if isinstance(value,tuple):
        fmt ="\t"+ str(key)+ ":"+ str(value) + ',' + '\n'
    else:
        fmt ="\t"+ str(key)+ ":" + "'" +str(value)+"'"+ ',' + '\n'
    lines.insert(-1,fmt)
    s = ''.join(lines)
    f = open(filename,'w+')
    f.write(s)
    f.close()
    del lines[:]

def all_pictures():
    listall = os.listdir()
    jpg = []
    for i in range(len(listall)):
        if listall[i].endswith('jpg'):
            jpg.append(listall[i])
    return jpg

def get_pic_number(id, jpg):
    total = []
    n1 = 0
    n2 = 0
    # imp_pic = []
    for i in range(len(jpg)):
        if jpg[i].startswith(str(id)):
            total.append(jpg[i])
        if jpg[i].startswith(str(id) + '_improve'):
            n2 = n2 + 1
    n1 = len(total) - n2
    return (total, n1, n2)

