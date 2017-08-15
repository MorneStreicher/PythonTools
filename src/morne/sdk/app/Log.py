

class Log:
    _log = None

    def __init__(self):
        pass

    @staticmethod
    def _set_application_log(log):
        """
        Sets the main application log. Applications typically will not make use of this function.
        Args:
            log: The log instance
        Returns:
            Nothing
        """
        Log._log = log

    @staticmethod
    def log():
        """
        Returns:
            A handle to the main application log instance.
        """
        return Log._log