import TimerThread
import Timer

#
# We have a single thread responsible for placing expired timers on their respective queues.
#  We create this thread when the module is initialized
#

_timerThread = TimerThread.TimerThread()
_timerThread.start()

#
# Keep a global static reference to this timer thread. Intended to be used by the SDK internally.
#

Timer.Timer._timerThread = _timerThread






