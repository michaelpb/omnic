'''
SingletonManager is what provides the 'omnic.singletons' functionality,
instantiating singletons as needed.
'''


class SingletonManager(object):
    def __init__(self):
        self.singletons = {}
        self.singleton_classes = {}

    def __getattr__(self, name):
        if name not in self.singleton_classes:
            raise AttributeError(name)

        if name in self.singletons:
            return self.singletons[name]

        # New (and only) instance of this singleton
        self.singletons[name] = self.singleton_classes[name]()
        return self.singletons[name]

    def register(self, name, cls):
        self.singleton_classes[name] = cls
        return cls

    def clear(self, name):
        del self.singleton_classes[name]
