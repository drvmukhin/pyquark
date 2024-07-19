# pyquark
- v.0.2.4: Fixes error when trying to print "list" or "dict" objects with colored print methods
- v.0.3.1: Added class L (logging) based on pythin logging library. Allows console and file logging
- v.0.3.2: Allows to programmatically add <app_index> into application name, which allows to run multiple instances of the script writing into different log_files "<application_name>_<app_index>.log"
- v.0.3.4: Allows to log simultaneously into console and file and preserves color schema for the logging into console. Default level of the logger is set to DEBUG and can be decreased by setting debug attribute of the L class object to False. Logging to the console is enabled by default.  If debug attribute set to False logging to the console will continue at WARNING level. Logging to console can be disabled by setting log_to_console attribute to False. Logging to file disabled by default and can be enabled by setting log_to_file attribute to True. Setting debug attribute to False will decrease the logging level to file to INFO level.
- v.0.3.5: Use log_dir parameter of the __inti__ to define a custom logs directory
- v.0.3.6: @switch2 decorator (modification of the @switch) defined
- v.0.3.7: '__call__' name added to the list of functions names excluded from the logger prefix
- v.0.3.9: Added print_dict to print complex data structures in a more readable way
- v.0.3.10: Added switch_reverse_yesno decorator. Allows to switch the return value of the decorated function from Boolean to Yes/No string.