import json
import base64
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from http.client import HTTPConnection
from multiprocessing import Process

class Config(object):
    PROXY_HTTP_SERVER_HOST="127.0.0.1"
    PROXY_HTTP_SERVER_PORT=8993
    PROXY_HTTP_SERVER_PATH="/proxy"
    HTTP_SERVER_HOST="127.0.0.1"
    HTTP_SERVER_PORT=8992
    HTTP_SERVER_PATH="/hook"
    PROXY_SERVER_HOST = "127.0.0.1"
    PROXY_SERVER_PORT = 8080
    HOOK_REQUEST_KEY = "justd01t"

class HookProxyServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("----------------[HookServer]收到POST请求------------------")
        # print(self.headers)
        print(self.command)
        print(self.path)
        if self.path == Config.HTTP_SERVER_PATH:
            req_datas = self.rfile.read(int(self.headers['content-length']))
            print("----------------[HookServer]开始接受client发送的数据----------------")
            req = req_datas.decode('utf-8')
            try:
                req_dict = json.loads(req)
            except json.JSONDecodeError as e:
                print("----------------[HookServer]无法解析JSON，返回---------------")
                return
            print("----------------[HookServer]已接受client发送的数据------------------")
            if "key" not in req_dict or req_dict["key"] != Config.HOOK_REQUEST_KEY:
                print("----------------[HookServer]无法验证Key，非预期请求，返回---------------")
                return
            print("----------------[HookServer]转发到代理------------------")
            conn = HTTPConnection(Config.PROXY_SERVER_HOST, Config.PROXY_SERVER_PORT)
            payload = json.dumps(req_dict["data"])
            headers = {
                'Content-Type': 'application/json'
            }
            conn.set_tunnel(Config.PROXY_HTTP_SERVER_HOST + ":" + str(Config.PROXY_HTTP_SERVER_PORT))
            conn.request("POST", "/proxy", payload, headers)
            res = conn.getresponse()
            res_data = res.read()
            print("----------------[HookServer]转发到代理------------------")
            try:
                res_dict = json.loads(res_data)
            except json.JSONDecodeError as e:
                print("返回封包失败，无法解析JSON")
            res_dict_2 = {
                "data": res_dict
            }
            res_data = json.dumps(res_dict_2)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
            self.end_headers()
            self.wfile.write(res_data.encode("utf-8"))
        else:
            print("----------------[HookServer]非预期的请求路径，丢弃！------------------")
            return

    def do_OPTIONS(self):
        print("----------------[HookServer]OPTIONS请求------------------")
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()
        print("----------------[HookServer]OPTIONS请求已响应------------------")


class ProxyServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print(self.path)
        if self.path == Config.PROXY_HTTP_SERVER_PATH:
            req_datas = self.rfile.read(int(self.headers['content-length']))
            print("----------------[ProxyServer]直接返回收到的内容----------------")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(req_datas)
            print("----------------[ProxyServer]直接返回收到的内容------------------")
        else:
            print("----------------[ProxyServer]非预期的请求路径，丢弃！------------------")
            return
    

def start_hook_server():
    hook_host = (Config.HTTP_SERVER_HOST, Config.HTTP_SERVER_PORT)
    hook_server = HTTPServer(hook_host, HookProxyServerHandler)
    print("Starting Hook server, listen at: %s:%s" % hook_host)
    hook_server.serve_forever()


def start_proxy_server():
    proxy_host = (Config.PROXY_HTTP_SERVER_HOST, Config.PROXY_HTTP_SERVER_PORT)
    proxy_server = HTTPServer(proxy_host, ProxyServerHandler)
    print("Starting Proxy server, listen at: %s:%s" % proxy_host)
    proxy_server.serve_forever()


def main():
    hook_parame_name = input("输入要代理的变量名字：")
    hook_script_str_1 = "var xhr = new XMLHttpRequest();"\
    "xhr.open('POST', '" + "http://" + Config.HTTP_SERVER_HOST + ":" + str(Config.HTTP_SERVER_PORT) + Config.HTTP_SERVER_PATH + "', true);"\
    "xhr.setRequestHeader('content-type', 'application/json');"\
    "xhr.onreadystatechange = function() {"\
    "if (xhr.readyState == 4) {console.log(xhr.responseText);"\
	"var result = JSON.parse(xhr.responseText);console.log(result);"\
    + hook_parame_name + " = result.data;"\
    "}"\
    "};"\
    "var sendData = {key:'" + Config.HOOK_REQUEST_KEY + "',data:" + hook_parame_name + "};"\
    "xhr.send(JSON.stringify(sendData));"
    print(hook_script_str_1)
    hook_script_str_2 = "caijisec: eval(atob(`{0}`))".format(base64.b64encode(hook_script_str_1.encode("utf-8")).decode("utf-8"))
    print("payload:")
    print(hook_script_str_2)

    hook_server_process = Process(target=start_hook_server)
    hook_server_process.start()
    
    proxy_server_process = Process(target=start_proxy_server)
    proxy_server_process.start()
    proxy_server_process.join()

if __name__ == '__main__':
    main()
