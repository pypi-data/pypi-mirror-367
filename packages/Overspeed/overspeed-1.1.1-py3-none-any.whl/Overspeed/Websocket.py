from . import Library , Const;
from .Function import Function;
from .Control import Control;

class Websocket :
    
    @classmethod
    def Lunch(Self , Context:Library.Simple) -> None :
        Context.Signal = Library.Simple(
            Proctitle = f'{Context.Config.Proctitle}.Websocket' ,
            Config = Context.Config.Websocket ,
            Handle = Self.Client ,
        );
        Control.Lunch(Context);
    
    @classmethod
    async def Client(Self , Context:Library.Simple , Reader:Library.Asyncio.StreamReader , Writer:Library.Asyncio.StreamWriter) -> None :
        try :
            while True :
                Context = await Control.Request(Context , Reader);
                if Context.Signal.Request.Status is False : break;
                if len(Context.Signal.Request.Header) == 0 : raise ValueError(402);
                if Context.Signal.Request.Header.get('upgrade' , str()).lower() == 'websocket' :
                    await Self.Upgrade(Context , Writer);
                    await Self.Session(Context , Reader , Writer);
        except ValueError as Error :
            try :
                Context.Signal.Response = dict(Code = Error.args[0]);
                await Self.Send(Context , Writer);
            except : Function.Trace(Context.Journal);
        except : Function.Trace(Context.Journal);
    
    @staticmethod
    async def Upgrade(Context:Library.Simple , Writer:Library.Asyncio.StreamWriter) -> None :
        try :
            if Writer.is_closing() is False :
                Writer.write(Const.Socket_Upgrade % (
                    Function.Hash(f'{Context.Signal.Request.Header.get("sec-websocket-key")}{Const.Socket_Guid}').encode() ,
                ));
                await Writer.drain();
        except : Function.Trace(Context.Journal);
        finally : await Library.Asyncio.sleep(0);
    
    @classmethod
    async def Session(Self , Context:Library.Simple , Reader:Library.Asyncio.StreamReader , Writer:Library.Asyncio.StreamWriter) -> None :
        try :
            Context.Begin = Function.Time(Int = False);
            Queue = Library.Asyncio.Queue();
            Waiting = Library.Asyncio.create_task(Self.Worker(Queue , Context.Journal , Writer));
            while True :
                if (Function.Time(Int = False) - Context.Begin) > Context.Signal.Config.Connect : break;
                if Context.Signal.Config.Timeout > 0 :
                    try : Header = await Library.Asyncio.wait_for(Reader.readexactly(2) , timeout = Context.Signal.Config.Timeout);
                    except : break;
                else : Header = await Reader.readexactly(2);
                Fin = Header[0] & Const.Socket_Fin;
                Opcode = Header[0] & Const.Socket_Opcode;
                Masked = Header[1] & Const.Socket_Fin;
                Payload = Header[1] & Const.Socket_Payload;
                if Payload == 126 : Payload = Library.Struct.unpack(Const.Socket_H , await Reader.readexactly(2))[0];
                if Payload == 127 : Payload = Library.Struct.unpack(Const.Socket_Q , await Reader.readexactly(8))[0];
                Mask = await Reader.readexactly(4) if Masked else Const.Socket_Empty;
                Load = await Reader.readexactly(Payload);
                if Masked : Load = bytes(Byte ^ Mask[Index % 4] for Index , Byte in enumerate(Load));
                if Opcode in (1 , 2) :
                    try : Context.Signal.Request.Body = Library.Json.loads(Load);
                    except :
                        Body = Load.decode();
                        Parse = Library.Parse.parse_qs(Body);
                        if len(Parse) == 0 : Context.Signal.Request.Body = Body;
                        else : Context.Signal.Request.Body = {Key.strip() : Value[0].strip() if len(Value) == 1 else Value for Key , Value in Parse.items()};
                    finally :
                        if Context.Signal.Config.Journal is True : Context.Journal.put(Library.Simple(
                            Method = 'Websocket' ,
                            Type = 'Request' ,
                            Body = Context.Signal ,
                        ));
                        await Queue.put(Library.Copy.deepcopy(Context.Signal));
                else : break;
            await Queue.put(None);
            await Waiting;
        except ValueError as Error :
            try :
                Context.Signal.Response = dict(Code = Error.args[0]);
                await Self.Send(Context , Writer);
            except : Function.Trace(Context.Journal);
        except : Function.Trace(Context.Journal);
        finally : await Library.Asyncio.sleep(0);
    
    @classmethod
    async def Worker(Self , Queue:Library.Asyncio.Queue , Journal:Library.Processing.Queue , Writer:Library.Asyncio.StreamWriter) -> None :
        while True :
            Context = await Queue.get();
            if Context is None : break;
            await Self.Task(Library.Simple(
                Signal = Context ,
                Journal = Journal ,
            ) , Writer);
    
    @classmethod
    async def Task(Self , Context:Library.Simple , Writer:Library.Asyncio.StreamWriter) -> None :
        try :
            Context.Signal.Response = await Library.Asyncio.to_thread(Control.Business , Context);
            await Self.Send(Context , Writer);
        except :
            try :
                Context.Signal.Response = dict(Code = 503);
                await Self.Send(Context , Writer);
            except : pass;
            finally : Function.Trace(Context.Journal);
    
    @staticmethod
    async def Send(Context:Library.Simple , Writer:Library.Asyncio.StreamWriter) -> None :
        try :
            if Writer.is_closing() is False :
                Code = Context.Signal.Response.get('Code' , 200);
                Body = Context.Signal.Response.get('Body' , str());
                Response_Code = getattr(Const , f'Socket_{Code}' , Const.Socket_400);
                if all([
                    not Code == 200 ,
                    any([
                        Body == '' ,
                        Body is None ,
                        len(Body) == 0 ,
                    ]) ,
                ]) is True : Body = Response_Code;
                if Body is None : Body = Const.Socket_Empty.decode();
                if isinstance(Body , bytes) is True : Body = Body.decode();
                Data = Library.Json.dumps(dict(
                    Code = Code ,
                    Body = Body ,
                ));
                Header = bytearray();
                Header.append(0x81);
                Length = len(Data);
                if Length <= 125 : Header.append(Length);
                elif Length < 65535 :
                    Header.append(126);
                    Header += Library.Struct.pack(Const.Socket_H , Length);
                else :
                    Header.append(127);
                    Header += Library.Struct.pack(Const.Socket_Q , Length);
                Writer.write(Header + Data);
                await Writer.drain();
                if Context.Signal.Config.Journal is True : Context.Journal.put(Library.Simple(
                    Method = 'Websocket' ,
                    Type = 'Response' ,
                    Body = Context.Signal ,
                ));
        except : Function.Trace(Context.Journal);
        finally : await Library.Asyncio.sleep(0);
    