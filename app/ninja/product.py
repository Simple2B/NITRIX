class NinjaProduct(object):
    """Ninja Product entity
    """
    def __init__(self, data={}):
        self.__data_keys = [k for k in data]
        for k in data:
            self.__setattr__(k, data[k])

    def to_dict(self):
        return {k: self.__getattribute__(k) for k in self.__data_keys}
