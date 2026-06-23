import asyncio
import threading

from typing_extensions import Self



class AsyncManager:
     
     def __init__(self) -> None:
          self.loop = None
          self.thread = None
          self.is_running_loop = False
     
     def __enter__(self) -> Self:
          if self.is_running_loop is False:
               try:
                    running_loop = asyncio.get_running_loop()
               except RuntimeError:
                    self.__create_loop_in_thread()
               else:
                    self.__close_thread_event_loop()
                    self.loop = running_loop
                    self.is_running_loop = True
          return self
     
     def __exit__(self, exc_type, exc, tb) -> None:
          pass
     
     def __create_loop_in_thread(self) -> None:
          self.loop = asyncio.new_event_loop()
          self.thread = threading.Thread(
               target=self.__set_thread_loop, 
               args=(self.loop,), 
               daemon=True
          )
          self.thread.start()
     
     def __set_thread_loop(self, loop: asyncio.AbstractEventLoop) -> None:
          try:
               asyncio.set_event_loop(loop)
               loop.run_forever()
          finally:
               loop.close()
               
     def __close_thread_event_loop(self) -> None:
          if self.thread is not None:
               self.loop.call_soon_threadsafe(self.loop.stop)
               self.thread.join()
               self.thread = None
               self.loop = None
          
     def run_coroutine(self, coro) -> None:
          asyncio.run_coroutine_threadsafe(coro, self.loop)
          
        
async_manager = AsyncManager()