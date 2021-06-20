import copy
from jira import JIRA
import time
# import ZL
import EJmap as EJ
import common as C
import PicNumCheck as P

jira = JIRA(server='http://jira.ams.apc.com', basic_auth=(C.loginJira['JiraUser'], C.loginJira['JiraPasswd']))

#=========================================将需要同步的field在此处修改 step 3.1 对应 step1
def update_issue(issueid_list,issue_list):
    '''
    批量更新Jira
    issue_list: from ZL interface 获取数据，在jira中做相应更新的issue 列表
    issueid_list ZL 中的id 和issue_list 一一对应 [id1,id2,....]
    issue_dict: 部分fields 值从 issue list（其数据结构在 ZL.py get_issue_fields_list函数中定义）获取 [{fields1},{fields2}....]
    '''
    issue_l = []
    for i in range(len(issue_list)):
        issue_l.append(copy.deepcopy(C.issue_dict_u))
        issue_l[i]['summary'] = issue_list[i]['summary']
        issue_l[i]['description'] = issue_list[i]['description']
        try:
            issue_l[i]['customfield_10679'] = int(issue_list[i]['customfield_10679'])               #None 会出错
            issue_l[i]['customfield_10680'] = int(issue_list[i]['customfield_10680'])
            issue_l[i]['customfield_10681'] = int(issue_list[i]['customfield_10681'])
        except:
            print('CHECK S O D value, please ',issueid_list[i])
        # issue_l[i]['issuetype']['name'] = issue_list[i]['issuetype']
        # issue_l[i]['components'][0]['name'] = issue_list[i]['components']
        if issue_list[i]['versions'] in C.Jedi_Version:
            issue_l[i]['versions'][0]['name'] = issue_list[i]['versions']
        else:
            issue_l[i]['versions'][0]['name'] = 'EP1.1'
        jira.issue(EJ.map_tab[issueid_list[i]]).update(fields=issue_l[i])
        issue = jira.issue(EJ.map_tab[issueid_list[i]])
        # print(issue.fields.status.name)
        # print(issue_list[i]['status'])
        if issue_list[i]['status'] == 'Closed' and issue.fields.status.name == 'Resolved':
            try:
                jira.transition_issue(EJ.map_tab[issueid_list[i]], transition='701')
                print('The Jira %s is CLOSED'%EJ.map_tab[issueid_list[i]])
            except:
                print('CLOSE %s failed.'%EJ.map_tab[issueid_list[i]])
        elif issue_list[i]['status'] == 'Reopened' and issue.fields.status.name == 'Resolved':
            try:
                jira.transition_issue(EJ.map_tab[issueid_list[i]], transition='3')
                print('The Jira %s is REOPENED' % EJ.map_tab[issueid_list[i]])
            except:
                print('REOPEN %s failed.' % EJ.map_tab[issueid_list[i]])
        #issue.update(assignee={'name': 'SESA504595'})

# issueid_list = [965]
# issue_list = [{'summary': 'JE0965-Test ===================================Test', 'description': 'Test ===================================Test\r\nBen', 'customfield_10679': '4', 'customfield_10680': '1', 'customfield_10681': '10', 'priority': '3 - Functionality', 'status': 'Closed', 'versions': 'SP02', 'fixVersions': '123'}]
#=========================================将需要同步的field在此处修改 step 4 对应 step1
def create_issues(issue_list):
    '''
    批量创建Jira
    issue_list: from ZL interface ZL 中新建issue 列表[{fields},{issue_dict}....]
    issue_dict: 部分fields 值从 issue list（其数据结构在 ZL.py get_issue_fields_list函数中定义）获取
                其他部分取默认值（按实际需求）
    '''
    issue_l = []
    if issue_list:
        for i in range(len(issue_list)):
            issue_l.append(copy.deepcopy(C.issue_dict))
            issue_l[i]['summary'] = issue_list[i]['summary']
            issue_l[i]['description'] = issue_list[i]['description']
            issue_l[i]['priority']['name'] = issue_list[i]['priority']
            # issue_l[i]['components'][0]['name'] = issue_list[i]['components']
            # issue_l[i]['assignee']['name'] = issue_list[i]['assignee']
            if issue_list[i]['customfield_10679']:
                issue_l[i]['customfield_10679'] = int(issue_list[i]['customfield_10679'])
            else:
                issue_l[i]['customfield_10679'] = None
            if issue_list[i]['customfield_10680']:
                issue_l[i]['customfield_10680'] = int(issue_list[i]['customfield_10680'])
            else:
                issue_l[i]['customfield_10680'] = None
            if issue_list[i]['customfield_10681']:
                issue_l[i]['customfield_10681'] = int(issue_list[i]['customfield_10681'])
            else:
                issue_l[i]['customfield_10681'] = None
            if issue_list[i]['versions'] in C.Jedi_Version:
                issue_l[i]['versions'][0]['name'] = issue_list[i]['versions']
            else:
                issue_l[i]['versions'][0]['name'] = 'EP1.1'
        #print(jira.create_issues(issue_l))
        return jira.create_issues(issue_l)

def update_comments(comment_d):
    '''
    函数接受到来自ZL interface 的参数 comment_d (dict)
    ex.{888: [('2021-05-07 11:14:32', '八戒', '测试评论1620357270'),
              ('2021-05-07 11:13:45', '八戒', '测试评论1620357223'),
              ('2021-05-07 11:07:04', '八戒', '测试评论1620356822'),
              ('2021-05-07 08:26:57', 'Andy', 'Just test for 3')],
        966: [('2021-05-07 10:53:26', '悟空', '测试评论1620356006')]}
    查表得到jira id
    更新Jira 上的comments
    '''
    update_list = []
    if len(comment_d):
        for key, value in comment_d.items():
            issue = jira.issue(EJ.map_tab[key])
            jira.add_comment(issue,str(value))
            update_list.append(EJ.map_tab[key])
        print(update_list,' comments has been updated')
    else:
        print('No any new comment')

def update_attachment(id,jpgname):
    # fun_name = sys._getframe().f_code.co_name
    # print(fun_name)
    issue = jira.issue(EJ.map_tab[int(id)])
    jira.add_attachment(issue=issue, attachment=jpgname)
    print("upload attachments %s to %s"%(jpgname, EJ.map_tab[int(id)]))

def update_attachments(idlist,filenamelist):
    '''
    检查ZL 系统中attachments 是否有更新，根据PicNumCheck 中记录的文件数量和类型
    :param idlist: ZL id list[id1,id2,...]
    :param filenamelist: [[id1],[id2],...]
    :return:
    '''
    for i in range(len(idlist)):
        if idlist[i] in P.pics_check.keys():
            #判读图片数量,从当前文件夹读取以id 开头的文件 如果数目相等，不更新，数目增加，上传附件，更新记录
            jpglist = filenamelist[i]
            num_info = C.get_pic_number(idlist[i], jpglist)
            if P.pics_check[idlist[i]][0] != num_info[1]:      #attachments pic
                for k in range(num_info[1] - P.pics_check[idlist[i]][0]):
                    update_attachment(idlist[i],jpglist[P.pics_check[idlist[i]][0]+k])
                print('Add attechment picture to %s .'%EJ.map_tab[idlist[i]])
            else:
                print('%s No need upload attachment picture.'%EJ.map_tab[idlist[i]])
            if P.pics_check[idlist[i]][1] != num_info[2]:    #improvement pic
                for k in range(num_info[2] - P.pics_check[idlist[i]][1]):
                    update_attachment(idlist[i], jpglist[-k-1])
                    print('Add improvement picture to %s .' % EJ.map_tab[idlist[i]])
            else:
                print('%s No need upload improvement picture.' % EJ.map_tab[idlist[i]])
            if P.pics_check[idlist[i]][1] != num_info[2] or P.pics_check[idlist[i]][0] != num_info[1]:
                C.add_map_log(idlist[i], tuple((num_info[1], num_info[2])), 'PicNumCheck.py')
        else:
            #查表没有发现记录，直接上传附件，并添加记录
            jpglist = filenamelist[i]
            num_info = C.get_pic_number(idlist[i], jpglist)
            for j in range(num_info[1] + num_info[2]):
                update_attachment(idlist[i], jpglist[j])
            print('Add %s picture to %s.'%(str(num_info[1] + num_info[2]), EJ.map_tab[idlist[i]]))
            C.add_map_log(idlist[i], tuple((num_info[1], num_info[2])), 'PicNumCheck.py')


#------------------------------------------------these functions are for Jira write information back to ZL
def issues_updated():
    '''
    查询自从上次同步（Jira — ZL）以来，Jira 上的更新 返回issue list
    :return: list[jiar-id] ex.[<JIRA Issue: key='JEDI-1083', id='367565'>, <JIRA Issue: key='JEDI-1082', id='367553'>, <JIRA Issue: key='JEDI-668', id='360657'>]
    '''
    updatetime = C.get_last_sync_time(-1)
    # print(updatetime,'is Last sync time.')
    mins = int((time.time() - int(updatetime))/60)
    JQL = "project='Jedi 3 Phase' AND type = Defect AND updated > -%sm" % mins
    # print(JQL)
    list1 = []
    list = jira.search_issues(JQL)
    num = len(list)
    if list:
        for i in list:
            if str(i) in EJ.map_tab.values():
                list1.append(str(i))
    return list1

#=========================================将需要同步的field在此处修改 step 5
def get_jira_updatedfield(key):
    '''
    :args: jira-id
    :return:dict[fields]
    '''
    issue = jira.issue(key)
    fields = issue.__dict__
    # if fields['raw']['fields']['resolution']:
    #     resolution = fields['raw']['fields']['resolution']['name']
    # else:
    #     resolution = None
    # if fields['raw']['fields']['assignee']:
    #     assignee = fields['raw']['fields']['assignee']['name']
    # else:
    #     assignee = None
    # if fields['raw']['fields']['components']:
    #     components = fields['raw']['fields']['components'][0]['name']
    # else:
    #     components = []
    if fields['raw']['fields']['fixVersions']:
        fixVersions = fields['raw']['fields']['fixVersions'][0]['name'],
    else:
        fixVersions = None
    return {'S': fields['raw']['fields']['customfield_10679'],
            'O': fields['raw']['fields']['customfield_10680'],
            'D': fields['raw']['fields']['customfield_10681'],
            # 'assignee': assignee,
            'fixVersions': fixVersions,
            # 'labels': fields['raw']['fields']['labels'],
            # 'components': components,                #如果包含多个组件的情况？
            'description': fields['raw']['fields']['description'],
            'priority': fields['raw']['fields']['priority']['name'],
            'status': fields['raw']['fields']['status']['name'],
            # 'resolution': resolution,
            'versions': fields['raw']['fields']['versions'][0]['name'],
            # 'issuetype': fields['raw']['fields']['issuetype']['name'],
            }

def get_jira_updatedcomments(key):
    '''
    :arg: jira-id
    :return: list[comments]
    '''
    issue = jira.issue(key)
    fields = issue.__dict__
    total = fields['raw']['fields']['comment']['total']
    updatetime = C.get_last_sync_time(-2)
    print(updatetime,' is last sync time.')
    comments = []
    for i in range(total):
        updated = fields['raw']['fields']['comment']['comments'][i]['updated']
        if updated[10] == 'T':
            updated = updated[:10] + ' ' + str(int(updated[11:13]) + 12) + updated[13:19]
        else:
            updated = updated[:10]+ ' '+updated[11:19]
        name = fields['raw']['fields']['comment']['comments'][i]['updateAuthor']['displayName']
        id = fields['raw']['fields']['comment']['comments'][i]['id']
        content = fields['raw']['fields']['comment']['comments'][i]['body']
        print(updated,'is the comment update time ', key)
        # print(updatetime)
        if updated >= updatetime:
            comments.append((updated,name,content,id))
    if comments:
        comments.append(key)
    return comments

def get_jira_updateattachment(key):
    '''
    only get image type attachment from jira by key
    :param key:Jira-id
    :return:list[attachment_name]
    '''
    issue = jira.issue(key)
    fields = issue.__dict__
    total = len(fields['raw']['fields']['attachment'])
    updatetime = C.get_last_sync_time(-2)
    attachments = []
    for i in range(total):
        filename = fields['raw']['fields']['attachment'][i]["filename"]
        createtime = fields['raw']['fields']['attachment'][i]["created"]
        if createtime[10] == 'T':
            createtime = createtime[:10] + ' ' + str(int(createtime[11:13]) + 12) + createtime[13:19]
        else:
            createtime = createtime[:10] + ' ' + createtime[11:19]
        mimeType = fields['raw']['fields']['attachment'][i]["mimeType"]
        id = fields['raw']['fields']['attachment'][i]['id']
        if (createtime >= updatetime) & (mimeType == 'image/jpeg'):
            attachments.append(filename)
            attachment = jira.attachment(id)
            image = attachment.get()
            with open(filename, 'wb') as f:
                f.write(image)
    return attachments

