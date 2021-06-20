import ZL
import Jira
import EJmap,PicNumCheck
import os

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


if __name__ == "__main__":
    idlist = ZL.get_new_update_list()       #获取自上次sync后，新的更新列表（包含新建）
    # print(idlist)
    idlist_update = []
    idlist_new = []
    for i in range(len(idlist)):        #通过查表，将上述列表分为更新问题列表和新建问题列表
        if idlist[i] in EJmap.map_tab.keys():
            idlist_update.append(idlist[i])
        else:
            idlist_new.append(idlist[i])
    # print(idlist_new)
    # print(idlist_update)
    if idlist_new != []:        #根据新建问题列表在Jira 新建jira
        new_issue_list = ZL.get_issue_fields_list(idlist_new)
        # ZL.sync_time()
        new_issues = Jira.create_issues(new_issue_list)
        for i in range(len(idlist_new)):
            # print(idlist_new[i])
            # print(new_issues[i])
            EJmap.add_map_log(idlist_new[i],new_issues[i]['issue'].key)
            print('Add new Jira ',new_issues[i]['issue'].key)
    else:
        print("No new issue.")

    if idlist_update != []:     #根据更新问题列表，在jira同步数据
        only_update_list = ZL.get_issue_fields_list(idlist_update)
        Jira.update_issue(idlist_update,only_update_list)
        for i in range(len(idlist_update)):
            print('Update Jira fields ',EJmap.map_tab[idlist_update[i]])
    else:
        print("No fields update.")
#同步comments
    ZL_comments = ZL.get_ZL_comments()
    Jira.update_comments(ZL_comments)
#同步图片
    idlist_update = []
    idlist_new = []
    # idlist = [990, 989]
    for i in range(len(idlist)):
        print(idlist[i])
        print("Need to wait a bit for downloading attachments... ")
        ret = ZL.get_picture_by_id(idlist[i])
        if isinstance(ret,int):
            # idlist.remove(idlist[i])
            pass
        else:
            if idlist[i] in PicNumCheck.pics_check.keys():
                #判读图片数量,从当前文件夹读取以id 开头的文件 如果数目相等，不更新，数目增加，上传附件，更新记录
                jpg = all_pictures()
                info = get_pic_number(idlist[i], jpg)
                if PicNumCheck.pics_check[idlist[i]][0] != info[1]:
                    for k in range(info[1] - PicNumCheck.pics_check[idlist[i]][0]):
                        Jira.update_attachment(idlist[i],info[0][PicNumCheck.pics_check[idlist[i]][0]+k])
                    print('Add attechment picture.')
                else:
                    print('No need upload attachment picture.')
                if PicNumCheck.pics_check[idlist[i]][1] != info[2]:
                    for k in range(info[2] - PicNumCheck.pics_check[idlist[i]][1]):
                        Jira.update_attachment(idlist[i], info[0][-k-1])
                    print('Add improvement picture.')
                else:
                    print('No need upload improvement picture.')
                if PicNumCheck.pics_check[idlist[i]][1] != info[2] or PicNumCheck.pics_check[idlist[i]][0] != info[1]:
                    EJmap.add_map_log(idlist[i], tuple((info[1], info[2])), 'PicNumCheck.py')
            else:
                #查表没有发现记录，直接上传附件，并添加记录
                jpg = all_pictures()
                info = get_pic_number(idlist[i], jpg)
                # print(idlist[i])
                # print(info[0])
                for j in range(info[1]+info[2]):
                    Jira.update_attachment(idlist[i], info[0][j])
                print('Add %s picture.'%str(info[1]+info[2]))
                EJmap.add_map_log(idlist[i], tuple((info[1],info[2])), 'PicNumCheck.py')
    #remove all jpg
    jpg = all_pictures()
    if jpg:
        for i in range(len(jpg)):
            os.remove(jpg[i])
    ZL.sync_time()              # 记录本次操作时间戳







    #









#     idlist_update = []
#     idlist_new = []
#     for i in range(len(idlist)):        #通过查表，将上述列表分为更新问题列表和新建问题列表
#         if idlist[i] in EJmap.map_tab.keys():
#             idlist_update.append(idlist[i])
#         else:
#             idlist_new.append(idlist[i])
#     # print(idlist_new)
#     # print(idlist_update)
#     if idlist_new != []:        #根据新建问题列表在Jira 新建jira
#         new_issue_list = ZL.get_issue_fields_list(idlist_new)
#         # ZL.sync_time()
#         new_issues = Jira.create_issues(new_issue_list)
#         for i in range(len(idlist_new)):
#             # print(idlist_new[i])
#             # print(new_issues[i])
#             EJmap.add_map_log(idlist_new[i],new_issues[i]['issue'].key)
#             print('Add new Jira ',new_issues[i]['issue'].key)
#     else:
#         print("No new issue.")
#
#     if idlist_update != []:     #根据更新问题列表，在jira同步数据
#         only_update_list = ZL.get_issue_fields_list(idlist_update)
#         Jira.update_issue(idlist_update,only_update_list)
#         for i in range(len(idlist_update)):
#             print('Update Jira fields ',EJmap.map_tab[idlist_update[i]])
#     else:
#         print("No fields update.")
# #同步comments
#     ZL_comments = ZL.get_ZL_comments()
#     Jira.update_comments(ZL_comments)
# #同步图片
#     idlist_update = []
#     idlist_new = []
#     # idlist = [990, 989]
#     for i in range(len(idlist)):
#         print(idlist[i])
#         print("Need to wait a bit for downloading attachments... ")
#         ret = ZL.get_picture_by_id(idlist[i])
#         if isinstance(ret,int):
#             # idlist.remove(idlist[i])
#             pass
#         else:
#             if idlist[i] in PicNumCheck.pics_check.keys():
#                 #判读图片数量,从当前文件夹读取以id 开头的文件 如果数目相等，不更新，数目增加，上传附件，更新记录
#                 jpg = all_pictures()
#                 info = get_pic_number(idlist[i], jpg)
#                 if PicNumCheck.pics_check[idlist[i]][0] != info[1]:
#                     for k in range(info[1] - PicNumCheck.pics_check[idlist[i]][0]):
#                         Jira.update_attachment(idlist[i],info[0][PicNumCheck.pics_check[idlist[i]][0]+k])
#                     print('Add attechment picture.')
#                 else:
#                     print('No need upload attachment picture.')
#                 if PicNumCheck.pics_check[idlist[i]][1] != info[2]:
#                     for k in range(info[2] - PicNumCheck.pics_check[idlist[i]][1]):
#                         Jira.update_attachment(idlist[i], info[0][-k-1])
#                     print('Add improvement picture.')
#                 else:
#                     print('No need upload improvement picture.')
#                 if PicNumCheck.pics_check[idlist[i]][1] != info[2] or PicNumCheck.pics_check[idlist[i]][0] != info[1]:
#                     EJmap.add_map_log(idlist[i], tuple((info[1], info[2])), 'PicNumCheck.py')
#             else:
#                 #查表没有发现记录，直接上传附件，并添加记录
#                 jpg = all_pictures()
#                 info = get_pic_number(idlist[i], jpg)
#                 # print(idlist[i])
#                 # print(info[0])
#                 for j in range(info[1]+info[2]):
#                     Jira.update_attachment(idlist[i], info[0][j])
#                 print('Add %s picture.'%str(info[1]+info[2]))
#                 EJmap.add_map_log(idlist[i], tuple((info[1],info[2])), 'PicNumCheck.py')
#     #remove all jpg
#     jpg = all_pictures()
#     if jpg:
#         for i in range(len(jpg)):
#             os.remove(jpg[i])
#     ZL.sync_time()              # 记录本次操作时间戳