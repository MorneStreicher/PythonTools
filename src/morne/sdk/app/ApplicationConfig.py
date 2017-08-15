import ConfigParser
import string
import os


class ApplicationConfig:
    """
    A utility class to wrap an application's Config.ini file.
    """

    def __init__(self, filename=None, base_config={}):
        """
        Constructor.
        Args:
            filename: The application configuration filename.
            base_config: A dictionary of application-defined configuration values.
        Returns:
            Nothing
        """
        self._config_filename = filename
        self._base_config = base_config
        self._config = base_config.copy()
        if filename is not None:
            self._load_config()

    def _load_config(self):
        if not os.path.exists(self._config_filename):
            raise Exception("Config file name [%s] could not be read." % self._config_filename)
        config = self._base_config.copy()
        cp = ConfigParser.ConfigParser()
        cp.read(self._config_filename)
        for sec in cp.sections():
            name = string.lower(sec)
            for opt in cp.options(sec):
                config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
        self._config = config

    def config(self):
        """
        Returns:
            A dictionary of all application configuration values.
        """
        return self._config

    def get_application_setting(self, name, default_value=None):
        import morne.sdk.app.Application
        setting_name = "application:%s.%s" % \
                       (morne.sdk.app.Application.Application.instance.get_application_name().lower(), name.lower())
        if setting_name in self.config():
            return self.config()[setting_name]
        else:
            return default_value


