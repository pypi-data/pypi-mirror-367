from . import Library;
from .Function import Function;

Proctitle = 'Overspeed';

Http_Status = True;
Http_Print = False;
Http_Journal = True;
Http_Cpu = Library.Os.cpu_count();
Http_Port = [31100];
Http_Large = 2097152;
Http_Keyfile = str();
Http_Certfile = str();
Http_Callable = None;

Websocket_Status = True;
Websocket_Print = False;
Websocket_Journal = True;
Websocket_Cpu = Library.Os.cpu_count();
Websocket_Port = [31200];
Websocket_Timeout = 5;
Websocket_Connect = 60;
Websocket_Keyfile = str();
Websocket_Certfile = str();
Websocket_Callable = None;

Resource_Status = True;
Resource_Print = False;
Resource_Journal = True;
Resource_Sleep = 30;
Resource_Cpu = True;
Resource_Memory = True;
Resource_Network = True;
Resource_Disk = True;
Resource_File = True;
Resource_Load = True;

Journal_Thread = 100;
Journal_Clean = 7;

Runtime_Trace = '/Runtime/Trace/';
Runtime_Http = '/Runtime/Http/';
Runtime_Websocket = '/Runtime/Websocket/';
Runtime_Resource = '/Runtime/Resource/';

Socket_Host = '0.0.0.0';
Socket_Waittime = 5;
Socket_Listen = int(Function.Sysctl('net.core.somaxconn' , 1024));
Socket_Empty = b'';
Socket_Newline = b'\r\n';
Socket_Keep = b'keep-alive';
Socket_Close = b'close';
Socket_Cors = Socket_Newline.join([
    b'Access-Control-Allow-Origin:*' ,
    b'Access-Control-Allow-Methods:GET,POST,PUT,DELETE,OPTIONS' ,
    b'Access-Control-Allow-Headers:*' ,
    Socket_Empty ,
]);
Socket_Response = Socket_Newline.join([
    b'HTTP/1.1 %s' ,
    b'Content-Type:%s' ,
    b'Content-Length:%d' ,
    b'Connection:%s' ,
    b'%s' ,
    b'%s' ,
]);
Socket_Upgrade = Socket_Newline.join([
    b'HTTP/1.1 101 Switching Protocols' ,
    b'Upgrade:websocket' ,
    b'Connection:Upgrade' ,
    b'Sec-WebSocket-Accept:%s' ,
    Socket_Empty ,
    Socket_Empty ,
]);
Socket_Guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';
Socket_Fin = 0b10000000;
Socket_Opcode = 0b00001111;
Socket_Payload = 0b01111111;
Socket_H = '>H';
Socket_Q = '>Q';

Socket_Html = b'text/html';
Socket_Image = b'image/*';
Socket_Plain = b'text/plain';
Socket_Xml = b'application/xml';
Socket_Json = b'application/json';
Socket_Stream = b'text/event-stream';
Socket_Data = b'multipart/form-data';
Socket_Javascript = b'application/javascript';
Socket_Url = b'application/x-www-form-urlencoded';

Socket_200 = b'200 OK';
Socket_204 = b'204 No Content';
Socket_301 = b'301 Moved Permanently';
Socket_302 = b'302 Found';
Socket_400 = b'400 Bad Request';
Socket_401 = b'401 Unauthorized';
Socket_402 = b'402 Bad Internal';
Socket_403 = b'403 Forbidden';
Socket_404 = b'404 Not Found';
Socket_405 = b'405 Method Not Allowed';
Socket_406 = b'406 Not Acceptable';
Socket_407 = b'407 Body Error';
Socket_408 = b'408 Request Timeout';
Socket_413 = b'413 Payload Too Large';
Socket_415 = b'415 Unsupported Media Type';
Socket_429 = b'429 Too Many Requests';
Socket_500 = b'500 Internal Server Error';
Socket_502 = b'502 Bad Gateway';
Socket_503 = b'503 Service Unavailable';
Socket_504 = b'504 Gateway Timeout';