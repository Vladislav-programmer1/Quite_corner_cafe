class BaseModelClass:
    __attributes = ()
    __action_dict: dict[str, tuple[str, str]] = dict()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value if value is not None else getattr(self, key))

    @property
    def attributes(self):
        return self.__attributes
