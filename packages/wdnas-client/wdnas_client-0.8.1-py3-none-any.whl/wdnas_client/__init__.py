import aiohttp, json, base64
from .exceptions import InvalidLoginError, RequestFailedError
from xml.etree import ElementTree
import http.cookies

RAW_LOGIN_STRING = 'cmd=wd_login&username={username}&pwd={enc_password}'
SCHEME = "http://"


class client:
    def __init__(self, username, password, host):
        self.host = host
        self.username = username.lower()
        self.password = password
        self.session = None
        self.phpsessid = None
        self.wd_csrf_token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        
    async def login(self):
        url = f"{SCHEME}{self.host}/cgi-bin/login_mgr.cgi"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": self.host,
        }

        enc_password = base64.b64encode(self.password.encode('utf-8')).decode("utf-8")

        data = RAW_LOGIN_STRING.format(username=self.username, enc_password=enc_password)

        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:

                set_cookies = response.headers.getall('Set-Cookie', [])
                for cookie_str in set_cookies:
                    cookie = http.cookies.SimpleCookie(cookie_str)
                    for key, morsel in cookie.items():
                        self.session.cookie_jar.update_cookies({key: morsel.value})

                cookies = response.cookies
                if "PHPSESSID" in cookies and "WD-CSRF-TOKEN" in cookies:
                    self.phpsessid = cookies["PHPSESSID"].value
                    self.wd_csrf_token = cookies["WD-CSRF-TOKEN"].value
                else:
                    raise InvalidLoginError("Invalid Username/Password or missing cookies")
            else:
                raise RequestFailedError(response.status)
    
    async def system_info(self):
        url = f"{SCHEME}{self.host}/xml/sysinfo.xml"
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
        }
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                device_info = ElementTree.fromstring(content)
                device_info_json = {"disks": {}, "volumes": {"size":{}}}
                for disk in device_info.iter('disk'):
                    device_info_json['disks'][disk.attrib['id']] = {
                        "name":  disk.findtext('name'),
                        "connected":  bool(int(disk.findtext('connected'))),
                        "vendor":  disk.findtext('vendor'),
                        "model":  disk.findtext('model'),
                        "rev":  disk.findtext('rev'),
                        "sn":  disk.findtext('sn'),
                        "size":  int(disk.findtext('size')),
                        "failed":  bool(int(disk.findtext('failed'))),
                        "healthy":  bool(int(disk.findtext('healthy'))),
                        "removable":  bool(int(disk.findtext('removable'))),
                        "over_temp":  bool(int(disk.findtext('over_temp'))),
                        "temp": int(disk.findtext('temp')),
                        "sleep":  bool(int(disk.findtext('sleep')))
                    }
                for disk in device_info.iter('vol'):
                    device_info_json['volumes'][disk.attrib['id']] = {
                        "name":  disk.findtext('name'),
                        "label":  disk.findtext('label'),
                        "encrypted":  bool(int(disk.findtext('encrypted'))),
                        "unlocked":  bool(int(disk.findtext('unlocked'))),
                        "mounted":  bool(int(disk.findtext('mounted'))),
                        "size":  int(disk.findtext('size')),
                    }
                device_info_json['volumes']['size']['total'] =int(device_info.find('.//total_size').text)
                device_info_json['volumes']['size']['used'] = int(device_info.find('.//total_used_size').text)
                device_info_json['volumes']['size']['unused'] = int(device_info.find('.//total_unused_size').text)
                return device_info_json
            else:
                raise RequestFailedError(response.status)
    
    async def share_names(self):
        url = f"{SCHEME}{self.host}/web/get_share_name_list.php"

        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
        }
        async with self.session.post(url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                json_content = json.loads(content)
                if json_content['success']:
                    return json_content['item']
                else:
                    raise RequestFailedError(response.status)
            else:
                raise RequestFailedError(response.status)
    
    async def system_status(self):
        url = f"{SCHEME}{self.host}/cgi-bin/status_mgr.cgi"
        data = 'cmd=resource'
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                device_status = ElementTree.fromstring(content)
                json_device_status = {"memory": {}, "cpu": None}
                json_device_status['cpu'] = int(device_status.find('.//cpu').text.strip('%'))
                json_device_status['memory']['total'] = int(device_status.find('.//mem_total').text)
                json_device_status['memory']['unused'] = int(device_status.find('.//mem_free').text)
                json_device_status['memory']['simple'] = device_status.find('.//mem2_total').text
                return json_device_status
            else:
                raise RequestFailedError(response.status)
    
    async def network_info(self):
        url = f"{SCHEME}{self.host}/cgi-bin/network_mgr.cgi?cmd=cgi_get_lan_xml"
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
        }

        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                network_info = ElementTree.fromstring(content)
                json_network_info = {}
                for lan in network_info.iter('lan'):
                    mac = lan.findtext('mac')
                    if mac != 'No found.':
                        json_network_info[mac] = {
                            "speed": lan.findtext('speed'),
                            "dhcp_enable": bool(int(lan.findtext('dhcp_enable'))),
                            "dns_manual": bool(int(lan.findtext('dns_manual'))),
                            "ip": lan.findtext('ip'),
                            "netmask": lan.findtext('netmask'),
                            "gateway": lan.findtext('gateway'),
                            "lan_speed": lan.findtext('lan_speed'),
                            "lan_enabled": bool(int(lan.findtext('lan_status'))),
                            "dns1": lan.findtext('dns1'),
                            "dns2": lan.findtext('dns2'),
                            "dns3": lan.findtext('dns3')
                        }
                return json_network_info
            else:
                raise RequestFailedError(response.status)

    async def device_info(self):
        url = f"{SCHEME}{self.host}/cgi-bin/system_mgr.cgi"
        data = 'cmd=cgi_get_device_info'
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                device_info = ElementTree.fromstring(content)
                json_device_info = {"serial_number": None, "name": None, "description": None}
                json_device_info['serial_number'] = device_info.find('.//serial_number').text
                json_device_info['name'] = device_info.find('.//name').text
                json_device_info['description'] = device_info.find('.//description').text
                return json_device_info
            else:
                raise RequestFailedError(response.status)

    async def system_version(self):
        url = f"{SCHEME}{self.host}/cgi-bin/system_mgr.cgi"
        data = 'cmd=get_firm_v_xml'
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                device_version = ElementTree.fromstring(content)
                json_device_version = {"firmware": None, "oled": None}
                json_device_version['firmware'] = device_version.find('.//fw').text
                json_device_version['oled'] = device_version.find('.//oled').text.strip('\n')
                return json_device_version
            else:
                raise RequestFailedError(response.status)
                     
    async def latest_version(self):
        url = f"{SCHEME}{self.host}/cgi-bin/system_mgr.cgi"
        data = 'cmd=get_auto_fw_version'
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                latest_version = ElementTree.fromstring(content)
                json_latest_version = {"new": None, "details": {}}
                json_latest_version['new'] = bool(int(latest_version.find('.//new').text))
                json_latest_version['details']['version'] = latest_version.find('.//version').text
                json_latest_version['details']['path'] = latest_version.find('.//path').text
                json_latest_version['details']['releasenote'] = latest_version.find('.//releasenote').text
                return json_latest_version
            else:
                raise RequestFailedError(response.status)
    
    async def accounts(self):
        url = f"{SCHEME}{self.host}/xml/account.xml"
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
        }
        async with self.session.post(url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                accounts = ElementTree.fromstring(content)
                json_accounts = {"users": {}, "groups": {}}
                for user in accounts.iter('item'):
                    uid = user.findtext('uid')
                    if user.findtext('pwd') is not None:
                        password_bool = bool(int(user.findtext('pwd')))
                    else:
                        password_bool = False
                    last_name_list = []
                    for lastName in user.iter('last_name'):
                        last_name_list.append(lastName.text)
                    json_accounts['users'][uid] = {
                        "name": user.findtext('name'),
                        "email": user.findtext('email'),
                        "pwd": password_bool,
                        "gid": user.findtext('gid'),
                        "first_name": user.findtext('first_name'),
                        "last_name": last_name_list,
                        "hint": user.findtext('hint'),
                    }
                for group in accounts.iter('item'):
                    gid = group.findtext('gid')
                    json_accounts['groups'][gid] = {
                        "name": group.findtext('name'),
                        "user_cnt": user.findtext('user_cnt'),
                    }
                    json_accounts['groups'][gid]['users'] = []
                    for user in group.iter('users'):
                        json_accounts['groups'][gid]['users'].append(user.findtext('user'))
                return json_accounts
            else:
                raise RequestFailedError(response.status)
    
    async def alerts(self):
        url = f"{SCHEME}{self.host}/cgi-bin/system_mgr.cgi"
        data = 'cmd=cgi_get_alert'
        headers = {
            "Host": self.host,
            "X-CSRF-Token": self.wd_csrf_token,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                alerts = ElementTree.fromstring(content)
                json_alerts = []
                for user in alerts.iter('alerts'):
                    json_alerts.append ({
                        "code": user.findtext('code'),
                        "seq_num": user.findtext('seq_num'),
                        "level": user.findtext('level'),
                        "msg": user.findtext('msg'),
                        "desc": user.findtext('desc'),
                        "time": user.findtext('time'),
                    })
                return json_alerts
            else:
                raise RequestFailedError(response.status)