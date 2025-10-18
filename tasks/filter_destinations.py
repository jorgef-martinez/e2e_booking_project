from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb
import time

class FilterDestinations:
    def __init__(self, max_price: str):
        self.max_price = int(max_price)

    @staticmethod
    def by_price(max_price: str) -> "FilterDestinations":
        return FilterDestinations(max_price)

    def perform_as(self, actor: Actor):
        page = actor.ability_to(BrowseTheWeb).page
        
        # Cargar todos los destinos disponibles
        self._load_all_destinations(page)
        
        # Interactuar con el slider de precio
        self._adjust_price_slider(page)

    def _load_all_destinations(self, page):
        """Carga todos los destinos disponibles"""
        load_more_button = page.get_by_role("button", name="Load more")
        max_clicks = 5
        clicks_done = 0
        
        while clicks_done < max_clicks:
            # Verificar si el botón está visible y no está deshabilitado
            if load_more_button.is_visible():
                # Verificar si el botón está deshabilitado
                is_disabled = load_more_button.get_attribute("disabled")
                if is_disabled is not None:
                    break
                
                try:
                    load_more_button.click(timeout=3000)
                    clicks_done += 1
                    time.sleep(2)
                except Exception:
                    break
            else:
                break

    def _adjust_price_slider(self, page):
        """Ajusta el slider de precio de forma robusta"""
        
        # Estrategia 1: Buscar input de texto del slider
        slider_input = page.locator('div[data-react-toolbox="slider"] input[type="text"]')
        
        if slider_input.count() > 0 and slider_input.is_visible():
            try:
                # Limpiar y establecer el valor directamente
                slider_input.fill("")
                slider_input.fill(str(self.max_price))
                slider_input.press("Enter")
                time.sleep(2)
                return
            except Exception:
                pass
        
        # Estrategia 2: Buscar el slider handle
        slider_handle = page.locator('div[data-react-toolbox="slider"] div[role="slider"]')
        
        if slider_handle.count() > 0 and slider_handle.is_visible():
            try:
                # Obtener propiedades del slider
                min_price = int(slider_handle.get_attribute("aria-valuemin") or "0")
                max_price_possible = int(slider_handle.get_attribute("aria-valuemax") or "1000")
                
                # Asegurar que el precio objetivo esté en rango
                target_price = min(max(self.max_price, min_price), max_price_possible)
                
                # Hacer click en el slider para enfocar
                slider_handle.click()
                
                # Usar teclas para ajustar (fallback)
                current_price = int(slider_handle.get_attribute("aria-valuenow") or "0")
                if target_price > current_price:
                    # Presionar flecha derecha para aumentar
                    for _ in range(min(10, target_price - current_price)):
                        page.keyboard.press("ArrowRight")
                        time.sleep(0.1)
                else:
                    # Presionar flecha izquierda para disminuir
                    for _ in range(min(10, current_price - target_price)):
                        page.keyboard.press("ArrowLeft")
                        time.sleep(0.1)
                
                time.sleep(2)
                return
            except Exception:
                pass