import requests
import socket
from stem import Signal
from stem.control import Controller

def get_device_info():
    """Получение информации об устройстве"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return {
        "device_name": hostname,
        "local_ip": local_ip
    }

class TorAnonymizer:
    """Класс для анонимизации через Tor"""
    def __init__(self, tor_port=9050, ctrl_port=9051):
        self.tor_proxy = {
            'http': f'socks5h://127.0.0.1:{tor_port}',
            'https': f'socks5h://127.0.0.1:{tor_port}'
        }
        self.ctrl_port = ctrl_port
        self.session = requests.Session()
        self.session.proxies = self.tor_proxy
        
    def renew_connection(self):
        """Смена Tor цепи для нового IP"""
        with Controller.from_port(port=self.ctrl_port) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
    
    def get_public_ip(self):
        """Получение публичного IP"""
        try:
            return self.session.get('https://api.ipify.org').text
        except:
            return "Не удалось определить IP"

    def make_request(self, url, method='GET', **kwargs):
        """Выполнение анонимного запроса"""
        return self.session.request(method, url, **kwargs)
