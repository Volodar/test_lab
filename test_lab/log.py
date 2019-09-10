

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
RESULT = 9

class Log(object):
    LEVEL = WARNING

    @staticmethod
    def debug(message, *args):
        Log.__log(DEBUG, message, *args)

    @staticmethod
    def info(message, *args):
        Log.__log(INFO, message, *args)

    @staticmethod
    def warning(message, *args):
        Log.__log(WARNING, message, *args)

    @staticmethod
    def error(message, *args):
        Log.__log(ERROR, message, *args)

    @staticmethod
    def result(message, *args):
        Log.__log(RESULT, message, *args)

    @staticmethod
    def __log(level, message, *args):
        tag = {
            DEBUG:   '[DEBUG]:   ',
            INFO:    '[INFO]:    ',
            WARNING: '[WARNING]: ',
            ERROR:   '[ERROR]:   ',
            RESULT:  '[RESULT]:  ',
        }[level]
        if level < Log.LEVEL:
            return
        if args:
            print(tag + message.format(*args))
        else:
            print(tag + message)

    @staticmethod
    def whitespace():
        print()


if __name__ == "__main__":
    Log.LEVEL = WARNING
    Log.debug('Some debug out [{}], [{}]', 123, 123)
    Log.info('Some info out [{}], [{}]', 123, 123)
    Log.warning('Some warning out [{}], [{}]', 123, 123)
    Log.error('Some error out [{}], [{}]', 123, 123)
    Log.error('Some error out')
    Log.error('Some error out {}')
