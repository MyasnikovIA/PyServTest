import sys
import os
import socket
from _thread import *
import hashlib
import subprocess
import os.path
import subprocess


# begin  WebServerQuery
class WebServerQuery:
    __array_pipe__={}
    _lastio = None
    _lastioerror = None
    __client_connection = None
    request = {}
    dirfile = None
    __contenttype = {"py":"text/html","psp":"text/html","css":"text/css","js":"application/x-javascript",
        "xml":"text/xml","dtd":"text/xml","txt":"text/plain","inf":"text/plain","nfo":"text/plain",
        "php":"text/plain","html":"text/html","csp":"text/html","htm":"text/html","shtml":"text/html",
        "shtm":"text/html","stm":"text/html","sht":"text/html","sht":"text/html","csp":"text/html",
        "mac":"text/html","cls":"text/html","jpg":"image/jpeg","cos":"text/html","mpeg":"video/mpeg",
        "mpg":"video/mpeg","mpe":"video/mpeg","ai":"application/postscript","zip":"application/zip",
        "zsh":"text/x-script.zsh","x-png":"image/png","xls":"application/x-excel","xlm":"application/excel",
        "wav":"audio/x-wav","txt":"text/plain","tiff":"image/tiff","tif":"image/x-tiff","text":"text/plain",
        "swf":"application/x-shockwave-flash","sprite":"application/x-sprite","smil":"application/smil",
        "sh":"text/x-script.sh","rtx":"text/richtext","rtf":"text/richtext","pyc":"application/x-bytecode.python",
        "png":"image/png","pic":"image/pict","mp3":"video/mpeg","mp2":"video/mpeg","movie":"video/x-sgi-movie",
        "mov":"video/quicktime","mjpg":"video/x-motion-jpeg","mime":"www/mime","mif":"application/x-mif",
        "midi":"audio/midi","js":"application/javascript","jpeg":"image/jpeg","jps":"image/x-jps","jam":"audio/x-jam",
        "jav":"text/plain","java":"text/x-java-source","htm":"text/html","html":"text/html",
        "gzip":"application/x-gzip","gif":"image/gif","gl":"video/gl","csh":"text/x-script.csh",
        "css":"text/css","bsh":"application/x-bsh","bz":"application/x-bzip","bz2":"application/x-bzip2",
        "c":"text/plain","c++":"text/plain","cat":"application/vnd.ms-pki.seccat","cc":"text/plain",
        "htmls":"text/html","bmp":"image/bmp","bm":"image/bmp","avi":"video/avi","avs":"video/avs-video",
        "au":"audio/basic","arj":"application/arj","art":"image/x-jg","asf":"video/x-ms-asf","asm":"text/x-asm",
        "asp":"text/asp"}

    def __init__(self, client, addr, userdirfile):
        self.dirfile = userdirfile
        self.__client_connection = client
        self.request = {'ip': addr[0]}
        self.request['cookie'] = {}
        self.request['data'] = {}
        inputhead =b""
        # inputhead =self.__client_connection.recv(32768)
        while True:
             inputhead += self.__client_connection.recv(32768)
             if not inputhead:
                 break
             if len(inputhead)<32768:
                 break
        self._lastio = sys.stdout
        sys.stdout = self.__client_connection.makefile('w')
        headtxt = inputhead.decode()
        arrhead = headtxt[:headtxt.find("\r\n\r\n")]
        arrhead = arrhead.replace('\n', '')
        arrhead = str(arrhead).split('\r')
        for (ind, line) in enumerate(arrhead):
            if ind == 0:  # парсим первую строку запроса     0  =  GET /index.html?v=1 HTTP/1.1
                typequery = line[:line.find(" ")]
                webquery = line[line.find(" ") + 1:line.find(" HTTP/")]
                protocolquery = line[1 + line.find(" HTTP/"):]
                attr = {}
                if webquery.find('?') > -1:
                    attrlist = webquery[webquery.find("?") + 1:]
                    self.request['attrebute'] = attrlist
                    attr = self.__parseattrebute__(attrlist, '&', '=')
                    webquery = webquery[:webquery.find("?")]

                self.request['protocol'] = protocolquery
                if webquery[-1:] == '/':
                    webquery = webquery + 'index.html'
                if len(webquery) == 0:
                    webquery = '/index.html'
                self.request['query'] = webquery
                file = webquery.split('.')
                self.request['exec'] = file[-1].lower().replace("/", "")
                self.request['typequery'] = typequery
                if 'typ' in attr:
                    self.request['typ'] = attr['typ'].lower()
                    del attr['typ']
                self.request['data'] = attr
                continue
            nam = line[:line.find(":")]
            nam = nam.upper()
            val = line[line.find(":") + 2:]
            self.request[nam] = val
            if nam == 'COOKIE':
                self.request['cookie'] = self.__parseattrebute__(val, ';', '=')
        if 'USER-AGENT' in self.request:
            sessionid = self.request['USER-AGENT'] + addr[0]
        else:
            sessionid = addr[0]
        sessionid = hashlib.md5(sessionid.encode())
        self.request['sessionid'] = sessionid.hexdigest()
        self.request['dir'] = self.dirfile
        filepath = self.dirfile + self.request['query']
        filepath = filepath.replace("\\/", os.sep)
        self.request['filepath'] = filepath
        if "CONTENT - LENGTH" in self.request:  # Выделяем тело POST запроса (Добрботать!!!)
            self.request['post'] = headtxt[headtxt.find("\r\n\r\n"):]

    def drawhead(self):
        contenttype = "text/html"
        if 'typ' in self.request:
           rashirenie = self.request['typ']
        elif 'exec' in self.request:
           rashirenie = self.request['exec']
        else:
           rashirenie = 'html'
        if rashirenie in self.__contenttype:
           contenttype = self.__contenttype[rashirenie]
        else:
           contenttype = "application/octet-stream"
        try:
            self.__client_connection.sendall(b'HTTP/1.1 200 OK\r\n')
            self.__client_connection.sendall(b'Content-type: ')
            self.__client_connection.sendall(contenttype.encode())
            self.__client_connection.sendall(b'\r\n')
            self.__client_connection.sendall(b'Connection: close\r\n')
            self.__client_connection.sendall(b'\r\n')
        except:
            print("An exception occurred", self.request)

    def drawbodypsp(self):
        try:
            f = open(self.request['filepath'])
            for txt in f:
                arrstart = txt.split(")#")
                for frag in arrstart:
                    if '#(' in frag:
                        txt = frag[:frag.find("#(")]
                        cod = frag[frag.find("#(") + 2:]
                        if len(cod)>0 :
                           sys.stdout.write(txt)
                           res = str(eval(cod))
                           sys.stdout.write(res)
                           sys.stdout.flush()
                        else:
                           sys.stdout.write(txt)
                           sys.stdout.flush()
                    else:
                        sys.stdout.write(frag)
                        sys.stdout.flush()
        except:
            print("Something went wrong when writing to the file")
        finally:
            f.close()

    
    def drawbodypy(self):
        # 1) нужен механизм для подключения к ранее созданному процессу
        # 2) нужен механизм остановки (паузы) у паралельного процесса(ожидание сигнала для снятия с паузы),
        """
        if self.request['sessionid'] in self.__array_pipe__:
            print('sessionid ',self.request['sessionid'])
            # Восстанавливаем поток из глобального массива
            # pipe = self.__array_pipe__[self.request['sessionid']]
        else:
            print('NO sessionid ',self.request['sessionid'])
            # Запоминаем созданный поток в  глобальный массив
            # self.__array_pipe__[self.request['sessionid']]=pipe
        """
        pipe = subprocess.Popen([sys.executable, self.request['filepath']]
                                 , stdout=subprocess.PIPE
                                 , shell=True
                                 , stdin=subprocess.PIPE
                                 , stderr=subprocess.STDOUT)

        pipe.stdin.write(repr(self.request).encode("utf8"))
        pipe.stdin.close()
        # pipe.wait()
        out, err = pipe.communicate()
        sys.stdout.write(out.decode("utf-8"))


    def drawbody(self):
        sys.stdout = self._lastio
        try:
            with open(self.request['filepath'], mode='rb') as file:  # b is important -> binary
                self.__client_connection.sendall(file.read())
        except:
            print("Something went wrong when writing to the file")
        finally:
            sys.stdout = self.__client_connection.makefile('w')  # file interface: text, buffered

    def cls(self):
        sys.stdout = self._lastio
        self.__client_connection.close()

    def __parseattrebute__(self, value, spel='&', spval='='):
        res = {}
        if len(value) == 0:
            return res
        array = value.split(spel)
        for (ind, line) in enumerate(array):
            nam = line[:line.find(spval)]
            val = line[line.find(spval) + 1:]
            if len(nam) > 0:
                res[nam] = val
        return res
# end WebServerQuery

# begin  WebServer
class WebServer:
    port = 8080
    dirfile = None

    def __init__(self, portsocket=8080, userdirfile=""):
        self.port = portsocket
        self.dirfile = userdirfile
        if self.dirfile == "":
            self.dirfile = os.path.abspath(os.curdir) + os.sep + 'www' + os.sep
        if not os.path.isdir(self.dirfile):
            os.mkdir(self.dirfile)

    def setPort(self, portsocket=8080):
        self.port = portsocket

    def setQueryDef(self, userquerydef):
        self.querydef = userquerydef

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.port))
        # mac = hexlify(s.getsockname()[4])
        s.listen(5)
        while True:
            сonnect, addr = s.accept()
            print('Connected to :', addr[0], ':', addr[1])
            # Start a new thread and return its identifier
            start_new_thread(self.__runclientthreaded, (сonnect, addr, self.dirfile))
            # print(os.getpid())
        s.close()

    def __runclientthreaded(self, сonnect, addr, dirfile):
            webclient = WebServerQuery(сonnect, addr, dirfile)
            if os.path.exists(webclient.request['filepath']) == False:
                webclient.request['exec'] = 'txt'
                webclient.drawhead()
                print('File not found', webclient.request['filepath'])
            elif webclient.request['exec'] == 'py':  # PythonScript
               webclient.drawhead()
               webclient.drawbodypy()
            elif webclient.request['exec'] == 'psp':  # PythonServicePage
               webclient.drawhead()
               webclient.drawbodypsp()
            else:
               webclient.drawhead()
               webclient.drawbody()
            webclient.cls()
# end  WebServer




def main():
    host = ""
    try:
        port = sys.argv[1]
    except IndexError:
        port = 8080
    srv = WebServer(port)
    srv.start()



if __name__ == '__main__':
    main()
