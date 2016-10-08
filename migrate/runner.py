"""
Defines interface for migration runner object.
Also provides default implementation.
"""


class BaseRunner:
    """
    Abstract class which defines API.
    All runners must inherit from this class.
    Also defines methods for some logic which is
    not suggested to modify.
    """
    def create(self):
        raise NotImplementedError()

    def perform(self):
        raise NotImplementedError()

    def show(self):
        raise NotImplementedError()


class DefaultRunner(BaseRunner):
    """
    Provides default implementation of migration runner.
    It can be substituted with user-created one.
    """
    pass
