import ZL
import Jira
import EJmap as EJ
import common as C
import os

if __name__ == "__main__":

    # 获取自上次同步以来，ZL 和 Jira上产生的更新
    keylist = Jira.issues_updated()
    print('All jira update [keylist]: %s'%keylist)
    idlist = ZL.get_new_update_list()       #获取自上次sync后，新的更新列表（包含新建）
    print('All ZL update [idlist]: %s'%idlist)


    #ZL 上的idlist 要区分成两类 1. new issue 2. update issue
    idlist_n = []
    idlist_u = []
    if idlist:
        for i in range(len(idlist)):
            if idlist[i] in EJ.map_tab:
                idlist_u.append(idlist[i])
            else:
                idlist_n.append(idlist[i])
    # print(idlist_n)
    # print(idlist_u)
    # Create Jira from idlist_n

    # 找出三类数据 1. ZL update only 2.jira update only 3. both ZL and Jira update
    set_Z = []
    set_J = []
    if idlist:
        for i in range(len(idlist_u)):
            set_Z.append(EJ.map_tab[idlist_u[i]])
    # print(set_Z)
    if keylist:
        for i in range(len(keylist)):
            set_J.append(keylist[i])
    # print(set_J)
    set_Z = set(set_Z)
    set_J = set(set_J)
    both = set_Z & set_J
    only_Z = list(set_Z - both)
    only_J = list(set_J - both)
    both = list(both)
    #convert only_z to ZL id list by EJmap
    new_dict = {v: k for k, v in EJ.map_tab.items()}
    only_z = []
    if only_Z:
        for i in range(len(only_Z)):
            only_z.append(new_dict[only_Z[i]])
    both4z = []
    if both:
        for i in range(len(both)):
            both4z.append(new_dict[both[i]])
    print('[both][both4z] update Jira No. is both %s ZL No. is both4z %s'%(both,both4z))
    print('[only_z] [idlist_n] ZL update only_z %s New issue ZL idlist_n %s'%(only_z,idlist_n))
    print('[only_J] Jira update only_J %s'%only_J)

    '''
    Get all ZL data by idlist
    Get all Jira data by keylist
    '''
    Z_fields = ZL.get_issue_fields_list(idlist)
    Z_comments = ZL.get_ZL_comments()
    Z_atName = []
    if idlist:
        for i in range(len(idlist)):
            Z_atName.append(ZL.get_picture_by_id(idlist[i]))
    print("==============================ZZZZZZZZZZZZZZZZZZZLLLLLLLLLLLLLLLLLLLLLL=====================================")
    print("ZL_fields: ",Z_fields)
    print("ZL_comments: ",Z_comments)
    print("ZL_atName: ",Z_atName)

    J_fields = []
    J_comments = []
    J_atName = []
    if keylist:
        for i in range(len(keylist)):
            J_fields.append(Jira.get_jira_updatedfield(keylist[i]))
            J_comments.append(Jira.get_jira_updatedcomments(keylist[i]))
            J_atName.append(Jira.get_jira_updateattachment(keylist[i]))
    print("===============================JJJJJJJJJJJJJJJJJJJJJJJRRRRRRRRRRRRRRR=======================================")
    print("Jira_fields: ",J_fields)
    print("Jira_comments: ",J_comments)
    print("Jira_atName: ",J_atName)

    # '''
    # Create new jira by idlist_n add data to EJmap
    # '''
    new_Jissues = Jira.create_issues(ZL.get_issue_fields_list(idlist_n))
    if new_Jissues:
        for i in range(len(idlist_n)):
            C.add_map_log(idlist_n[i],new_Jissues[i]['issue'].key)
            EJ.map_tab[idlist_n[i]] = new_Jissues[i]['issue'].key
            print('Add new Jira to map',new_Jissues[i]['issue'].key)

    '''
    Sync ZL fields to Jira by only_Z
    Sync all ZL comments to Jira
    Sync all attachments to Jira via PicNumCheck find new attachments
        update new data to  PicNumCheck
    '''
    only_Z_fields = []
    for i in range(len(only_z)):
        for j in range(len(idlist)):
            if only_z[i] == idlist[j]:
                only_Z_fields.append(Z_fields[j])
                break
    Jira.update_issue(only_z, only_Z_fields)
    Jira.update_comments(Z_comments)
    Jira.update_attachments(idlist, Z_atName)

    '''
    Sync all comments to ZL by keylist
    Sync all fields and attachment by keylist
        update picNumCheck
    '''
    for i in range(len(J_comments)):
        ZL.add_comments(J_comments[i])
    J_id = []
    if keylist:
        for i in range(len(keylist)):
            J_id.append(new_dict[keylist[i]])
    for i in range(len(J_id)):
        ZL.writeback_fields(J_id[i], J_fields[i], J_atName[i])

    #clear up remove all jpg
    jpg = C.all_pictures()
    if jpg:
        for i in range(len(jpg)):
            os.remove(jpg[i])

    # log the sync time to sync_time.txt
    C.sync_time()
