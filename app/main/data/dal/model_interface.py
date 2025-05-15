import abc

class ModelInterface(abc.ABC):
    @abc.abstractmethod
    def register_from_form(self, form):
        """Register a model from a form."""
        pass

    @abc.abstractmethod
    def update_from_form(self, form):
        """Update a model from a form."""
        pass
    
    @abc.abstractmethod
    def delete(self):
        """Delete a model."""
        pass
    
    @abc.abstractmethod
    def get_by_id(self, id):
        """Get a model by its ID."""
        pass
    
    @abc.abstractmethod
    def get_all(self):
        """Get all models."""
        pass