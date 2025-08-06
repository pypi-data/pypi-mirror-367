from . import Library;

class Function :
    
    @staticmethod
    def Policy() -> None :
        try : Library.Asyncio.set_event_loop_policy(Library.EventLoopPolicy());
        except : pass;
    
    @staticmethod
    def Proctitle(Source:str) -> None :
        Library.Proctitle(f'{Source}.{Library.Os.getpid()}');
    
    @classmethod
    def Trace(Self , Journal = None) -> None :
        if Journal is None : Self.Print(Library.Traceback.format_exc());
        else : Journal.put(Library.Simple(
            Method = 'Trace' ,
            Body = Library.Traceback.format_exc() ,
        ));
    
    @staticmethod
    def Print(Source:str , File = None) -> None :
        print(Source , end = '\n' , file = File);
    
    @staticmethod
    def Sysctl(Primary:str , Default:str|None = None) -> str|None :
        try : return Library.Subprocess.run([
            'sysctl' ,
            '-n' ,
            Primary ,
        ] , capture_output = True , text = True , check = True).stdout.strip();
        except : return Default;
    
    @staticmethod
    def Hash(Source:str) -> str :
        if isinstance(Source , bytes) is False : Source = Source.encode();
        return Library.Base64.b64encode(Library.Hashlib.sha1(Source).digest()).decode();
    
    @classmethod
    def Ssl(Self , Source:dict) -> Library.Ssl.SSLContext|None :
        if any([
            Source.Keyfile == '' ,
            Source.Certfile == '' ,
        ]) is True : return None;
        Primary = f'SSLContext_{Self.Hash(Library.Json.dumps(dict(
            Keyfile = Source.Keyfile ,
            Certfile = Source.Certfile ,
        )))}'.upper();
        if hasattr(Self , Primary) is False :
            SSLContext = Library.Ssl.SSLContext(Library.Ssl.PROTOCOL_TLS_SERVER);
            SSLContext.load_cert_chain(
                keyfile = f'{Library.Os.getcwd()}{Source.Keyfile}' ,
                certfile = f'{Library.Os.getcwd()}{Source.Certfile}' ,
            );
            SSLContext.set_ciphers('ECDHE+AESGCM');
            SSLContext.options |= Library.Ssl.OP_NO_COMPRESSION;
            setattr(Self , Primary , SSLContext);
        return getattr(Self , Primary);
    
    @staticmethod
    def Bytes(Source:int|float , Suffix:str = 'B') -> str :
        for Unit in ['' , 'K' , 'M' , 'G' , 'T' , 'P'] :
            if abs(Source) < 1024 : return f'{Source:.2f}{Unit}{Suffix}';
            Source /= 1024;
        return f'{Source:.2f}Y{Suffix}';
    
    @staticmethod
    def Time(Method:str|bool|None = None , Utc:bool = True , Int:bool|None = None) -> str|int|float|Library.Date :
        Calendar = Library.Date.utcnow() if Utc is True else Library.Date.now();
        if isinstance(Int , bool) is True :
            Stamp = Calendar.timestamp();
            return int(Stamp) if Int is True else float(Stamp);
        elif any([
            isinstance(Method , str) is True ,
            isinstance(Method , bool) is True ,
        ]) is True :
            if Method is True : Strftime = '%Y-%m-%d %H:%M:%S';
            elif Method is False : Strftime = '%Y-%m-%d';
            else : Strftime = Method;
            return Calendar.strftime(Strftime);
        else : return Calendar;
    
    @staticmethod
    def Uuid() -> str :
        return str(Library.Uuid.uuid4()).replace('-' , '');
    
    @staticmethod
    def Configure(Keyword) -> Library.Simple :
        from . import Const;
        return Library.Simple(
            Proctitle = Keyword.get('Proctitle') if isinstance(Keyword.get('Proctitle') , str) is True and not Keyword.get('Proctitle' , '') == '' else Const.Proctitle ,
            Http = Library.Simple(
                Status = Keyword.get('Http_Status') if isinstance(Keyword.get('Http_Status') , bool) is True else Const.Http_Status ,
                Print = Keyword.get('Http_Print') if isinstance(Keyword.get('Http_Print') , bool) is True else Const.Http_Print ,
                Journal = Keyword.get('Http_Journal') if isinstance(Keyword.get('Http_Journal') , bool) is True else Const.Http_Journal ,
                Cpu = int(Keyword.get('Http_Cpu') if isinstance(Keyword.get('Http_Cpu') , int) is True and Keyword.get('Http_Cpu') > 0 else Const.Http_Cpu) ,
                Port = Keyword.get('Http_Port') if isinstance(Keyword.get('Http_Port') , list) is True and len(Keyword.get('Http_Port')) > 0 else Const.Http_Port ,
                Large = int(Keyword.get('Http_Large') if isinstance(Keyword.get('Http_Large') , int) is True and Keyword.get('Http_Large') > 0 else Const.Http_Large) ,
                Keyfile = Keyword.get('Http_Keyfile') if isinstance(Keyword.get('Http_Keyfile') , str) is True and not Keyword.get('Http_Keyfile' , '') == '' else Const.Http_Keyfile ,
                Certfile = Keyword.get('Http_Certfile') if isinstance(Keyword.get('Http_Certfile') , str) is True and not Keyword.get('Http_Certfile' , '') == '' else Const.Http_Certfile ,
                Callable = Keyword.get('Http_Callable') if callable(Keyword.get('Http_Callable')) is True else Const.Http_Callable ,
            ) ,
            Websocket = Library.Simple(
                Status = Keyword.get('Websocket_Status') if isinstance(Keyword.get('Websocket_Status') , bool) is True else Const.Websocket_Status ,
                Print = Keyword.get('Websocket_Print') if isinstance(Keyword.get('Websocket_Print') , bool) is True else Const.Websocket_Print ,
                Journal = Keyword.get('Websocket_Journal') if isinstance(Keyword.get('Websocket_Journal') , bool) is True else Const.Websocket_Journal ,
                Cpu = int(Keyword.get('Websocket_Cpu') if isinstance(Keyword.get('Websocket_Cpu') , int) is True and Keyword.get('Websocket_Cpu') > 0 else Const.Websocket_Cpu) ,
                Port = Keyword.get('Websocket_Port') if isinstance(Keyword.get('Websocket_Port') , list) is True and len(Keyword.get('Websocket_Port')) > 0 else Const.Websocket_Port ,
                Timeout = int(Keyword.get('Websocket_Timeout') if isinstance(Keyword.get('Websocket_Timeout') , int) is True and Keyword.get('Websocket_Timeout') > 0 else Const.Websocket_Timeout) ,
                Connect = int(Keyword.get('Websocket_Connect') if isinstance(Keyword.get('Websocket_Connect') , int) is True and Keyword.get('Websocket_Connect') > 0 else Const.Websocket_Connect) ,
                Keyfile = Keyword.get('Websocket_Keyfile') if isinstance(Keyword.get('Websocket_Keyfile') , str) is True and not Keyword.get('Websocket_Keyfile' , '') == '' else Const.Websocket_Keyfile ,
                Certfile = Keyword.get('Websocket_Certfile') if isinstance(Keyword.get('Websocket_Certfile') , str) is True and not Keyword.get('Websocket_Certfile' , '') == '' else Const.Websocket_Certfile ,
                Callable = Keyword.get('Websocket_Callable') if callable(Keyword.get('Websocket_Callable')) is True else Const.Websocket_Callable ,
            ) ,
            Resource = Library.Simple(
                Status = Keyword.get('Resource_Status') if isinstance(Keyword.get('Resource_Status') , bool) is True else Const.Resource_Status ,
                Print = Keyword.get('Resource_Print') if isinstance(Keyword.get('Resource_Print') , bool) is True else Const.Resource_Print ,
                Journal = Keyword.get('Resource_Journal') if isinstance(Keyword.get('Resource_Journal') , bool) is True else Const.Resource_Journal ,
                Sleep = int(Keyword.get('Resource_Sleep') if isinstance(Keyword.get('Resource_Sleep') , int) is True and Keyword.get('Resource_Sleep') > 0 else Const.Resource_Sleep) ,
                Cpu = Keyword.get('Resource_Cpu') if isinstance(Keyword.get('Resource_Cpu') , bool) is True else Const.Resource_Cpu ,
                Memory = Keyword.get('Resource_Memory') if isinstance(Keyword.get('Resource_Memory') , bool) is True else Const.Resource_Memory ,
                Network = Keyword.get('Resource_Network') if isinstance(Keyword.get('Resource_Network') , bool) is True else Const.Resource_Network ,
                Disk = Keyword.get('Resource_Disk') if isinstance(Keyword.get('Resource_Disk') , bool) is True else Const.Resource_Disk ,
                File = Keyword.get('Resource_File') if isinstance(Keyword.get('Resource_File') , bool) is True else Const.Resource_File ,
                Load = Keyword.get('Resource_Load') if isinstance(Keyword.get('Resource_Load') , bool) is True else Const.Resource_Load ,
            ) ,
            Journal = Library.Simple(
                Thread = int(Keyword.get('Journal_Thread') if isinstance(Keyword.get('Journal_Thread') , int) is True and Keyword.get('Journal_Thread') > 0 else Const.Journal_Thread) ,
                Clean = int(Keyword.get('Journal_Clean') if isinstance(Keyword.get('Journal_Clean') , int) is True and Keyword.get('Journal_Clean') > 0 else Const.Journal_Clean) ,
            ) ,
            Runtime = Library.Simple(
                Trace = Keyword.get('Runtime_Trace') if isinstance(Keyword.get('Runtime_Trace') , bool) is True else Const.Runtime_Trace ,
                Http = Keyword.get('Runtime_Http') if isinstance(Keyword.get('Runtime_Http') , bool) is True else Const.Runtime_Http ,
                Websocket = Keyword.get('Runtime_Websocket') if isinstance(Keyword.get('Runtime_Websocket') , bool) is True else Const.Runtime_Websocket ,
                Resource = Keyword.get('Runtime_Resource') if isinstance(Keyword.get('Runtime_Resource') , bool) is True else Const.Runtime_Resource ,
            ) ,
        );