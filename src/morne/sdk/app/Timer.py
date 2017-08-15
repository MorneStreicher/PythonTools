import datetime
import functools

from morne.sdk.app.Event import Event


class Timer(Event):
    def __init__(self, expires, queue, reference):
        Event.__init__(self)
        self.expires = expires
        self.queue = queue
        self.reference = reference
        self._stopped = False
        Timer._timerThread.add(self)

    def stop(self):
        self._stopped = True

    def is_stopped(self):
        return self._stopped

    def __str__(self):
        return "<Timer Event: reference = %s; expires = %s>" % (self.reference, self.expires)

    @staticmethod
    def create_timer(queue, time_ms, reference):
        if queue is None:
            from morne.sdk.app.Application import Application
            if not Application.instance:
                raise Exception("Application.instance is not set. Has the application been started?")
            queue = Application.instance.queue()

        expires = datetime.datetime.utcnow() + datetime.timedelta(milliseconds=time_ms)
        timer = Timer(expires, queue, reference)
        return timer

    @staticmethod
    def create_callback(queue, time_ms, func, *args, **keywords):
        reference = Callback(func, *args, **keywords)
        return Timer.create_timer(queue, time_ms, reference)


class Callback:
    def __init__(self, func, *args, **keywords):
        self._callback = functools.partial(func, *args, **keywords)

    def callback(self):
        return self._callback

    def __str__(self):
        return "<Callback reference: %s>" % repr(self._callback)
