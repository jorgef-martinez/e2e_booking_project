import pytest
from playwright.sync_api import Page, sync_playwright
from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb

@pytest.fixture(scope="function")
def browser_page():
    """
    Fixture que maneja el ciclo de vida del browser y page de Playwright.
    """
    playwright = sync_playwright().start()
    
    browser = playwright.chromium.launch(
        headless=False, 
        slow_mo=500
    )
    
    context = browser.new_context(
        viewport={"width": 1496, "height": 864},
        ignore_https_errors=True
    )
    
    # Configurar timeout global
    context.set_default_timeout(15000)
    context.set_default_navigation_timeout(30000)
    
    page = context.new_page()
    
    yield page
    
    # Cerrar todo adecuadamente
    context.close()
    browser.close()
    playwright.stop()

@pytest.fixture(scope="function")
def web_actor(browser_page: Page) -> Actor:
    """
    Fixture que crea un Actor con la habilidad de navegar por la web.
    """
    the_actor = Actor(name="Automator")
    the_actor.can(BrowseTheWeb.using(browser_page))
    return the_actor

@pytest.fixture(scope="function")
def test_context(request):
    """
    Fixture para compartir contexto entre steps del scenario.
    """
    class Context:
        def __init__(self):
            self.destination = None
            self.user_data = {}
    
    return Context()