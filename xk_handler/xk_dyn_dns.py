#!/usr/bin/python
#-*- coding:utf8 -*-
# Desgin By Xiaok
from xk_application.xk_main import *

class DynHandler(BaseHandler):
    def get(self,*args):
        #print args # 传入了一个login的参数进来了
        self.post(self,*args);

    def post(self,*args):
        username = self.get_argument('username')
        password = self.get_argument('password')
        
        domain = self.get_argument('domain')
        record = self.get_argument('record')
        typename = self.get_argument('typename')

        user = self.db.get('''select id,username,status from xk_users where username = %s and password = md5(%s)''',username,password)
        if user:
            if user['status'] == 'no':
                self.write('''用户已禁用, 请联系管理员！''')
                return
        else:
            self.write('''用户名或密码错误！''')
            return
        # 获取客户端信息,并写入登录日志
        headers = self.request.headers
        login_host = self.request.remote_ip
        #login_host = "210.75.225.254" # For Test and Debug
        user_agent = headers.get('User-Agent')
        # 写登录日志
        self.db.execute(''' insert into xk_login_logs (uid,username,login_host,user_agent) values (%s,%s,%s,%s) ''',user['id'],user['username'],login_host,user_agent)
        
        #domain is exit
        _domain = self.db.get("select id,domain from xk_domain where status = 'yes' and domain = %s", domain)
        if _domain:
            _record = self.db.get("select id,value,did from xk_record where record = %s and type = %s and did=%s", record,typename,_domain['id'])
            if _record:
                #record exist,check ip,if change, then update and restrat dns server
                if _record['value'] == login_host:
                    
                    return
                else:
                    self.db.execute(''' update xk_record set value=%s where id=%s  and did=%s ''',login_host,_record['id'],_domain['id'])
                    self.redirect("/public/api?module=dnsmasq&fun=update&id="+str(_record['did'])+"&force=yes")
                    
                    return
                
            else:
                #record not exist,insert and restart dns server
                did = _domain['id']
                record = self.get_argument("record")
                type = self.get_argument("typename")
                value = login_host
                priority = self.get_argument("priority",0)
                comment = "auto create dns"
                
                if type == "MX":
                    priority = int(priority)
                else:
                    priority = None
                
                self.db.execute("insert into xk_record (did,record,type,value,priority,comment,create_time) values (%s,%s,%s,%s,%s,%s,%s)",did,record,type,value,priority,comment,self.get_time())
                #self.write("1")
                self.redirect("/public/api?module=dnsmasq&fun=update&id="+str(did)+"&force=no")
                return  
        else:
            self.write("domain  ["+domain+"] is not exist")
            return
        
        
        
