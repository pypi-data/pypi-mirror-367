from . import Library;
from .Function import Function;
from .Http import Http;
from .Websocket import Websocket;
from .Resource import Resource;
from .Journal import Journal;

def Lunch(*Argrament , **Keyword) -> None :
    try :
        Context = Library.Simple(
            Config = Function.Configure(Keyword) ,
            Journal = Library.Processing.Queue() ,
        );
        Function.Proctitle(Context.Config.Proctitle);
        Process:list[Library.Processing.Process] = list();
        if Context.Config.Http.Status is True : Process.append(Library.Processing.Process(target = Http.Lunch , args = (Context , )));
        if Context.Config.Websocket.Status is True : Process.append(Library.Processing.Process(target = Websocket.Lunch , args = (Context , )));
        if len(Process) == 0 : Function.Print('Http Or Websocket Must Have One Enabled');
        else :
            if Context.Config.Resource.Status is True : Process.append(Library.Processing.Process(target = Resource.Lunch , args = (Context , )));
            Process.append(Library.Processing.Process(target = Journal.Lunch , args = (Context , )));
        for X in Process : X.start();
        for X in Process : X.join();
    except : Function.Trace();