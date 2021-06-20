实现智联与Jira系统的自动关联
功能列表：
1.将ZL系统的issue，相应的创建Jira系统上
2.将ZL系统上的更新，以定时或人为触发的方式同步在Jira系统上更新
    2.1 同步fields    eg. Serverity,Occurence，Detection，title(ZL id + summary), Description, Affects Versions, Priority
    2.2 同步comments  一定时间内的评论打包一起同步
    2.3 同步attachment 下载后重新命名
3.记录智联和Jira系统关联问题的映射
4.记录attachment 分问题描述附件和改进措施附件数目的变化
5.记录每次同步是时间节点
6.屏幕提示信息。   同步进度及那些更新项目对应的Jira No.

注意事项：
1.不可并行操作，会重复创建新的issue，
2.本地log文件，不要改动，丢失记录，会导致重复创建issue及覆盖最新的信息。
3.同步冲突问题 如下
    ZL Z issue 关联 Jira J issue
    Z issue 有更新
    J issue 也有更新
    如何同步？先执行Z-J 同步？还是先执行J-Z同步（覆盖操作？ 先保留备份，再覆盖？）
4.导致程序出错的风险有：
    ZL 安全检查机制 （秘钥方式，HTTPS）
    ZL 接口变化问题
    ZL 关键字变化 （improvepics-> improve_pics）
    ZL 返回值变化（NULL null ‘’）
    ZL 中S O 必须填写正确的数值


建议管理员权限操作及Git管理工程文件

未完成事项：
1.将Jira中的相关更新回写到智联上的关联
    1.1 未确立冲突解决原则
    1.2 ZL 为准备好接口
        1.2.1 field
        1.2.2 comments
        1.2.3 attachment 智联附件仅支持jpg图片格式，不支持zip包
2.Jira 建立公共账号
3.项目后期扩展维护
    3.1 宏开关 - 调试信息
    3.2 全局变量 - 项目迁移
    3.3 comments 显示优化

    3.4 issue 状态同步
    3.5 assignee 和 模块，label 映射
    3.6 S O D 在ZL中是枚举值，如果回写的 不是{null，1,4,7,10}则保持不变


更新status
更新assignee
