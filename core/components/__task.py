import threading
from tkinter import Event

class BackgroundTask:
    def __init__(self, taskFuncPointer):
        self.__taskFuncPointer_ = taskFuncPointer
        self.__workerThread_ = None
        self.__isRunning_ = False

    def taskFuncPointer(self):
        return self.__taskFuncPointer_

    def isRunning(self):
        return self.__isRunning_ and self.__workerThread_.isAlive()

    def start(self, *args):
        if not self.__isRunning_:
            self.__isRunning_ = True
            self.__workerThread_ = self.WorkerThread(self, args)
            self.__workerThread_.start()

    def stop(self):
        self.__isRunning_ = False

    class WorkerThread(threading.Thread):
        def __init__(self, bgTask, args):
            threading.Thread.__init__(self)
            self.__bgTask_ = bgTask
            self.__args_ = [x for x in args if not isinstance(x, Event)]

        def run(self):
            try:
                self.__bgTask_.taskFuncPointer()(
                    self.__bgTask_.isRunning, *self.__args_
                )
            except Exception as e:
                print(repr(e))
            self.__bgTask_.stop()
