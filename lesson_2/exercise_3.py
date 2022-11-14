class PortDescriptor:

    def __init__(self, default=7777):
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.my_attr, self.default)

    def __set__(self, instance, value):
        if value < 1024 or value > 65535:
            raise ValueError
        instance.__dict__[self.my_attr] = value

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr