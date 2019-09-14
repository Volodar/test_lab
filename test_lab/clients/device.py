

class Device(object):
    def __init__(self):
        self.name = 'Unknown Device'
        self.ip = None
        self.identifier = None
        self.app_installed = False

    def is_remote(self):
        return self.ip is not None

    def is_usb(self):
        return self.ip is None and self.identifier is not None

    def get_human_name(self):
        name = self.name
        if self.identifier:
            name += ' id: [%s]' % self.identifier
        if self.ip:
            name += ' ip: [%s]' % self.ip
        return name
