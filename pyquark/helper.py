import sys
import json
import unicodedata
import re
import os
import logging
import logging.handlers
from datetime import datetime
from threading import Thread
from typing import Optional


def target_directory(output_path: Optional[str] = None) -> str:
    """
    Function for determining target directory of a download.
    Returns an absolute path (if relative one given) or the current
    path (if none given). Makes directory if it does not exist.

    type output_path: str
        :rtype: str
    returns:
        An absolute directory path as a string.
    """
    if output_path:
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
    else:
        output_path = os.getcwd()
    os.makedirs(output_path, exist_ok=True)
    return output_path


""" Tips and Hints for basic color coding the output in console.
Usage of "\033[": This is to handle the console cursor. 
(https://cplusplus.com/forum/unices/36461/)
"""
cc = {
    'black': '30',
    'red': '31',
    'green': '32',
    'brown': '33',
    'blue': '34',
    'magenta': '35',
    'cyan': '36',
    'lightgray': '37'}

"""Usage Format: 
* 'm' character at the end of each of the following sentences is used as a 
stop character, where the system should stop and parse the \033[ syntax.
\033[0m - is the default color for the console
\033[0;#m - is the color of the text, where # is one of the codes mentioned above
\033[1m - makes text bold
\033[1;#m - makes colored text bold**
\033[2;#m - colors text according to # but a bit darker
\033[4;#m - colors text in # and underlines
\033[7;#m - colors the background according to #
\033[9;#m - colors text and strikes it
\033[A - moves cursor one line above (carfull: it does not erase the previously written line)
\033[B - moves cursor one line under
\033[C - moves cursor one spacing to the right
\033[D - moves cursor one spacing to the left
\033[E - don't know yet
\033[F - don't know yet
\033[2K - erases everything written on line before this.
"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[1;31;40m'
    RED = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def rstring(string):
    return "{}{}{}".format(bcolors.RED, string, bcolors.ENDC)


def gstring(string):
    return "{}{}{}".format(bcolors.OKGREEN, string, bcolors.ENDC)


def bstring(string):
    return "{}{}{}".format(bcolors.OKBLUE, string, bcolors.ENDC)


def ystring(string, **kwargs):
    return "{}{}{}".format(bcolors.WARNING, string, bcolors.ENDC)


def error_string(string):
    return "{}{}{}".format(bcolors.FAIL, string, bcolors.ENDC)


def gprint(string):
    print("{}{}{}".format(bcolors.OKGREEN, string, bcolors.ENDC))


def bprint(string):
    print("{}{}{}".format(bcolors.OKBLUE, string, bcolors.ENDC))


def yprint(string, **kwargs):
    if kwargs and kwargs.get('end') == "":
        print("{}{}{}".format(bcolors.WARNING, string, bcolors.ENDC), end="")
    else:
        print("{}{}{}".format(bcolors.WARNING, string, bcolors.ENDC))


def rprint(string):
    print("{}{}{}".format(bcolors.RED, string, bcolors.ENDC))


def print_error(string):
    print("{}{}{}".format(bcolors.FAIL, string, bcolors.ENDC))


def logs_prefix(*args, **kwargs):
    _func_ = ''
    if kwargs.get('cls'):
        _func_ += '[{}.'.format(kwargs['cls'].__name__)
    elif kwargs.get('self'):
        _func_ += '[{}.'.format(kwargs['self'].__class__.__name__)
    elif kwargs.get('classname'):
        _func_ += '[{}.'.format(kwargs['classname'])
    else:
        _func_ += '['

    frames = []
    i = 1 if not args or len(args) < 2 else args[1]
    imax = 3 if not args else args[0]
    memorized_name = None
    excludes = ('dispatch', 'view', 'func_wrapper', 'inner', '__init__')
    while True:
        name = str(sys._getframe(i).f_code.co_name)
        if type(name).__name__ == 'NoneType' or name == memorized_name or name in excludes:
            i += 1
            imax += 1
            continue
        if name == '<module>' or i == imax:
            break
        memorized_name = name
        frames.append(name)
        i += 1
    frames.reverse()

    for name in frames:
        _func_ += '{}.'.format(name)

    if kwargs.get('decorator'):
        _func_ += '{}]'.format(kwargs['decorator'])
    else:
        _func_ = _func_[:-1]
        _func_ += "]"
    offset = 2
    _func_ = _func_ + ' ' * offset
    return _func_


def json_export():
    data = []
    project_file = '/export.json'
    export_file = open(project_file, 'w')
    strLine = json.dumps(data)
    export_file.write(strLine)


def get_choice(choices, mychoice, allow_revers: bool = True):
    if not choices or choices.__class__.__name__ not in ('list', 'tuple', 'dict'):
        return None
    for choice in choices:
        if choice[0] == mychoice:
            return choice[1]
        elif choice[1] == mychoice and allow_revers:
            return choice[0]
        elif choice[1] == mychoice:
            return choice[1]
    return None


def get_index(mylist, value):
    for index, item in enumerate(mylist):
        if item == value:
            return index
    return None


def is_mac(mac_addr):
    mac_addr = str(mac_addr).lower().strip()
    if re.search(r"^[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}:[a-f\d]{1,2}$", mac_addr):
        return True
    else:
        return False


def switch(func):
    def func_wrapper(self, value, **kwargs):
        p = P(inst=self, decorator='switch', omit=True)
        cls = self.__class__
        ON = self.ON.lower() if getattr(self, 'ON') else 'yes'
        OFF = self.OFF.lower() if getattr(self, 'OFF') else 'no'
        attr_name = func.__name__.replace('set_', '')
        if value.__class__.__name__ == 'bool':
            pass
        elif value.lower() == ON:
            value = True
        elif value.lower() == OFF:
            value = False
        else:
            error = 'Error: wrong "switch" attribute (value = {}). {} or {} is expected.'
            p.rprint(error.format(value, ON, OFF))
            value = None
        if attr_name in cls.__dict__.keys() and value is not None:
            self.__setattr__(attr_name, value)
        return func(self, value, **kwargs)
    return func_wrapper


def clean_select_field(self, choices, forms, error_message):
    p = P(inst=self, omit=True)
    _func_name_ = str(sys._getframe(1).f_code.co_name)
    if 'clean_' not in _func_name_:
        raise forms.ValidationError("Wrong procedure")
    field_name = str(_func_name_).replace('clean_', '')
    field = str(self.cleaned_data.get(field_name))
    p.print("Cleaning {} parameter".format(field_name))
    if not field or field == '':
        p.print("Parameter {} not found in request. Skip cleaning.".format(field_name))
        return None
    if not get_choice(choices, field):
        p.rprint('Cleaning select-field "{}" Error '.format(field_name))
        raise forms.ValidationError(error_message)
    p.print("Parameter {0} cleaned: {0}={1}.".format(field_name, field))
    return field


def clean_switch_field(self, forms, error_message):
    p = P(inst=self, omit=True)
    _func_name_ = str(sys._getframe(1).f_code.co_name)
    if 'clean_' not in _func_name_:
        raise forms.ValidationError("Wrong procedure")
    field_name = str(_func_name_).replace('clean_', '')
    field = str(self.cleaned_data.get(field_name))
    p.print("Cleaning {} parameter".format(field_name))
    if not field:
        p.print("Parameter {} not found in request. Skip cleaning.".format(field_name))
        return None
    if field.lower() not in ('yes', 'no'):
        p.rprint('Cleaning switch-field "{}" Error '.format(field_name))
        raise forms.ValidationError(error_message)
    p.print("Parameter {0} cleaned: {0}={1}.".format(field_name, field))
    return field


def start_as_thread(func):
    _func_ = logs_prefix()

    def func_wrapper(*args, **kwargs):
        if kwargs:
            yprint(_func_ + ': starting {} as a thread'.format(func.__name__))
            return Thread(target=func, args=args, kwargs=kwargs).start()
        else:
            yprint(_func_ + ': starting {} as a thread'.format(func.__name__))
            return Thread(target=func, args=args).start()
    return func_wrapper


class P(object):
    FORMAT = '[{}] {}{}'

    def __init__(self, **kwargs):
        """
        Parameters:
            omit: skips regular print, but allows all colored print methods
            omit_all: skips all prints methods except rprint
            prefix: controls if data+method name to be added to prefix
        """
        self.omit = False
        self.omit_all = False
        if kwargs.get('omit'):
            self.omit = True
        if kwargs.get('omit_all'):
            self.omit = True
            self.omit_all = True
        if kwargs.get('native'):
            self.prefix = ''
        elif kwargs.get('inst'):
            self.prefix = logs_prefix(4, 2, self=kwargs['inst'], decorator=kwargs.get('decorator'))
        elif kwargs.get('cls'):
            self.prefix = logs_prefix(4, 2, cls=kwargs['cls'], decorator=kwargs.get('decorator'))
        else:
            self.prefix = logs_prefix(4, 2, decorator=kwargs.get('decorator'))

    def print(self, str_line, **kwargs):
        if self.omit:
            return
        print(self.FORMAT.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"), self.prefix, str_line), **kwargs)

    def rprint(self, str_line, **kwargs):
        rprint(self.FORMAT.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"), self.prefix, str_line))

    def yprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        yprint(self.FORMAT.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"), self.prefix, str_line), **kwargs)

    def bprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        bprint(self.FORMAT.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"), self.prefix, str_line))

    def gprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        gprint(self.FORMAT.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"), self.prefix, str_line))

    def print_error(self, errors: dict):
        prefix = '[{}] {}'.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"), self.prefix)
        for error_key, error_value in errors.items():
            if error_key not in ('error', 'source', 'params'):
                continue
            print_error("{}{}: {}".format(prefix, str(error_key).capitalize(), error_value))


class L(object):

    ERROR_FILE = "app_errors.log"
    APPLICATION_INDEX = ""
    LOG_DIR = target_directory("logs")
    FORMAT = '{}{}'
    DEFAULT_LOGGER_NAME = 'pyquark.sys'
    LOG_FORMAT = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)6s %(message)s', datefmt='%d/%b/%y %H:%M:%S')

    def __init__(self, 
                 application: str = DEFAULT_LOGGER_NAME,
                 debug: bool = True,
                 log_to_file: bool = False,
                 log_to_console: bool = True,
                 omit: bool = False, 
                 omit_all: bool = False,
                 native: bool = False,
                 decorator: str = "",
                 init: bool = False,
                 **kwargs):
        """
        Parameters:
            omit: skips regular print, but allows all colored print methods
            omit_all: skips all prints methods except rprint
            prefix: controls if data+method name to be added to prefix
        """
        self.omit = omit if not omit_all else omit_all
        self.omit_all = omit_all
        self.debug = debug
        self._log_file_name = ''
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        if native:
            self.prefix = ''
        elif kwargs.get('inst'):
            self.prefix = logs_prefix(4, 2, self=kwargs['inst'], decorator=decorator)
        elif kwargs.get('cls'):
            self.prefix = logs_prefix(4, 2, cls=kwargs['cls'], decorator=decorator)
        else:
            self.prefix = logs_prefix(4, 2, decorator=decorator)

        logger_name = f"{application}_{self.app_index()}" if self.app_index() else application
        con_logger_name = f"{logger_name}_"

        """ Define console logger: 
                Note: We are using separate loggers for console and file modes to allow colored records in console.
                Effectively we are sending a colored record to console logger and plain log record to the file logger.
        """
        if con_logger_name in logging.Logger.manager.loggerDict.keys() and not init:
            self.con_logger = logging.getLogger(con_logger_name)
        elif self.log_to_console:
            self.con_logger = logging.getLogger(con_logger_name)
            self.con_logger.setLevel(logging.DEBUG)  # Set's the root level for the logger. Handler can overwrite it
            """ Console handler """
            con_handler_level = logging.DEBUG if self.debug else logging.WARNING
            log_con_handler = logging.StreamHandler()
            log_con_handler.setFormatter(self.log_format)
            log_con_handler.setLevel(con_handler_level)  # NOTSET(0),DEBUG(10),INFO(20),WARNING(30),ERROR(40),CRITICAL(50)
            self.con_logger.addHandler(log_con_handler)
        else:
            self.con_logger = None

        """Define file logger"""

        if logger_name in logging.Logger.manager.loggerDict.keys() and not init:
            self.logger = logging.getLogger(logger_name)
        elif self.log_to_file:
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(logging.DEBUG)  # Set's the root level for the logger. Handler can overwrite it
            """ File handler """
            handler_level = logging.DEBUG if self.debug else logging.INFO
            self._log_file_name = f"{self.LOG_DIR}/{logger_name.lower()}.log"
            log_file_handler = logging.handlers.TimedRotatingFileHandler(filename=self._log_file_name,
                                                                         when='midnight',
                                                                         backupCount=30)
            log_file_handler.setFormatter(self.log_format)
            log_file_handler.setLevel(handler_level)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            self.logger.addHandler(log_file_handler)
        else:
            self.logger = None

    @property
    def log_format(self):
        return self.LOG_FORMAT

    @classmethod
    def app_index(cls):
        return cls.APPLICATION_INDEX

    @classmethod
    def set_app_index(cls, name: str):
        cls.APPLICATION_INDEX = name

    @property
    def log_file_name(self):
        if self._log_file_name:
            return self._log_file_name
        if self.logger:
            for handler in self.logger.handlers:
                if handler.__dict__.get('baseFilename'):
                    self._log_file_name = handler.__dict__['baseFilename']
                    return self._log_file_name
        return None

    def print(self, str_line, **kwargs):
        if self.omit:
            return
        if self.logger:
            self.logger.debug(self.FORMAT.format(self.prefix, str_line))
        if self.con_logger:
            self.con_logger.debug(self.FORMAT.format(self.prefix, str_line))

    def rprint(self, str_line, **kwargs):
        if self.logger:
            self.logger.warning(self.FORMAT.format(self.prefix, str_line))
        if self.con_logger:
            str_line = rstring(self.FORMAT.format(self.prefix, str_line))
            self.con_logger.warning(str_line)

    def yprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        if self.logger:
            self.logger.info(self.FORMAT.format(self.prefix, str_line))
        if self.con_logger:
            str_line = ystring(self.FORMAT.format(self.prefix, str_line))
            self.con_logger.info(str_line)

    def bprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        if self.logger:
            self.logger.info(self.FORMAT.format(self.prefix, str_line))

        if self.con_logger:
            str_line = bstring(self.FORMAT.format(self.prefix, str_line))
            self.con_logger.info(str_line)

    def gprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        if self.logger:
            self.logger.info(self.FORMAT.format(self.prefix, str_line))

        if self.con_logger:
            str_line = gstring(self.FORMAT.format(self.prefix, str_line))
            self.con_logger.info(str_line)

    def print_error(self, errors):
        if type(errors).__name__ == 'dict':
            for error_key, error_value in errors.items():
                if error_key not in ('error', 'source', 'params'):
                    continue
                if self.logger:
                    self.logger.error('{}{}: {}'.format(self.prefix, str(error_key).capitalize(), error_value))
                if self.con_logger:
                    str_line = error_string('{}{}: {}'.format(self.prefix, str(error_key).capitalize(), error_value))
                    self.con_logger.error(str_line)
        else:
            if self.logger:
                self.logger.error(self.FORMAT.format(self.prefix, errors))
            if self.con_logger:
                str_line = rstring(self.FORMAT.format(self.prefix, errors))
                self.con_logger.error(str_line)


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')


class Log(L):

    def __init__(self,
                 application: str = L.DEFAULT_LOGGER_NAME,
                 debug: bool = True,
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 omit: bool = False,
                 omit_all: bool = False,
                 native: bool = False,
                 decorator: str = "",
                 **kwargs):
        super(Log, self).__init__(application=application,
                                  debug=debug,
                                  omit=omit,
                                  omit_all=omit_all,
                                  native=native,
                                  decorator=decorator,
                                  log_to_file=log_to_file,
                                  log_to_console=log_to_console,
                                  **kwargs)


def main():
    test_dict = {
        "a": "AA",
        "b": "BB",
        "error": "Print my error"
    }
    print("==== Standard colored print methods ====")
    p = P(decorator="decorator")
    p.bprint(f"{test_dict}")
    p.gprint(f"{test_dict}")
    p.rprint(f"{test_dict}")
    p.yprint(f"{test_dict}")
    p.print_error(test_dict)

    print("\n==== Logs based on python logging. DEBUG is ON =====")
    p = Log(decorator="debug_is_on")
    p.print(f"Logger filename: {p.log_file_name}")
    p.print(f"Print dictionary: {test_dict}")
    p.bprint(f"Print dictionary: {test_dict}")
    p.gprint(f"Print dictionary: {test_dict}")
    p.rprint(f"Print dictionary: {test_dict}")
    p.yprint(f"Print dictionary: {test_dict}")
    p.print_error(test_dict)

    print("\n==== Logs based on python logging. DEBUG is OFF + logging to file ====")
    Log.set_app_index("sys")
    p = Log(application="Helper", debug=False, decorator="debug_is_off")
    p.rprint(f"Logger filename: {p.log_file_name}")
    p.print(f"print: Print dictionary: {test_dict}")
    p.bprint(f"bprint: Print dictionary: {test_dict}")
    p.gprint(f"gprint: Print dictionary: {test_dict}")
    p.rprint(f"rprint: Print dictionary: {test_dict}")
    p.yprint(f"yprint: Print dictionary: {test_dict}")
    p.print_error(test_dict)


if __name__ == "__main__":
    main()
