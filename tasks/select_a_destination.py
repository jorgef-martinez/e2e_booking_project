from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb
from tasks.select_dates import SelectDates
import time

class SelectADestination:
    def __init__(self, adults: str, children: str, departing: str, returning: str):
        self.adults = adults
        self.children = children
        self.departing = departing
        self.returning = returning

    @staticmethod
    def for_passengers(adults: str, children: str, departing: str, returning: str) -> "SelectADestination":
        return SelectADestination(adults, children, departing, returning)

    def perform_as(self, actor: Actor):
        page = actor.ability_to(BrowseTheWeb).page
        
        # Primero seleccionar las fechas
        actor.attempts_to(
            SelectDates.for_trip(departing=self.departing, returning=self.returning)
        )
        
        # Esperar a que la página esté lista después de seleccionar fechas
        time.sleep(2)
        
        # Seleccionar adultos
        self._select_passenger_count(page, self.adults, dropdown_index=0, passenger_type="adultos")
        
        # Esperar entre selecciones
        time.sleep(1)
        
        # Seleccionar children  
        self._select_passenger_count(page, self.children, dropdown_index=1, passenger_type="niños")

        # Click el botón principal para proceder
        page.get_by_role("button", name="Select Destination").click()

    def _select_passenger_count(self, page, count: str, dropdown_index: int, passenger_type: str):
        """Selecciona la cantidad de pasajeros de forma robusta"""
        
        # Localizar todos los dropdowns
        dropdowns = page.locator('div[data-react-toolbox="dropdown"]')
        
        if dropdowns.count() <= dropdown_index:
            return False
        
        target_dropdown = dropdowns.nth(dropdown_index)
        
        # Estrategia 1: Intentar abrir el dropdown
        if not self._open_dropdown_safely(page, target_dropdown, passenger_type):
            return False
        
        # Estrategia 2: Buscar y seleccionar la opción
        option_selected = self._select_dropdown_option(page, count, passenger_type)
        
        return option_selected

    def _open_dropdown_safely(self, page, dropdown, passenger_type: str):
        """Abre el dropdown de forma segura"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Verificar que el dropdown esté visible
                if not dropdown.is_visible():
                    continue
                
                # Hacer click en el dropdown
                dropdown.click(timeout=5000)
                time.sleep(1)
                
                # Verificar si el dropdown se abrió (buscar las opciones)
                options = page.locator('ul.theme__values___1jS4g li')
                if options.count() > 0:
                    return True
                    
            except Exception:
                # Intentar cerrar cualquier dropdown abierto
                page.keyboard.press("Escape")
                time.sleep(1)
        
        return False

    def _select_dropdown_option(self, page, target_value: str, passenger_type: str):
        """Selecciona una opción del dropdown"""
        # Buscar todas las opciones disponibles
        options = page.locator('ul.theme__values___1jS4g li')
        option_count = options.count()
        
        if option_count == 0:
            return False
        
        # Estrategia 1: Buscar por texto exacto
        for i in range(option_count):
            option = options.nth(i)
            option_text = option.text_content().strip()
            
            if option_text == target_value:
                try:
                    # Verificar que la opción esté visible antes de hacer click
                    if option.is_visible():
                        option.click(timeout=5000)
                        return True
                except Exception:
                    pass
        
        # Estrategia 2: Buscar por texto que contenga el valor
        for i in range(option_count):
            option = options.nth(i)
            option_text = option.text_content().strip()
            
            if target_value in option_text:
                try:
                    if option.is_visible():
                        option.click(timeout=5000)
                        return True
                except Exception:
                    pass
        
        # Estrategia 3: Seleccionar la primera opción VISIBLE como fallback
        visible_options = []
        for i in range(option_count):
            option = options.nth(i)
            if option.is_visible():
                visible_options.append((i, option.text_content().strip()))
        
        if visible_options:
            first_visible_index, _ = visible_options[0]
            try:
                options.nth(first_visible_index).click(timeout=5000)
                return True
            except Exception:
                pass
        
        return False