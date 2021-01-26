"""
文档
https://www.osgeo.cn/tornado/routing.html


todo options 如果不想使用单例模式如何使用?
todo options 获取程序启动时的参数
todo 日志log文件设置
todo 命令行日志
todo 路由映射管理
todo Tornado中的`send_error`, `write_error`和`raise HTTPError`有什么区别?


################ 原理
利用Linux的epoll工具是Tornado不依靠多进程/多线程而达到高性能的原因
    1.创建socket并绑定端口，用linux系统的epoll监听socket读写情况
    2.当socket接收到客户端链接请求时，创建新的socket和客户端通信，并用epoll监听。原来的socket继续监听。此时epoll中有2个
    3.解析socket的请求报文，到rornado.web.Applickation中路由映射列表解析找到对应的类
    4.处理完请求生成响应报文，通过socket返回给客户端
    5.继续循环


################ options
tornado.options是负责解析tornado容器的全局参数的，同时也能够解析命令行传递的参数和从配置文件中解析参数
默认是定义为单例模式


################ request
RequestHandler.request 对象存储了关于请求的相关信息
    method HTTP的请求方式，如GET或POST;
    host 被请求的主机名；
    uri 请求的完整资源标示，包括路径和查询字符串；
    path 请求的路径部分；
    query 请求的查询字符串部分；
    version 使用的HTTP版本；
    headers 请求的协议头，是类字典型的对象，支持关键字索引的方式获取特定协议头信息，例如：request.headers["Content-Type"]
    body 请求体数据；
    remote_ip 客户端的IP地址；
    files 用户上传的文件，为字典类型，型如：
    {
        "form_filename1":[<tornado.httputil.HTTPFile>, <tornado.httputil.HTTPFile>],
        "form_filename2":[<tornado.httputil.HTTPFile>,],
        ...
    }

################ tornado.web.RequestHandler
def write(self, chunk: Union[str, bytes, dict]) -> None:
    write()方法执行不代表视图的终止, 其下如还有代码会继续执行. 该方法把返回的内容会放入输出缓存区, 最后一起发送
    string类型，并把Content-Type设置为text/html:text/html
    dict类型。write检测参数是字典，自动转换为json字符串,并把content-Type设置为application/json; charset=UTF-8
    满足任意条件时, 会将数据返回给前端
        1.程序结束;
        2.手动刷新;
        3.缓存区满了;


def finish(self, chunk: Optional[Union[str, bytes, dict]] = None) -> "Future[None]":
    finish 后不能再执行 write
    可以在 finish 返回结果后做一些与回应给前端无关的操作，缩短响应时间


def redirect( self, url: str, permanent: bool = False, status: Optional[int] = None ) -> None:
重定向到url网址, 302 临时重定向, 新的URL在response 的 Location头中给出，浏览器应该自动地访问新的URL
其他状态码:
    304 - Not Modified 客户端有缓冲的文档并发出了一个条件性的请求（一般是提供If-Modified-Since头表示客户只想比指定日期更新的文档）。服务器告诉客户，原来缓冲的文档还可以继续使用


def send_error(self, status_code: int = 500, **kwargs: Any) -> None:
     手动抛出http错误状态码, 默认为500, 抛出后tornado会调用write_error方法处理.并返回


def write_error(self, status_code: int, **kwargs: Any) -> None:
    处理异常


################ 静态文件


################ 路由
from tornado_widgets.router import Router




"""

from tornado import httpserver, ioloop, web
from tornado.options import options, define

from config import threading

# 定义全局的参数
define('port', default=8000, type=int, help='哈哈')
# 配置文件只用这种方式方便
print(threading)


class IndexHandler(web.RequestHandler):

    def get(self):
        # 页面重定向
        self.redirect("/show")


class Show(web.RequestHandler):
    # get和post都会先调用set_default_headers()
    def set_default_headers(self):
        print('调用 set_default_headers')
        self.set_header('a1', '1111')
        self.set_header('a2', '2222')

    def initialize(self):
        print("调用 initialize")

    # 不论以何种HTTP方式请求，都会执行prepare()方法
    def prepare(self):
        print("调用 prepare")

    def get(self):
        print('调用 get')
        # self.send_error(444, {'error': '错误'})

        self.write("hello itcast 1!")
        self.write('\n')
        self.write("hello itcast 2!")
        data = {'name': '小明', 'age': 10}
        self.write(data)

        self.finish(data)

        # set_header() 会覆盖掉在set_default_headers() 方法中设置的同名headerI
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_header('a1', 'new_a1')
        self.set_status(404)
        self.set_status(222, "aaaaaa")

    def post(self):
        print('调用 post')
        # 获取url种参数, 重名获取最后一个
        get_a = self.get_query_argument('a')
        get_b = self.get_query_arguments('b')
        # 获取请求体参数, 重名获取最后一个
        get_c = self.get_body_argument('c')
        get_d = self.get_body_arguments('d')
        # 同时获取url和请求体参数
        get_e = self.get_argument('e')
        get_c = self.get_arguments('f')

        # 获取发送的文件
        f = self.request.files

        # 获取请求体
        j = self.request.body

        self.write('post over')

    def write_error(self, status, **kargs):
        print('调用 write_error')
        self.write(kargs.get('error_title'))
        self.write(kargs.get('error_content'))

    def on_finish(self):
        print("调用 on_finish")


class Change(web.RequestHandler):
    def get(self):
        # def get(self, **op):
        # RequestHandler.reverse_url(name)来获取该名子对应的url
        python_url = self.reverse_url("python_url")
        self.write('%s' % python_url)


if __name__ == "__main__":
    app = web.Application(
        [(r'/', IndexHandler),
         # (r'/show', Show, {"op": "这是一个字典"}),
         (r'/show', Show,),
         web.url(r'/cc', Change, name="python_url")],
        debug=True)
    http_server = httpserver.HTTPServer(app)

    # 绑定端口
    http_server.bind(options.port)

    # 指定开启几个进程，参数num_processes默认值为1，即默认仅开启一个进程；
    # 如果num_processes为None或者<=0，则自动根据机器硬件的cpu核芯数创建同等数目的子进程
    # 如果num_processes>0，则创建num_processes个子进程。
    http_server.start(num_processes=1)

    ioloop.IOLoop.current().start()
