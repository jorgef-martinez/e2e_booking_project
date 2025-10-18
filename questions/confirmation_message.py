from playwright.sync_api import expect
from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb
import time

class ConfirmationMessage:
    def __init__(self, expected_message: str):
        self.expected_message = expected_message

    @staticmethod
    def displays(expected_message: str) -> "ConfirmationMessage":
        return ConfirmationMessage(expected_message)

    def answered_by(self, actor: Actor):
        page = actor.ability_to(BrowseTheWeb).page
        
        # Esperar un poco antes de buscar
        time.sleep(2)
        
        # Múltiples estrategias para encontrar el mensaje
        confirmation_locator = page.locator(f"text='{self.expected_message}'")
        
        # Intentar la verificación principal
        try:
            expect(confirmation_locator).to_be_visible(timeout=10000)
            return True
        except Exception:
            return False