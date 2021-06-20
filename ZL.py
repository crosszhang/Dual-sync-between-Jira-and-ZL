#coding:utf-8
import hashlib
import time
import json
import base64
from urllib.parse import quote
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PicNumCheck as P
import EJmap as EJ
import common as C

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#私钥
#PrivateKey = 'af63d161c7d4450b9ae5363e3b5abb52'
PrivateKey = '95c2e7bb8c6841d49faaed285dfeffe9'   # for JEDIHMI

mn = 'JEDIHMI'
mid = '3823'
adminuserid = 3864

#proxy
proxies = {
#    "https": "http://wf1-ch.pac.schneider-electric.com:80",
    "https": "force-proxy-birst.pac.schneider-electric.com:80",
    "https": "101.231.121.17:80"
}

Host = 'https://www.llmes.com'
Url1 = Host + '/sqbd/api/console/issue/querychangelist'
Url2 = Host + '/sqbd/api/console/issue/querylist'
Url3 = Host + '/sqbd/api/console/issue/getimage'
Url4 = Host + ''
Url5 = Host + '/sqbd/api/console/issue/querycommentslist'
Url6 = Host + '/sqbd/api/console/issue/savecomment'
Url7 = Host + '/sqbd/api/console/issue/saveissue'

class LileiTool:

    def formatBizQueryParaMap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
          v = quote(paraMap[k]) if urlencode else paraMap[k]
          buff.append("{0}={1}".format(k, v))
        return "&".join(buff)

    def getSign(self, obj):
        """生成签名"""
        #签名步骤一：按字典序排序参数,formatBizQueryParaMap已做
        String = self.formatBizQueryParaMap(obj, False)
        #签名步骤二：在string后加入KEY
        String = "{0}&{1}".format(String,PrivateKey)
        #签名步骤三：MD5加密
        String = hashlib.md5(String.encode("utf-8")).hexdigest()
        #签名步骤四：所有字符转为大写
        result_ = String.upper()
        return result_

    def doPost(self, url,paraMap):
        response = requests.post(url,data=paraMap,headers={'Content-Type':'application/x-www-form-urlencoded'}, verify=False, proxies=proxies)
        # response = requests.post(url,data=paraMap,headers={'Content-Type':'application/x-www-form-urlencoded'}, verify=False)
        # print('****************************************************\n')
        # print(response.text)
        # print('****************************************************\n')
        return response

    # def doPostFile(self, url,paraMap, files):
    #     response = requests.post(url,data=paraMap,files=files ,headers={'Content-Type':'application/x-www-form-urlencoded'},verify=False, proxies=proxies)
    #     print('****************************************************\n')
    #     print(response.text)
    #     print('****************************************************\n')
    #     return response

def get_issues():
    '''
    获取JEDIHMI项目中所有issue id list[json object]
    '''
    timeStamp = int(time.time())
    paraMap = {'timestamp': timeStamp, 'mn': mn, 'mid': mid, 'page':1, 'rows':50}
    lileiTool = LileiTool()
    sign = lileiTool.getSign(paraMap)
    paraMap['sign'] = sign
    return lileiTool.doPost(Url1, paraMap)

def get_new_update_list():
    '''
    检查从上次同步以后，更新的issue id 列表 return 例如[888,886,948]
    '''
    update_l = []
    lst_sync_time = C.get_last_sync_time()
    all_issue_s = get_issues().text
    all_issue_d = json.loads(all_issue_s)
    # print(all_issue_d['rows'])
    for ie in range(len(all_issue_d['rows'])):
        if all_issue_d['rows'][ie]['updatetime'] > int(lst_sync_time):
            update_l.append(all_issue_d['rows'][ie]['id'])
    if not update_l:
        print("No any new update in ZL.")
    return update_l

def get_issue_fields(id):
    '''
    获取给定issue id (ex.888) 的所有field,return具体描述（json object）
    '''
    timeStamp = int(time.time())
    paraMap = {'timestamp': timeStamp, 'mn': mn, 'mid': mid, 'page':1, 'rows':50, 'idlist': id,}
    lileiTool = LileiTool()
    sign = lileiTool.getSign(paraMap)
    paraMap['sign'] = sign
    return lileiTool.doPost(Url2, paraMap)

#=========================================将需要同步的field在此处修改 step 1
def get_issue_fields_list(idlist):
    '''
    给定的(需要更新的)id列表中每个id 需要更新的fields的数据填充
    此处可根据具体需求扩展
    idlist eg.[888,886,948]
    '''
    issues_l = []
    new_dict = {v: k for k, v in C.Priority_level.items()}
    new_dict1 = {v: k for k, v in C.Status_J2Z.items()}
    if len(idlist) != 0:
        for id in idlist:
            fields_t = get_issue_fields(id).text
            fields = json.loads(fields_t)
            issues_l.append({'summary':fields['rows'][0]['issuesn']+'-'+fields['rows'][0]['content'][:fields['rows'][0]['content'].find('\r\n')],
                             'description': fields['rows'][0]['content'],
                             'customfield_10679': fields['rows'][0]['S'],
                             'customfield_10680': fields['rows'][0]['O'],
                             'customfield_10681': fields['rows'][0]['D'],
                             'priority': new_dict[fields['rows'][0]['level']],
                             'status': new_dict1[fields['rows'][0]['status']],                                      #需要将reopen 和 closed 同步到jira
                             'versions': fields['rows'][0]['tag8'],                      #Affects Versions
                             'fixVersions': fields['rows'][0]['tag9'],                    #Fix Version
                             })
        return issues_l
#
# fields['rows'][0]['seriesname'] #所属系列
# fields['rows'][0]['项目阶段'] #项目阶段
# fields['rows'][0]['产品系列'] #产品系列
# fields['rows'][0]['badtypedetailname'] #问题分类
# fields['rows'][0]['codedetail'] #
# fields['rows'][0]['tag7'] #Sprint
# fields['rows'][0]['chargeusername'] # 责任人
# 'assignee': C.assignee[fields['rows'][0]['seriesname']]
# 'components': 'AS-' + fields['rows'][0]['产品型号'],
# 'issuetype': C.SeriesName_IssueType[fields['rows'][0]['seriesname']],


def get_one_picture(picP, picS, picName='1.jpg'):
    '''
    根据issue id 查找其含有的图片数量
    下载后并重新命名
    并将id 和 图片数量 关联并记录到文件中
    ex.    888:(3, 3),
    '''
    timeStamp = int(time.time())
    paraMap = {'timestamp': timeStamp, 'mn': mn, 'mid': mid, 'pic': picP, 'picsign': picS}
    lileiTool = LileiTool()
    sign = lileiTool.getSign(paraMap)
    paraMap['sign'] = sign
    res = lileiTool.doPost(Url3, paraMap)

    # base 转本地图片示例
    base64Img = json.loads(res.text).get('pics_base64')
    data = base64Img.split(',')[1]
    image_data = base64.b64decode(data)
    with open(picName, 'wb') as f:
        f.write(image_data)

def get_picture_by_id(id):
    fields_t = get_issue_fields(id).text
    fields = json.loads(fields_t)
#    print(fields)
    pic_name = []

    picP = fields['rows'][0]['pics']
    if picP:
        picS = fields['rows'][0]['pics_sign'].split(';')
        picP = picP.split(';')
        for i in range(len(picP)):
            name =  str(id)+'_'+str(i)+'.jpg'
            get_one_picture(picP[i], picS[i], name)
            pic_name.append(name)

    improve_picP = fields['rows'][0]['improvepics']
    if improve_picP:
        improve_picS = fields['rows'][0]['improvepics_sign'].split(';')
        improve_picP = improve_picP.split(';')
        for i in range(len(improve_picP)):
            name =  str(id)+'_improve_'+str(i)+'.jpg'
            get_one_picture(improve_picP[i], improve_picS[i], name)
            pic_name.append(name)

    if not pic_name:
        print(id, " no picture.")
    else:
        print("Get %s pictures from %s"%(len(pic_name),id))
    return pic_name

def get_ZL_comments():
    '''
    获取新添加的评论
    自上次sync操作，如果有新的comments，将其提取放入字典返回
    ex.{888: [('2021-05-07 11:14:32', '八戒', '测试评论1620357270'),
              ('2021-05-07 11:13:45', '八戒', '测试评论1620357223'),
              ('2021-05-07 11:07:04', '八戒', '测试评论1620356822'),
              ('2021-05-07 08:26:57', 'Andy', 'Just test for 3')],
        966: [('2021-05-07 10:53:26', '悟空', '测试评论1620356006')]}
    '''
    timeStamp = int(time.time())
    paraMap = {'timestamp': timeStamp, 'mid': mid, 'mn': mn, 'page':1, 'rows': 30}
    lileiTool = LileiTool()
    sign = lileiTool.getSign(paraMap)
    paraMap['sign'] = sign
    comment = json.loads(lileiTool.doPost(Url5, paraMap).text)
    rows = comment['rows']
    # print(rows)
    comments_d = {}
    for i in range(len(rows)):
        if rows[i]['createtime'] > C.get_last_sync_time(-2):
            # print(rows[i]['createtime'], rows[i]['issueid'], rows[i]['createusername'], rows[i]['content'])
            if rows[i]['issueid'] in comments_d:
                comments_d[rows[i]['issueid']].append(
                    (rows[i]['createtime'], rows[i]['createusername'], rows[i]['content']))
            else:
                comments_d[rows[i]['issueid']] = [
                    (rows[i]['createtime'], rows[i]['createusername'], rows[i]['content'])]
        else:
            break
    return comments_d

#==========================================================these functions are for Jira write information back to ZL

def add_comments(list):
    '''
    add new comments to ZL
    :param list[dict]: which get form get_jira_updatedcomments(key)
    :return: no return
    '''
    if list:
        new_dict = {v:k for k,v in EJ.map_tab.items()}
        issueid = int(new_dict[list[-1]])
        for i in range(len(list)-1):
            timeStamp = int(time.time())
            commentusername = list[i][1]
            outerid = list[i][3]
            content = list[i][0] + ' -- ' + list[i][2]
            paraMap = {'issueid':issueid, 'commentusername': commentusername,'outerid':outerid,'timestamp': timeStamp, 'mid': mid, 'mn': mn,'content':content,'adminuserid':3864}
            lileiTool = LileiTool()
            sign = lileiTool.getSign(paraMap)
            paraMap['sign'] = sign
            lileiTool.doPost(Url6, paraMap)
        print('Add new comments to %s'%issueid)
    else:
        print('No new comments need write back to ZL')

#=========================================将需要同步的field在此处修改 step 2
def writeback_fields(key,dict,attachments):
    '''
    :param attachments: get from jira id, list[imagename]
    :param dict: get from jira id dict[fields]
    :param key: ZL id
    :return:
    '''
    fields_t = get_issue_fields(key).text
    fields = json.loads(fields_t)

    issueid = key

    timeStamp = int(time.time())
    mn = 'JEDIHMI'
    mid = '3823'
    adminuserid = 3864
    outerid = int(EJ.map_tab[key][5:])


    level = C.Priority_level[dict['priority']] #priority
    content = dict['description'] # description
    if dict['S']:
        S = int(dict['S'])
    else:
        S = 1
    if dict['O']:
        O = str(int(dict['O']))
    else:
        O = 1
    if dict['D']:
        D = int(dict['D'])
    else:
        D = 1
    status = C.Status_J2Z[dict['status']]
    AffectsVersion = dict['versions']
    if dict['fixVersions']:
        FixVersion = dict['fixVersions']
    else:
        FixVersion = fields['rows'][0]['tag9']

    #保持原来的值
    项目阶段 = fields['rows'][0]['项目阶段']
    产品系列 = fields['rows'][0]['产品系列']
    SOD = fields['rows'][0]['tag6']
    Sprint = fields['rows'][0]['tag7']
    seriesname = fields['rows'][0]['seriesname']
    chargeusername = fields['rows'][0]['chargeusername']
    improvemeasures = fields['rows'][0]['improvemeasures']
    badtypedetailname = fields['rows'][0]['badtypedetailname']
    codedetail = fields['rows'][0]['codedetail']
    expiredate = fields['rows'][0]['expiredate']

    paraMap = {'timestamp': timeStamp, 'outerid':outerid, 'mid': mid, 'mn': mn, 'adminuserid':adminuserid,
               '项目阶段':项目阶段, '产品系列':产品系列, 'S':S,'O':O,'D':D,'tag6':SOD, 'tag7':Sprint,
               'seriesname': seriesname, 'tag8': AffectsVersion, 'tag9': FixVersion,
               'badtypedetailname':badtypedetailname,'codedetail': codedetail, 'level': level,
               'content': content, 'chargeusername':chargeusername, 'expiredate': expiredate,'status': status,
               'improvemeasures': improvemeasures, 'issueid': issueid
    }

    lileiTool = LileiTool()
    sign = lileiTool.getSign(paraMap)
    paraMap['sign'] = sign

    if fields['rows'][0]['pics']:
        picsList = fields['rows'][0]['pics'].split(';')
    else:
        # picsList = fields['rows'][0]['pics']
        picsList = []
    if attachments:
        for i in range(len(attachments)):
            # 读取图片转base64
            imgPath = attachments[i]
            f = open(imgPath, 'rb')
            # 读取图片并转为相应的base64字符串
            base64Img = 'data:image/' + imgPath[imgPath.rfind('.') + 1:] + ';base64,' + base64.b64encode(f.read()).decode('ascii')
            picsImgs = [base64Img]
            picsList = picsList + picsImgs
    paraMap['pics'] = json.dumps( picsList)
    print(picsList)
    print(attachments)
    print(paraMap)
    print(json.loads(lileiTool.doPost(Url7, paraMap).text)['msg'])
    print('Sync fields or attachments from %s to %s'%(EJ.map_tab[key], key))
    if key in P.pics_check.keys():
        pic_num = P.pics_check[key]
        C.add_map_log(key, tuple((pic_num[0]+ len(attachments), pic_num[1])), 'PicNumCheck.py')
    else:
        C.add_map_log(key, tuple((len(attachments), 0)), 'PicNumCheck.py')


# dict1 = {'S': 4.0, 'O': 1.0, 'D': 10.0, 'fixVersions': None, 'description': 'Test ===================================Test\r\nBen', 'priority': '3 - Functionality', 'status': 'Closed', 'versions': 'SP02'}
# key = 965
# attachments = ['test2.jpg']
# writeback_fields(key, dict1, attachments)