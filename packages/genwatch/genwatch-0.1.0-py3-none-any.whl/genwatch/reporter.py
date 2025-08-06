import logging
import inspect
from typing import Generator

class _ProxyReporter:
    def __init__(self, gen, logger, attrs):
        self._gen = gen
        self.__name__, self.__qualname__ = gen.__name__, gen.__qualname__
        self._logger = logger 
        self._attrs = attrs

    
    def __iter__(self):
        class_name = self.__class__.__name__
        self._logger.info(self.__name__)
        i = None
        entered_sub_gen = False
        f_locals = None
        while True:
            try:
                result = self._gen.send(i)
                i = yield result 
            except StopIteration as e: # PEP 479 raising StopIteration within genrators raise RuntimeError
                return e.value
            
            except GeneratorExit as e:
                self._gen.close()
                self._logger.info(f'{self._gen.__name__!r} closed.')
                raise
            
            except Exception as e:
                try:
                    result = self._gen.throw(e)
                    i = yield result
                    self._logger.info(f"{self.__name__!r} recovered from exception `.throw`: exception as {e!r}")
                except StopIteration as ex:
                    return ex.value
            
                
            else:
                if not entered_sub_gen and self._gen.gi_yieldfrom is not None:
                    # assign that there is a subgenrator delgation
                    entered_sub_gen = True 
                    # to get correct subgenrator name instead of it being ProxyReporter.__iter__
                    # we check if the `sub genrator` name is ProxyReporter.__iter__
                    # if yes:
                    #        it means the subgenrator is decorated with @Reporter. so we read the value from gi_frame.f_locals. ===> This is equal to self._gen.gi_yieldfrom.gi_frame.f_locals['self']  `self`
                    # else:
                    #       it means the subgnerator is not decorated with @Reporter. so we read the name directly.
                    if not inspect.isgenerator(self._gen.gi_yieldfrom):
                        sub_gen_name = self._gen.gi_yieldfrom.__class__.__name__
                        self._logger.info(f'Yielding from iterator: {sub_gen_name}')
                    else:
                        sub_gen_name = self._gen.gi_yieldfrom.gi_frame.f_locals['self']._gen.__name__ if self._gen.gi_yieldfrom.gi_code.co_qualname == f'{class_name}.__iter__' else self._gen.gi_yieldfrom.__name__
                        self._logger.info(f'Entered subgenerator: {sub_gen_name}')
                    
                
                if entered_sub_gen and self._gen.gi_yieldfrom is None:
                    self._logger.info(f'Exited subgenrator.')
                    entered_sub_gen = False
                    sub_gen_name = None
                    f_locals = None
                
                if entered_sub_gen:
                    # to get correct subgenrator name instead of it being ProxyReporter.__iter__
                    # we check if the `sub genrator` name is ProxyReporter.__iter__
                    # if yes:
                    #        it means the subgenrator is decorated with @Reporter. so we read the value from gi_frame.f_locals. ===> This is equal to self._gen.gi_yieldfrom.gi_frame.f_locals['self']  `self`
                    # else:
                    #       it means the subgnerator is not decorated with @Reporter. so we read f_locals directly.
                    if not inspect.isgenerator(self._gen.gi_yieldfrom):
                        self._logger.info(f'delegated to a iterator do has no locals')
                    else:
                        f_locals = self._gen.gi_yieldfrom.gi_frame.f_locals['self']._gen.gi_frame.f_locals if self._gen.gi_yieldfrom.gi_code.co_qualname  == f'{class_name}.__iter__' else self._gen.gi_yieldfrom.gi_frame.f_locals
                        self._logger.info(f'Locals of {sub_gen_name!r}: {f_locals}')

                self._logger.info({
                    attr: getattr(self._gen,attr) for attr in self._attrs if attr != 'gi_yieldfrom'
                }|{
                    "gi_yieldfrom": self._gen.gi_yieldfrom if not inspect.isgenerator(self._gen.gi_yieldfrom) else \
                        (self._gen.gi_yieldfrom.gi_frame.f_locals['self']._gen if entered_sub_gen and (self._gen.gi_yieldfrom.gi_code.co_qualname  == f'{class_name}.__iter__') else  self._gen.gi_yieldfrom)
                })
                

class Reporter:
    """
    This calls helps trace genrators internals.
    """
    def __new__(cls, *args, **kwargs):
        # Check if the function decorated `isgenerator`
        if args:
            func, = args
        else:
            func = kwargs.get('func')
        if func is not None and not inspect.isgeneratorfunction(func):
            raise TypeError(f'decorated object must be generator')
        return super().__new__(cls)
    def __init__(self, func = None, *,logger: logging.Logger|None = None):
        """
        func(function):         is generator function.
        logger(logging.Logger): is logger which will report generation created from `func` internals. 
                                if no logger is passed then uses default root logger and emits to StreamHandler

        """
        self._func = func
        self.__name__, self.__qualname__ = (func.__name__, func.__qualname__) if func is not None else [""]*2
        self.logger = logger or self._get_logger()
            
    
    def _get_logger(self):
        logger = logging.getLogger(self.__name__)
        logger.setLevel(logging.DEBUG)
        strm_hdlr = logging.StreamHandler()
        strm_hdlr.setLevel(logging.DEBUG)
        strm_hdlr.setFormatter(logging.Formatter(fmt="[%(asctime)s]: [%(name)s]: [%(funcName)s]: [%(lineno)d]: [%(msg)s]"))
        if not logger.handlers:
            logger.addHandler(strm_hdlr)
        return logger
    
    def __call__(self,*args,**kwargs):
        """
        This will create the generator from `func`
        """
        if self._func is None:
            self = self.__class__(func = args[0] if args else kwargs['func'], logger = self.logger) 
            return self
        
        gen: Generator = self._func(*args,**kwargs) 
        attrs = list(filter(
            lambda x: x.startswith('gi'), dir(gen)
        )) 
        proxy_obj = _ProxyReporter(gen, self.logger, attrs)
        return iter(proxy_obj)
    