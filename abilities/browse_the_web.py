from playwright.sync_api import Page

class BrowseTheWeb:
    """
    Habilidad para navegar por la web usando Playwright.
    Esta clase contiene el objeto page de Playwright que el actor usará
    para interactuar con la aplicación web.
    """
    def __init__(self, page: Page):
        self.page = page

    @staticmethod
    def using(page: Page) -> "BrowseTheWeb":
        """
        Método factory para crear una instancia de esta habilidad.
        """
        return BrowseTheWeb(page)

    def __repr__(self) -> str:
        return "Navegar por la Web"