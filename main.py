# -*- coding: utf-8 -*-
"""
@Time ： 2021/3/21 12:01
@Auth ： Icrons
@IDE ：PyCharm
//魔改版 by George_Li
//修改内容：增加多网站登录，多用户登录，改为github workflow定时执行
//使用方法：创建secrets 名字：MYKEY 内容的写法：
//机场的名字(方便自己看)|机场的网址(https:www.xxxx...)|第一个邮箱(用户名),密码;第二个邮箱,密码;...
//每两个机场用回车键隔开
//例如: 某某云|https://www.yun.com|jjjj@qq.com,password

"""
import requests
import os
import re
import json

requests.urllib3.disable_warnings()

#初始化环境变量开头
datas = os.environ["mykey"]
SKey = os.environ["serverkey"]
QKey = os.environ["qmsgkey"]
telekey = os.environ["telekey"]
ttoken = ""
tuserid = ""
if(telekey != ''):
  telekeys = telekey.split('\n')
  ttoken = telekeys[0]
  tuserid = telekeys[1]
if(datas == ''):
  print('您没有输入任何信息')
  exit
groups = datas.split('\n')
#初始化环境变量结尾

class SspanelQd(object):
    def __init__(self,name,site,username,psw):
        ###############登录信息配置区###############
        #机场的名字
        self.name = name
        #签到流量
        self.flow = 0
        # 机场地址
        self.base_url = site
        # 登录信息
        self.email = username
        self.password = psw
        ###########################################
        ##############推送渠道配置区###############
        # 酷推qq推送
        self.ktkey = ''
        # ServerTurbo推送
        self.SendKey = SKey
        # Qmsg私聊推送
        self.QmsgKey = QKey
        # Telegram私聊推送
        self.tele_api_url = 'https://api.telegram.org'
        self.tele_bot_token = ttoken
        self.tele_user_id = tuserid
        # Pushplus私聊推送
        self.push_token = ''
        ##########################################

    def checkin(self):
        email = self.email.split('@')
        email = email[0] + '%40' + email[1]
        password = self.password
        try:
            session = requests.session()
            session.get(self.base_url, verify=False)

            login_url = self.base_url + '/auth/login'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }

            post_data = 'email=' + email + '&passwd=' + password + '&code='
            post_data = post_data.encode()
            session.post(login_url, post_data, headers=headers, verify=False)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                'Referer': self.base_url + '/user'
            }

            response = session.post(self.base_url + '/user/checkin', headers=headers, verify=False)
            # print(response.text)
            msg = (response.json()).get('msg')
            print(msg)
        except:
            return False

        info_url = self.base_url + '/user'
        response = session.get(info_url, verify=False)
        """
        以下只适配了editXY主题
        """
        try:
            level = re.findall(r'\["Class", "(.*?)"],', response.text)[0]
            day = re.findall(r'\["Class_Expire", "(.*)"],', response.text)[0]
            rest = re.findall(r'\["Unused_Traffic", "(.*?)"]', response.text)[0]
            msg = "- 今日签到信息：" + str(msg) + "\n- 用户等级：" + str(level) + "\n- 到期时间：" + str(day) + "\n- 剩余流量：" + str(rest)
            print(msg)
            return msg
        except:
            return msg
    def getflow(self , msg):
      pattern = re.compile('获得了(.+)MB')
      if(msg == ""):
        return 0
      num = pattern.findall(msg)
      if num == []:
        return 0
      else:
        return num[0]
    
    # Qmsg私聊推送
    def Qmsg_send(self, msg):
        if self.QmsgKey == '':
            return
        qmsg_url = 'https://qmsg.zendee.cn/send/' + str(self.QmsgKey)
        data = {
            'msg': msg,
        }
        requests.post(qmsg_url, data=data)

    # Server酱推送
    def server_send(self, msg):
        if self.SendKey == '':
            return
        server_url = "https://sc.ftqq.com/" + str(self.SendKey) + ".send"
        data = {
            'text': self.name + "签到通知",
            'desp': msg
        }
        requests.post(server_url, data=data)

    # 酷推QQ推送
    def kt_send(self, msg):
        if self.ktkey == '':
            return
        kt_url = 'https://push.xuthus.cc/send/' + str(self.ktkey)
        data = ('签到完成，点击查看详细信息~\n' + str(msg)).encode("utf-8")
        requests.post(kt_url, data=data)
    #Telegram私聊推送
    def tele_send(self, msg: str):
        if self.tele_bot_token == '':
            return
        tele_url = f"{self.tele_api_url}/bot{self.tele_bot_token}/sendMessage"
        data = {
            'chat_id': self.tele_user_id,
            'parse_mode': "Markdown",
            'text': msg
        }
        requests.post(tele_url, data=data)
        
    # Pushplus推送
    def pushplus_send(self,msg):
        if self.push_token == '':
            return
        token = self.push_token 
        title= '机场签到通知'
        content = msg
        url = 'http://www.pushplus.plus/send'
        data = {
            "token":token,
            "title":title,
            "content":content
            }
        body=json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type':'application/json'}
        requests.post(url,data=body,headers=headers)


    def main(self):
        msg = self.checkin()
        if msg == False:
            print("网址不正确或网站禁止访问。")
            msg = self.name + "签到失败"
            self.server_send(msg)
            self.kt_send(msg)
            self.Qmsg_send(msg)
            self.tele_send(self.email+"\n"+msg)
            self.pushplus_send(msg)
        else:
            self.server_send(msg)
            self.kt_send(msg)
            self.Qmsg_send(self.name+"\n"+self.email+"\n"+msg)
            self.tele_send(self.name+"\n"+self.email+"\n"+msg)
            self.pushplus_send(msg)

i = 0
while i < len(groups):
  group = groups[i]
  i += 1
  prop = group.split('|')
  site_name = prop[0]
  web_site = prop[1]
  prof = prop[2]
  profiles = prof.split(';')
  j = 0
  while j < len(profiles):
    profile = profiles[j]
    profile = profile.split(',')
    username = profile[0]
    pswd = profile[1]
    print(site_name)
    print(web_site)
    print(username)
    print(pswd)
    
    run = SspanelQd(site_name, web_site ,username ,pswd)
    run.main()
    j += 1
