from mwutils.mw_consul import KongConf,KongAdminConf
import requests
class KongError(Exception):
    pass

get_host = lambda host: '{http}{host}'.format(http='http://' if not host.startswith('http://') else '',
                                              host=host)
replace = lambda service:service.replace('.','_').replace('/','_').replace(':','_')
# 补充 /
get_backslash = lambda path:'{bs}{path}'.format(bs='/' if not path.startswith('/') else '',
                                                path=path)
class Kong():
    def _init_conf(self):
        self._kong = KongConf(self.kong_tag)
        self._kong_admin = KongAdminConf(self.kong_admin_tag)
        self.version = requests.get(self._kong_admin.host_url()).json()['version']

    def __init__(self,kong_tag='kong',kong_admin_tag='admin'):
        self.kong_tag= kong_tag
        self.kong_admin_tag= kong_admin_tag 
        self._init_conf()

    @property
    def ip(self):
        return self._kong.ip

    @property
    def port(self):
        return self._kong.port

    @property
    def admin_port(self):
        return self._kong_admin.port

    @property
    def host(self):
        return self._kong.host_url()

    @property
    def admin_host(self):
        return self._kong_admin.host_url()

    def reload(self):
        # 重新導入kong的配置
        self._init_conf()
    
    def __repr__(self):
        return f'kong:{self.host},kong admin:{self.admin_host},version:{self.version}'
    
    def reg_service(self,service,service_host, auth='jwt', kong_uris=''):
        # 旧版本的kong，注册服务到 apis
        if self.version < '0.15':
            self.add_apis(service,service_host, auth,kong_uris)
        else: # 新版本的kong,测试是以3.9.X，注册服务到 services
            self.add_services(service,service_host, auth,kong_uris)

    def add_services(self,service,service_host, auth='jwt', kong_uris=''):
        '''
        :param kong_admin: 用于注册服务
        :param service_host: 本地服务的host，用于设定upstream_url
        :param service: 服务api，如：rightmanage/v1.0
        :param kong_uris: 空的host uris，为空时值为service,如：rightmanage/v1.0
        :param auth: 认证类型，可为str或list，如：'jwt'，或：['jwt','key']
        :param health: 如果service_host 是upstreams，则可以注册health
        :return:
        '''
        ''''
        curl -i -s -X POST http://localhost:8001/services \
            --data name=example_service \
            --data url='https://httpbin.konghq.com'

        kong.reg_service('static', 'auth-server', auth='jwt', kong_uris='auth/static')
        kong.reg_service('auth/v1.0/login_face', 'auth-server', auth='')

        '''
        services_url = f'{self.admin_host}/services'
        uris = get_backslash(kong_uris if kong_uris else service)
        # 如果kong_uris有值，则需要用它注册
        # service 为/，则service_name 按service_host 产生
        service_name = replace(service_host) if service == '/' else replace(uris[1:])
        # print('uris',uris)
        upstream_url = f'{get_host(service_host)}{get_backslash(service)}'
        try:
            '''
            curl --request GET \
                --url http://localhost:8001/services/test-service \
                --header 'accept: application/json'
            '''
            resp = requests.get(f'{services_url}/{service_name}')
            print(f'get {services_url}/{service_name} {resp.status_code}')
            body ={'name': service_name,
                   'url': upstream_url,
                #    'host': service_host,
                #    "path" : '/' if kong_uris else '/' 
                   }
            if resp.status_code == 200:
                resp = requests.patch(f'{services_url}/{service_name}',json=body)
            else:
                resp = requests.post(services_url,
                                    json=body)
            print(f'add {service_host}/{service} to kong success ,{resp.status_code}')
            # print(resp.text)
            '''
            curl -i -X POST http://localhost:8001/services/example_service/routes \
                    --data 'paths[]=/mock' \
                    --data name=example_route
            '''
            routes_url = f'{self.admin_host}/services/{service_name}/routes'
            route_name = f'{service_name}_rt'
            route_data = {'name': route_name,
                          'paths': [uris]}
            routes_get_url = f'{routes_url}/{route_name}'
            resp = requests.get(routes_get_url)
            print(f'get {routes_get_url} {resp.status_code} ')
            # print(resp.text)
            if resp.status_code == 200:
                resp = requests.patch(routes_get_url, json=route_data)
            elif resp.status_code == 404:
                resp = requests.post(routes_url, json=route_data)
            else:
                raise Exception('get routes fail')
            print(f'post {routes_url} , {resp.status_code}')
            # print(f'body:{route_data} \n text:{resp.text}')
        except Exception as e:
            print('注册 %s服务失败,error:%s' % (service, e))
            import sys
            sys.exit(-1)
        if auth:
            if isinstance(auth, str):
                auth, auth_str = [], auth
                auth.append(auth_str)
            '''
            curl --request POST \
                --url http://localhost:8001/routes/my-route/plugins \
                --header 'Content-Type: application/json' \
                --header 'accept: application/json' \
                --data '{"name":"rate-limiting","route":"string"...'
            '''
            if 'jwt' in auth:
                auth_data =  {"name": "jwt",
                              "enabled":True,
                              "config": {
                                    "cookie_names": [
                                        "sessionid"
                                    ],
                                    "header_names": [
                                        "authorization"
                                    ],
                                    "key_claim_name": "iss",
                                    # "maximum_expiration": 0,
                                    "run_on_preflight": True,
                                    "secret_is_base64": False,
                                    "uri_param_names": [
                                        "jwt"
                                    ]
                                },
                             }

            elif 'key' in auth:
                auth_data =  {"name": "key-auth",
                              
                              "enabled": True,
                              "config": {
                            #   "key_in_body": False,
                            #   "key_in_header": True,
                              "key_in_query": True,
                              "key_names": [
                                 "apikey"
                                ],
                              "run_on_preflight": True,
                              }
                             }
            else:
                raise Exception('不支持的auth(%s)' % auth)
            auth_data['instance_name'] = f'{route_name}_{auth_data["name"]}'
            plugins_url = f'{self.admin_host}/routes/{route_name}/plugins'
            resp = requests.get(plugins_url)
            print(f'get {plugins_url},code:{resp.status_code}')
            # print(resp.text))
            plugin_id = None
            # 每个plugin 只能注册一次

            for auth_data_k in resp.json().get('data',[]):
                if auth_data['name'] == auth_data_k['name']:
                    plugin_id = auth_data_k['id']
                    break
            if plugin_id:
                resp = requests.patch(f'{plugins_url}/{plugin_id}',
                                      json=auth_data)
            else:
                resp = requests.post(plugins_url,
                                    json=auth_data)
            print(f'register {service} to kong ,auth_name:{auth},code:{resp.status_code}')
            # print(resp.text))

    def add_apis(self,service,service_host, auth='jwt', kong_uris=''):
        '''
        :param kong_admin: 用于注册服务
        :param service_host: 本地服务的host，用于设定upstream_url
        :param service: 服务api，如：rightmanage/v1.0
        :param kong_uris: 空的host uris，为空时值为service,如：rightmanage/v1.0
        :param auth: 认证类型，可为str或list，如：'jwt'，或：['jwt','key']
        :param health: 如果service_host 是upstreams，则可以注册health
        :return:
        '''
        ''''
        # 注册 服务API
        resp = requests.post('http://{kong}/apis/'.format(kong=KONG),
                             json={'name': 'rightmanage_v1.0',
                                   'uris': '/rightmanage/v1.0',
                                   'upstream_url': 'http://{server}/rightmanage/v1.0'.format(server=SERVER)})
        print('注册 服务API', resp.text)

        resp = requests.post('http://{kong}/apis/rightmanage_v1.0/plugins'.format(kong=KONG),
                             json={"name": "jwt"})
        print('注册服务API JWT', resp.text)
        '''
        api_url = f'{self.admin_host}/apis/'
        # 如果kong_uris有值，则需要用它注册
        api_name = replace(get_backslash(service if not kong_uris else kong_uris)[1:])
        if kong_uris:
            uris = '{service}'.format(service=get_backslash(kong_uris))
        else:
            uris = '{service}'.format(service=get_backslash(service))
        print('uris',uris)
        upstream_url = '{service_host}{service}'.format(service_host=get_host(service_host),
                                                        service=get_backslash(service))
        try:
            # 删除旧的api
            resp = requests.delete('{kong}/apis/{api_name}'.format(kong=self.admin_host,
                                                            api_name=api_name))
            print('del api(%s)'%api_name,',code:',resp.status_code,',text:',resp.text)
            resp = requests.post(api_url,
                                 json={'name': api_name,
                                       'uris': uris,
                                       'upstream_url': upstream_url,
                                       'preserve_host': True})
            print('注册%s服务 to kong 成功,'%service, resp.text)
        except Exception as e:
            print('注册 %s服务失败,error:%s' % (service, e))
            import sys
            sys.exit(-1)
        if auth:
            if isinstance(auth, str):
                auth, auth_str = [], auth
                auth.append(auth_str)
            if 'jwt' in auth:
                auth_data =  {"name": "jwt",
                             "config.uri_param_names": "jwt",
                             "config.claims_to_verify": "exp",
                             "config.key_claim_name": "iss",
                             "config.secret_is_base64": "false",
                             "config.cookie_names": "sessionid"
                             }

            elif 'key' in auth:
                auth_data =  {"name": "key-auth",
                             "config.key_names": "apikey"
                             }
            else:
                raise Exception('不支持的auth(%s)' % auth)

            resp = requests.post('{kong}/apis/{api_name}/plugins'.format(kong=self.admin_host,
                                                                         api_name=api_name),
                                 json=auth_data)
            if resp.status_code != 201:
                # 在0.12.1之前的kong 不支持config.cookie_names
                if 'jwt' in auth:
                    auth_data.pop('config.cookie_names')
                    resp = requests.post('{kong}/apis/{api_name}/plugins'.format(kong=self.admin_host,
                                                                                 api_name=api_name),
                                         json=auth_data)
            if resp.status_code == 201:
                print('注册%s服务API %s 成功' % (service,auth), resp.text)
            else:
                print('注册%s服务API %s 失败' % (service,auth), resp.status_code, resp.text)

    def add_upstream_target(self, upstream_name, service_host, weight,health):
        '''

        :param upstream_name: monitor-srv
        :param service_host: ip:port
        :param weight: 100
        :param health: 如： ordermng/v1.0/health, realtime-srv/v1.0/health
        :return:
        '''
        ''''
        # create an upstream
        $ curl -X POST http://kong:8001/upstreams \
            --data "name=address.v1.service"

        # add two targets to the upstream
        $ curl -X POST http://kong:8001/upstreams/address.v1.service/targets \
            --data "target=192.168.101.75:80"
            --data "weight=100"
        $ curl -X POST http://kong:8001/upstreams/address.v1.service/targets \
            --data "target=192.168.100.76:80"
            --data "weight=50"

        # create a Service targeting the Blue upstream
        $ curl -X POST http://kong:8001/apis/ \
            --data "name=service-api" \
            --data "uris=/aa"
            --data "upstream_url=http://address.v1.service"
        '''
        # 打印kong的信息
        print(self)
        upstream_api_url = f'{self.admin_host}/upstreams/'
        # add upstream
        try:
            if self.version <= '0.15':
                upstream = {'name': upstream_name,
                        'healthchecks.active.http_path': health,
                        'healthchecks.active.healthy.interval': 5,
                        'healthchecks.active.healthy.successes': 1,
                        'healthchecks.active.unhealthy.interval': 5,
                        'healthchecks.active.unhealthy.tcp_failures': 1,
                        'healthchecks.active.unhealthy.timeouts': 3,
                        'healthchecks.active.unhealthy.http_failures': 1
                        }
            else:
                upstream = {'name': upstream_name,
                        "healthchecks": {
                        "threshold": 0,
                        "active": {
                            "type": "http",
                            "timeout": 1,
                            "concurrency": 10,
                            "http_path": health,
                            "healthy": {
                                "interval": 5,
                                "successes": 5,
                                "http_statuses": [200, 302]
                             },
                            "unhealthy": {
                                "interval": 5,
                                "timeouts": 3,
                                "http_failures": 1,
                                "tcp_failures": 1,
                                "http_statuses": [429, 404, 500, 501, 502, 503, 504, 505]
                             }
                        }
                        }
                }
            upstream_name_url = upstream_api_url + upstream_name
            resp = requests.get(upstream_name_url)
            # print(f'get {upstream_api_url},code:{resp.status_code}')
            if resp.status_code==200:
                resp = requests.patch(upstream_api_url+upstream_name, json=upstream)
            elif resp.status_code==404:
                resp = requests.post(upstream_api_url, json=upstream)
            else:
                raise Exception(f'添加{upstream_name} upstream到kong失败,code:{resp.status_code},text:{resp.text}')
            print(f'add {upstream_name} upstream to kong success,code: {resp.status_code}')
            # print(resp.text))
        except Exception as e:
            print(f'add {upstream_name} upstream失败,error:{e}')
            import sys
            sys.exit(-1)
        targets_api_url = f'{self.admin_host}/upstreams/{upstream_name}/targets'
        try:
            if self.version <= '0.15':
                resp = requests.post(targets_api_url,
                                     json={'target': f'{service_host}',
                                           'weight': weight
                                           })
            else:
                resp = requests.get(f'{targets_api_url}/{service_host}')
                if resp.status_code==404:
                    resp = requests.post(targets_api_url,
                                    json={'target': f'{service_host}',
                                          'weight': weight
                                        })
                elif resp.status_code==200:
                    resp = requests.patch(f'{targets_api_url}/{service_host}',
                                    json={'target': f'{service_host}',
                                          'weight': weight
                                        })
                else:
                    raise Exception(f'add {service_host} target to {upstream_name} ,code:{resp.status_code},text:{resp.text}')
            print(f'add target for {upstream_name} to kong success,code: {resp.status_code}')
            # print(resp.text))
        except Exception as e:
            print('add target for %s失败,error:%s' % (upstream_name, e))
            import sys
            sys.exit(-1)



if __name__ == '__main__':
    '''
    curl -X Delete 'http://192.168.101.31:8001/apis/test_v1_0'
    curl -X Post 'http://192.168.101.31:8001/apis/' -d '{"upstream_url": "http://192.168.101.88:8001/test/v1.0", "preserve_host": true, "uris": "/test/v1.0", "name": "test_v1_0"}'
    curl -X Post 'http://192.168.101.31:8001/apis/test_v1_0/plugins' -d '{"name": "jwt"}'
    '''
    # k = Kong(kong_tag='kong',kong_admin_tag='admin')
    k = Kong(kong_tag='kong_new',kong_admin_tag='admin_new')
    # print(k)
    service_host = '192.168.101.78:30043'
    k.add_upstream_target('monitor-srv',service_host, 100,'/monitor-srv/v1.0/health')
    k.reg_service('monitor-srv/v1.0', 'monitor-srv', auth='jwt', kong_uris='')
    k.reg_service('monitor-srv/v1.0', 'monitor-srv', auth='jwt', kong_uris='')
    k.reg_service('monitor-srv/v1.0', 'monitor-srv', auth='key', kong_uris='')
    k.reg_service('monitor-srv/v1.0/ctrl_command', 'monitor-srv', auth='key', kong_uris='vehicle-monitor/v1.0/openclose_door')
    # service_host = 'httpbin.konghq.com:443'
    # k.add_upstream_target('httpbin-srv',service_host, 100,'/')
    # k.reg_service('/', 'httpbin-srv', auth='', kong_uris='/mock')

