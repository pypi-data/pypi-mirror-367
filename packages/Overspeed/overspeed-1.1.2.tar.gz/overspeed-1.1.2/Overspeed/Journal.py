from . import Library;
from .Function import Function;

class Journal :
    
    @classmethod
    def Lunch(Self , Context:Library.Simple) -> None :
        Function.Proctitle(f'{Context.Config.Proctitle}.Journal');
        if Self.Check(Context) is False : Function.Print(f'{Context.Config.Proctitle}.Journal Unable To Listen, [Http | Websocket | Resource] One Of Them Must Be Activated');
        else :
            Process:list[Library.Processing.Process] = list();
            Process.append(Library.Processing.Process(target = Self.Log , args = (Context , )));
            Process.append(Library.Processing.Process(target = Self.Clean , args = (Context , )));
            for X in Process : X.start();
            for X in Process : X.join();
    
    @staticmethod
    def Check(Context:Library.Simple) -> bool :
        return Context.Config.Http.Journal | Context.Config.Websocket.Journal | Context.Config.Resource.Journal;
    
    @classmethod
    def Log(Self , Context) :
        Function.Proctitle(f'{Context.Config.Proctitle}.Journal.Log');
        Action = list();
        if Context.Config.Http.Journal is True : Action.append('Http');
        if Context.Config.Websocket.Journal is True : Action.append('Websocket');
        if Context.Config.Resource.Journal is True : Action.append('Resource');
        with Library.Executor(max_workers = Context.Config.Journal.Thread) as Executor :
            Function.Print(f'{Context.Config.Proctitle}.Journal Log Start Up, Listen In | Pid[{Library.Os.getpid()}] | [{" | ".join(Action)}]');
            while True :
                if Context.Journal.qsize() == 0 : continue;
                Source = Context.Journal.get();
                Executor.submit(getattr(Self , Source.Method) , Source , Context);
    
    @classmethod
    def Trace(Self , Source:Library.Simple , Context:Library.Simple) -> None :
        Self.Save(Source.Body , Library.Simple(
            Print = True ,
            Path = Context.Config.Runtime.Trace ,
        ));
    
    @classmethod
    def Http(Self , Source:Library.Simple , Context:Library.Simple) -> None :
        Log = list();
        if Source.Type == 'Request' : Log = Self.Request(Source.Body);
        elif Source.Type == 'Response' : Log = Self.Response(Source.Body);
        if not len(Log) == 0 : Self.Save('\n'.join(Log) , Library.Simple(
            Print = Context.Config.Http.Print ,
            Path = Context.Config.Runtime.Http ,
        ));
    
    @classmethod
    def Websocket(Self , Source:Library.Simple , Context:Library.Simple) -> None :
        Log = list();
        if Source.Type == 'Request' : Log = Self.Request(Source.Body);
        elif Source.Type == 'Response' : Log = Self.Response(Source.Body);
        if not len(Log) == 0 : Self.Save('\n'.join(Log) , Library.Simple(
            Print = Context.Config.Websocket.Print ,
            Path = Context.Config.Runtime.Websocket ,
        ));
    
    @classmethod
    def Resource(Self , Source:Library.Simple , Context:Library.Simple) -> None :
        Self.Save('\n'.join(Source.Body) , Library.Simple(
            Print = Context.Config.Resource.Print ,
            Path = Context.Config.Runtime.Resource ,
        ));
    
    @classmethod
    def Request(Self , Source:Library.Simple) -> list :
        Log = list();
        try :
            Log.append(' | '.join([
                'Uuid' ,
                f'[{Source.Uuid}]' ,
            ]));
            Log.append(' | '.join([
                'Socket' ,
                f'[{Source.Socket}]' ,
            ]));
            Log.append(' | '.join([
                'Pid' ,
                f'Server[{Source.Server}]' ,
                f'Worker[{Source.Worker}]' ,
            ]));
            Log.append('----' * 10);
            Log.append(' | '.join([
                'Network' ,
            ]));
            Log.append(' | '.join([
                'Location' ,
                f'Ip[{Source.Location[0]}]' ,
                f'Port[{Source.Location[1]}]' ,
            ]));
            Log.append(' | '.join([
                'Remote' ,
                f'Ip[{Source.Remote[0]}]' ,
                f'Port[{Source.Remote[1]}]' ,
            ]));
            Log.append('----' * 10);
            Log.append(' | '.join([
                'Cors' ,
                f'[{Source.Request.Cors}]' ,
            ]));
            Log.append(' | '.join([
                'Method' ,
                f'[{Source.Request.Method}]' ,
            ]));
            Log.append(' | '.join([
                'Url' ,
                f'[{Source.Request.Url}]' ,
            ]));
            Log.append(' | '.join([
                'Path' ,
                f'[{Source.Request.Path}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Query');
            for X in Source.Request.Query : Log.append(' | '.join([
                X ,
                f'[{Library.Json.dumps(Source.Request.Query.get(X)).decode()}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Body');
            if isinstance(Source.Request.Body , str) : Log.append(Source.Request.Body);
            else :
                for X in Source.Request.Body : Log.append(' | '.join([
                    X ,
                    f'[{Library.Json.dumps(Source.Request.Body.get(X)).decode()}]' ,
                ]));
            Log.append('----' * 10);
            Log.append('Header');
            for X in Source.Request.Header : Log.append(' | '.join([
                X ,
                f'[{Library.Json.dumps(Source.Request.Header.get(X)).decode()}]' ,
            ]));
            Log.append('----' * 10);
            Log.append('Original');
            for X in Source.Request.Original.decode().split('\r\n') :
                if X : Log.append(X);
        except : Function.Trace();
        finally : return Self.Change(Log);
    
    @classmethod
    def Response(Self , Source:Library.Simple) -> list :
        Log = list();
        try :
            Log.append(' | '.join([
                'Uuid' ,
                f'[{Source.Uuid}]' ,
            ]));
            for X in Source.Response : Log.append(' | '.join([
                X ,
                f'[{Source.Response.get(X)}]' ,
            ]));
        except : Function.Trace();
        finally : return Self.Change(Log);
    
    @staticmethod
    def Change(Source:list) -> list :
        Log = list();
        if not len(Source) == 0 :
            for Item in Source :
                Log.append(f'|-- {Item}');
        return Log;
    
    @staticmethod
    def Save(Source:str , Config:Library.Simple) -> None :
        try :
            Calendar = Function.Time(Method = '%Y-%m-%d');
            Hour = Function.Time(Method = '%H');
            Minute = Function.Time(Method = '%M');
            Path = Library.Os.path.realpath('/'.join([
                Library.Os.getcwd() ,
                Config.Path ,
                Calendar ,
                Hour ,
            ]));
            if Library.Os.path.exists(Path) is False : Library.Os.makedirs(Path , exist_ok = True);
            Log = '\n'.join([
                f'|## {"##" * 50}' ,
                f'|| {Function.Time(Method = True)}' ,
                '' ,
                Source ,
                f'|## {"##" * 50}' ,
                '' ,
            ]);
            with open(Library.Os.path.normpath(f'{Path}/{Minute}.log') , 'a' , encoding = 'utf-8') as File : Function.Print(Log , File = File);
            if Config.Print is True : Function.Print(Log);
        except : Function.Trace();
    
    @classmethod
    def Clean(Self , Context) :
        Function.Proctitle(f'{Context.Config.Proctitle}.Journal.Clean');
        Function.Print(f'{Context.Config.Proctitle}.Journal Clean Start Up, Listen In | Pid[{Library.Os.getpid()}] | [{Context.Config.Journal.Clean}] Days');
        Function.Policy();
        while True :
            if int(Function.Time(Method = '%H')) == 1 : Library.Asyncio.gather([
                Self.Remote(Context.Config.Runtime.Http , Context.Config.Journal.Clean) ,
                Self.Remote(Context.Config.Runtime.Websocket , Context.Config.Journal.Clean) ,
                Self.Remote(Context.Config.Runtime.Resource , Context.Config.Journal.Clean) ,
                Self.Remote(Context.Config.Runtime.Trace , Context.Config.Journal.Clean) ,
            ]);
            Library.Time.sleep(Self.Sleep());
    
    @staticmethod
    def Sleep() :
        Current = Function.Time();
        Tomorrow = (Current + Library.Delta(days = 1)).replace(hour = 1 , minute = 0 , second = 0 , microsecond = 0);
        return int((Tomorrow - Current).total_seconds());
    
    @staticmethod
    async def Remote(Path , Day) :
        Route = Library.Os.path.realpath('/'.join([
            Library.Os.getcwd() ,
            Path ,
        ]));
        if Library.Os.path.exists(Route) is False : return False;
        Delta = Function.Time() - Library.Delta(days = Day);
        for Dir in Library.Os.listdir(Route) :
            Base = Library.Os.path.join(Route , Dir);
            if Library.Os.path.isdir(Base) is False : continue;
            try :
                Date = Library.Date.strptime(Dir , '%Y-%m-%d');
                if Date < Delta : Library.Shutil.rmtree(Base);
            except : continue;
        await Library.Asyncio.sleep(0);