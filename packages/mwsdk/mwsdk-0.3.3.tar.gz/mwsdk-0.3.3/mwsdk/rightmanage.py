import requests
# from consul import Consul
from collections import namedtuple
from mwutils.mw_consul import ServiceConf
import warnings
import aiohttp
User = namedtuple('User', ['uid', 'username', 'issystemuser','ismanageuser','manageuserid'])

class RightmanageError(Exception):
    pass

class RightmanageABS():
    def get_rm_sc(self):
        '''
        获取权限配置
        :return:
        '''
        if self._rm_sc is None:
            self._rm_sc = ServiceConf(self.service_name, tag=self.service_tag,near=True)
        return self._rm_sc

    def __init__(self):
        self.service_name = 'rightmanage'
        self._rm_sc = None
        self.service_tag = 'kong'
        # consul = Consul()
        # auth_conf = consul.catalog.service(self.service_name,tag='kong')[1]
        # if not auth_conf:
        #     raise Exception('The %s service is not exist!'%self.service_name)
        # self.ip = auth_conf[0]['ServiceAddress']
        # self.port = auth_conf[0]['ServicePort']
        # auth_conf = ServiceConf(self.service_name,  near=True)
        # self.ip = auth_conf.ip
        # self.port = auth_conf.port

    @property
    def ip(self):
        try:
            return self.get_rm_sc().ip
        except Exception as e:
            # 避免一個服務報錯的時候，可再使用其他服務
            self._rm_sc = None
            return self.get_rm_sc().ip

    @property
    def port(self):
        try:
            return self.get_rm_sc().port
        except Exception as e:
            # 避免一個服務報錯的時候，可再使用其他服務
            self._rm_sc = None
            return self.get_rm_sc().port

class Rightmanage(RightmanageABS):
    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/rightmanage/v1.0/cur-permissions?systemname=maxguideweb&jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    def cur_permissions(self,systemname,jwt,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        data = {'systemname':systemname,'jwt':jwt}
        try:
            resp = requests.get('http://{ip}:{port}/{service}/{version}/cur-permissions'.format(ip=self.ip,
                                port=self.port,version=version,service=self.service_name),
                          params=data,headers=headers)
            return resp.status_code, resp.json()
        except Exception as e:
            # 出现例外是服务不可用，需要重新从consul中读取配置
            self._rm_sc = None
            raise


    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/rightmanage/v1.0/cur-user?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    def cur_user(self,jwt,version='v1.0'):
        '''
        返回值是json
        {"uid": self.uid,   #user.id
        "uname": self.uname, # user.name
        "systemuser":self.systemuser, #user.issystemuser
            "manageuser":self.manageuser,
            "manageuserid":self.manageuserid}
        '''
        warnings.warn("cur_user is deprecated, "
                      "use g.current_user instead",
                      DeprecationWarning)
        headers = {'Accept': 'chatset=utf8'}
        data = {'jwt':jwt}
        try:
            resp = requests.get('http://{ip}:{port}/{service}/{version}/cur-user'.format(ip=self.ip,
                                port=self.port,version=version,service=self.service_name),
                          params=data,headers=headers)
            return resp.status_code,resp.json()
        except Exception as e:
            # 出现例外是服务不可用，需要重新从consul中读取配置
            self._rm_sc = None
            raise

    def login_user(self,jwt,version='v1.0'):
        warnings.warn("login_user is deprecated, "
                      "use g.current_user instead",
                      DeprecationWarning)
        _, user_js = self.cur_user(jwt,version)
        return User(uid=user_js['uid'],
                    username=user_js['uname'],
                    issystemuser=user_js['systemuser'],
                    ismanageuser=user_js['manageuser'],
                    manageuserid=user_js['manageuserid']
                    )

class Rightmanage_inner(RightmanageABS):
    '''
    内部API ，跳过auth，便于使用
    '''

    def __init__(self):
        super(Rightmanage_inner,self).__init__()
        self.service_tag = 'inner'
        # auth_conf = ServiceConf(self.service_name,'inner',near=True)
        # self.ip = auth_conf.ip
        # self.port = auth_conf.port

    # curl -X GET --header 'Accept: application/json' 'http://192.168.101.75:8003/rightmanage-ext/v1.0/permissions?systemname=maxguideweb&user_id=1999'
    def permissions(self,systemname,userid,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        data = {'systemname':systemname,'user_id':userid}
        try:
            resp = requests.get('http://{ip}:{port}/rightmanage-ext/{version}/permissions'.format(ip=self.ip,
                                port=self.port,version=version),
                          params=data,headers=headers)
            return resp.status_code,resp.json()
        except Exception as e:
            # 出现例外是服务不可用，需要重新从consul中读取配置
            self._rm_sc = None
            raise

    def create_user(self,login_userid,new_username,new_passwordmd5,companyid):
        '''
        为公司创建一个主账户，公司必须在资料库中已存在
        :param login_userid: 登录用户的id
        :param new_username: 新用户名
        :param new_passwordmd5: 新用户密码的md5值
        :param companyid: 新用户分配的公司
        :return:
        '''
        headers = {'Accept': 'chatset=utf8'}
        params = {'user_id':login_userid}
        data = {"uname":new_username,"passwordmd5":new_passwordmd5,"companyid":companyid}
        try:
            resp = requests.post('http://{ip}:{port}/rightmanage-ext/v1.0/users'.format(ip=self.ip,
                                port=self.port),params=params,
                                json=data,headers=headers)
            return resp.status_code,resp.json()
        except Exception as e:
            # 出现例外是服务不可用，需要重新从consul中读取配置
            self._rm_sc = None
            raise

    def refresh_permissions(self,companyid):
        '''
        刷新redis中某个公司的权限
        :param companyid: 需刷新的compony.id
        :return:
        '''
        headers = {'Accept': 'chatset=utf8'}
        try:
            resp = requests.get('http://{ip}:{port}/rightmanage-ext/v1.0/refresh-permissions/{companyid}'.format(ip=self.ip,
                                port=self.port,companyid=companyid),
                                headers=headers)
            if resp.status_code==422:
                raise Exception(resp.json()['error'])
            elif resp.status_code!=200:
                raise Exception(resp.text)
            return resp.status_code
        except Exception as e:
            # 出现例外是服务不可用，需要重新从consul中读取配置
            self._rm_sc = None
            raise

class AIORightmanage_inner(RightmanageABS):
    '''
    内部API ，跳过auth，便于使用
    支持异步获取权限资料
    '''
    def __init__(self):
        super(AIORightmanage_inner,self).__init__()
        self.service_tag = 'inner'
        # self.service_name = 'rightmanage'
        # auth_conf = ServiceConf(self.service_name,'inner')
        # self.ip = auth_conf.ip
        # self.port = auth_conf.port

    # curl -X GET --header 'Accept: application/json' 'http://192.168.101.75:8003/rightmanage-ext/v1.0/permissions?systemname=maxguideweb&user_id=1999'
    async def permissions(self,systemname,userid,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        params = {'systemname':systemname,'user_id':userid}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://{ip}:{port}/rightmanage-ext/{version}/permissions'.format(ip=self.ip,
                                port=self.port,version=version), params=params) as resp:
                    status = resp.status
                    resp_json = await resp.json()
            return status,resp_json
        except Exception as e:
            # 出现例外是服务不可用，需要重新从consul中读取配置
            self._rm_sc = None
            raise

if __name__ == '__main__':
    rm = Rightmanage_inner()
    # print(auth.login_jwt('ksbus','698d51a19d8a121ce581499d7b701668'))
    try:
        code ,result = rm.create_user('aaa','aa','aa','aa')
        print(result)
    except Exception as e:
        pass
    try:
        code ,result = rm.create_user('aaa','aa','aa','aa')
        print(result)
    except Exception as e:
        pass
    try:
        code ,result = rm.create_user('aaa','aa','aa','aa')
        print(result)
    except Exception as e:
        pass