import os
import json
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from multiprocessing import Process

Config = {
    "HTTP_INVOKE_SERVER_HOST": "127.0.0.1",
    "HTTP_INVOKE_SERVER_PORT": 8992,
    "HTTP_INVOKE_SERVER_PATH": "/invokeServer",
    "HOOK_REQUEST_KEY": "justd01t",
    "SCRIPT_PARENT_DIR": os.path.split(os.path.realpath(__file__))[0]
}

class CaijiSecHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, config_dict, bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.config_dict = config_dict

    def finish_request(self, request, client_address) -> None:
        # return super().finish_request(request, client_address)
        self.RequestHandlerClass(request, client_address, self)


class HookInvokeServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        Config = self.server.config_dict
        # print(self.headers)
        # print(self.command)
        print(self.path)
        if self.path == "/test.html":
            with open(os.path.join(Config["SCRIPT_PARENT_DIR"], "testwww/test.html"), "r") as f:
                res_data = f.read()
            self._caiji_easy_response(res_data, "text/html;charset=UTF-8")
        elif self.path == "/test.js":
            with open(os.path.join(Config["SCRIPT_PARENT_DIR"], "testwww/test.js"), "r") as f:
                res_data = f.read()
            self._caiji_easy_response(res_data, "application/javascript")
        elif self.path == "/hookAgent.js":
            with open(os.path.join(Config["SCRIPT_PARENT_DIR"], "hookAgent.js"), "r") as f:
                res_data = f.read()
            self._caiji_easy_response(res_data, "application/javascript")
        elif self.path == "/get":
            res_data = "testHelloGet"
            self._caiji_easy_response(res_data, "application/javascript")
        elif self.path == "/push":
            res_data = "testHelloPush"
            self._caiji_easy_response(res_data, "application/javascript") 
        else:
            self._caiji_easy_response("开发中...", "text/html;charset=UTF-8")


    def do_POST(self):
        Config = self.server.config_dict
        # print(self.headers)
        # print(self.command)
        # print(self.path)
        if self.path == Config["HTTP_INVOKE_SERVER_PATH"]:
            req_datas = self.rfile.read(int(self.headers['content-length']))
            print("[HookServer]开始接受client发送的数据")
            req = req_datas.decode('utf-8')
            print("[HookServer]接收到的内容")
            print(req)
            print("[HookServer]" + "-"*50)
            try:
                req_dict = json.loads(req)
            except json.JSONDecodeError as e:
                print("[HookServer]无法解析JSON，返回")
                return
            print("[HookServer]已接受client发送的数据")
            if "key" not in req_dict or req_dict["key"] != Config["HOOK_REQUEST_KEY"]:
                print("[HookServer]无法验证Key，非预期请求，返回")
                return
            res_dict = "HOOKPROXY"
            print(Config["NEED_START_PROXY_SERVER"])
            
            # 如果不需要再转发一次，直接将请求包的data封装返回
            res_dict = req_dict["data"]

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

            print("[HookServer]返回的内容")
            print(res_data)
            print("[HookServer]" + "-"*50)
            
            self.wfile.write(res_data.encode("utf-8"))
        else:
            print("[HookServer]非预期的请求路径，丢弃！")
            return


    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()
    

    def _caiji_easy_response(self, res_data, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

        print("[HookInvokeServer]返回的内容")
        print(res_data)
        print("[HookInvokeServer]" + "-"*50)
        
        self.wfile.write(res_data.encode("utf-8"))


    

def start_hook_invoke_server(config_dict):
    hook_host = (Config["HTTP_INVOKE_SERVER_HOST"], Config["HTTP_INVOKE_SERVER_PORT"])
    hook_server = CaijiSecHTTPServer(hook_host, HookInvokeServerHandler, config_dict)
    print("Starting Hook Invoke Server, listen at: http://%s:%s" % hook_host)
    hook_server.serve_forever()


def main():
    hook_invoke_server_process = Process(target=start_hook_invoke_server, args=(Config,))
    hook_invoke_server_process.start()
    

    hook_invoke_server_process.join()

if __name__ == '__main__':
    main()
