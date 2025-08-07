from collections import OrderedDict


__all__ = 'Registry', 'EntryRegistry',


class Registry(OrderedDict):
    def add(self, key, value):
        assert key not in self, f'{key} already registered.'

        self[key] = value

    register = add


class EntryRegistry(Registry):
    def transform_input(self, entry):
        raise NotImplementedError()

    def add(self, entry):
        key, value = self.transform_input(entry)
        return super().add(key, value)

    register = add
