import QueueExecuter


class AppQueueExecuter(QueueExecuter.QueueExecuter):
    """
    An queue executer, delegating event handling to an Application instance
    """
    def __init__(self, name, queue, application):
        QueueExecuter.QueueExecuter.__init__(self, name, queue)
        self.application = application

    def process_timer_event(self, timer):
        self.application.process_timer_event(timer)

    def process_connect_event(self, event):
        self.application.process_connect_event(event)

    def process_disconnect_event(self, event):
        self.application.process_disconnect_event(event)

    def process_data_event(self, event):
        self.application.process_data_event(event)

    def process_other_event(self, event):
        self.application.process_other_event(event)

