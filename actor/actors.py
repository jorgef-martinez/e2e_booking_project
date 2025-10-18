from typing import Any

class Actor:
    """
    Representa un usuario que interactúa con el sistema.
    Un actor tiene habilidades y puede realizar tareas.
    """
    def __init__(self, name: str):
        self.name = name
        self._abilities = {}

    def can(self, *abilities):
        """Dar al actor una o más habilidades."""
        for ability in abilities:
            self._abilities[ability.__class__.__name__] = ability
        return self
    
    def ability_to(self, ability_class: Any) -> Any:
        """Recuperar una habilidad por su clase."""
        return self._abilities.get(ability_class.__name__)

    def attempts_to(self, *tasks):
        """Realizar una o más tareas."""
        for task in tasks:
            task.perform_as(self)
        return self

    def asks_for(self, question: Any) -> Any:
        """Hacer una pregunta sobre el estado de la aplicación."""
        return question.answered_by(self)

    def __repr__(self) -> str:
        return f"Actor(name={self.name})"