import abc

class DAL(abc.ABC):
    @abc.abstractmethod
    def register_parish(parish_form):
        pass

    @abc.abstractmethod
    def register_parish_priest(parish_priest_form):
        pass

    @abc.abstractmethod
    def register_catechist(catechist_form):
        pass

    @abc.abstractmethod
    def register_catechizing(catechizing_form):
        pass