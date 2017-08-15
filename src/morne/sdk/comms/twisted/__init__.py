import ReactorThread, ReactorCaller

def __start():
    if not ReactorThread.ReactorThread.__started:
        ReactorThread.ReactorThread.__started = True
        ReactorThread.ReactorThread().start()

    if not ReactorCaller.ReactorCaller.__started:
        ReactorCaller.ReactorCaller.__started = True
        ReactorCaller.ReactorCaller().start()