import sys
import json
import unicodedata
import re
import os
from datetime import datetime
from threading import Thread
from typing import Optional


def target_directory(output_path: Optional[str] = None) -> str:
    """
    Function for determining target directory of a download.
    Returns an absolute path (if relative one given) or the current
    path (if none given). Makes directory if it does not exist.

    :type output_path: str
        :rtype: str
    :returns:
        An absolute directory path as a string.
    """
    if output_path:
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
    else:
        output_path = os.getcwd()
    os.makedirs(output_path, exist_ok=True)
    return output_path


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[1;31;40m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def gprint(string):
    string = "{}" + string + "{}"
    print(string.format(bcolors.OKGREEN, bcolors.ENDC))


def bprint(string):
    string = "{}" + string + "{}"
    print(string.format(bcolors.OKBLUE, bcolors.ENDC))


def yprint(string, **kwargs):
    string = "{}" + string + "{}"
    if kwargs and kwargs.get('end') == "":
        print(string.format(bcolors.WARNING, bcolors.ENDC), end=kwargs['end'])
    else:
        print(string.format(bcolors.WARNING, bcolors.ENDC))


def rprint(string):
    string = "{}" + string + "{}"
    print(string.format(bcolors.FAIL, bcolors.ENDC))


def logs_prefix(*args, **kwargs):
    # _func_ = '[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S"))
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
    while True:
        name = str(sys._getframe(i).f_code.co_name)
        if 'func_wrapper' in name or name == memorized_name:
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
    data = json.loads(strLine)


def get_choice(CHOICES, mychoice, allow_revers: bool = True):
    if not CHOICES or CHOICES.__class__.__name__ not in ('list', 'tuple', 'dict'):
        return None
    for choice in CHOICES:
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

    def __init__(self, **kwargs):
        """
        Parameters:
            omit: skips regular print, but allows all colored print methods
            omitall: skips all prints methods except rprint
            prefix: controls if data+method name to be added to prefix
        """
        self.omit = False
        self.omit_all = False
        if kwargs.get('omit'):
            self.omit = True
        if kwargs.get('omitall'):
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
        print('[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S")) + self.prefix + str_line, **kwargs)

    def rprint(self, str_line, **kwargs):
        rprint('[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S")) + self.prefix + str_line)

    def yprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        yprint('[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S")) + self.prefix + str_line, **kwargs)

    def bprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        bprint('[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S")) + self.prefix + str_line)

    def gprint(self, str_line, **kwargs):
        if self.omit_all:
            return
        gprint('[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S")) + self.prefix + str_line)

    def rprint_error(self, errors: dict):
        prefix = '[{}] '.format(datetime.now().strftime("%d/%b/%Y %H:%M:%S")) + self.prefix
        for error_key, error_value in errors.items():
            if error_key not in ('error', 'source', 'params'):
                continue
            f_error_value = f"{error_value}"
            if type(error_value).__name__ not in ('str', 'int'):
                print(prefix + str(error_key).capitalize() + ": " + f_error_value)
            else:
                rprint(prefix + str(error_key).capitalize() + ": " + f_error_value)


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
