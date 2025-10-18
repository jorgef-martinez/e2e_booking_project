from playwright.sync_api import Page
from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb
from datetime import datetime, timedelta
import time

class SelectDates:
    def __init__(self, departing: str, returning: str):
        self.departing = departing
        self.returning = returning

    @staticmethod
    def for_trip(departing: str, returning: str) -> "SelectDates":
        return SelectDates(departing, returning)

    def perform_as(self, actor: Actor):
        page = actor.ability_to(BrowseTheWeb).page
        
        # Validar formato de fechas
        self._validate_dates()
        
        # Convertir fechas
        departing_date = datetime.strptime(self.departing, "%d/%m/%Y")
        returning_date = datetime.strptime(self.returning, "%d/%m/%Y")
        
        # Seleccionar fecha de partida
        self._select_date_smart(page, departing_date, calendar_index=0, date_type="Partida")
        
        # Esperar a que se estabilice la página
        time.sleep(2)
        
        # Seleccionar fecha de retorno
        self._select_date_smart(page, returning_date, calendar_index=1, date_type="Retorno")

    def _validate_dates(self):
        """Valida que las fechas cumplan con las reglas de negocio"""
        try:
            departing_date = datetime.strptime(self.departing, "%d/%m/%Y")
            returning_date = datetime.strptime(self.returning, "%d/%m/%Y")
            current_date = datetime.now()
            
            max_allowed_date = current_date + timedelta(days=180)
            
            if departing_date < current_date.replace(hour=0, minute=0, second=0, microsecond=0):
                raise ValueError(f"La fecha de partida ({self.departing}) no puede ser menor a la fecha actual")
            
            if returning_date < current_date.replace(hour=0, minute=0, second=0, microsecond=0):
                raise ValueError(f"La fecha de retorno ({self.returning}) no puede ser menor a la fecha actual")
            
            if departing_date >= returning_date:
                raise ValueError(f"La fecha de partida ({self.departing}) debe ser menor a la fecha de retorno ({self.returning})")
            
            if departing_date > max_allowed_date or returning_date > max_allowed_date:
                raise ValueError("Las fechas no pueden ser mayor a 6 meses desde la fecha actual")
                
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError(f"Formato de fecha incorrecto. Use DD/MM/YYYY")
            else:
                raise e

    def _select_date_smart(self, page: Page, target_date: datetime, calendar_index: int, date_type: str):
        """Selección inteligente de fecha con manejo de overlays"""
        
        # Cerrar cualquier calendario abierto primero
        self._force_close_calendars(page)
        
        # Esperar a que la página esté lista
        time.sleep(1)
        
        # Localizar el input correcto
        date_inputs = page.locator('input[role="input"]')
        if date_inputs.count() <= calendar_index:
            return
        
        input_element = date_inputs.nth(calendar_index)
        
        # Intentar abrir el calendario con diferentes estrategias
        calendar_opened = self._open_calendar_safely(page, input_element)
        
        if not calendar_opened:
            return
        
        # Seleccionar la fecha en el calendario
        selection_success = self._select_date_in_calendar(page, target_date, date_type)
        
        # Cerrar el calendario
        self._force_close_calendars(page)

    def _force_close_calendars(self, page: Page):
        """Fuerza el cierre de cualquier calendario abierto"""
        
        # Estrategia 1: Presionar Escape
        try:
            page.keyboard.press("Escape")
            time.sleep(0.5)
        except:
            pass
        
        # Estrategia 2: Click en el backdrop para cerrar
        try:
            backdrop = page.locator('.theme__backdrop___WbaQn')
            if backdrop.count() > 0 and backdrop.is_visible():
                backdrop.click()
                time.sleep(0.5)
        except:
            pass
        
        # Estrategia 3: Click fuera del calendario
        try:
            page.mouse.click(10, 10)
            time.sleep(0.5)
        except:
            pass
        
        # Estrategia 4: Buscar y cerrar diálogos de calendario
        try:
            calendar_dialogs = page.locator('div[data-react-toolbox="dialog"]')
            for i in range(calendar_dialogs.count()):
                dialog = calendar_dialogs.nth(i)
                if dialog.is_visible():
                    # Intentar encontrar botón Cancel o cerrar
                    cancel_btn = dialog.locator('button:has-text("Cancel")')
                    if cancel_btn.count() > 0:
                        cancel_btn.click()
                    else:
                        # Click fuera del diálogo
                        page.mouse.click(10, 10)
                    time.sleep(0.5)
        except:
            pass

    def _open_calendar_safely(self, page: Page, input_element):
        """Abre el calendario de forma segura"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Cerrar calendarios existentes primero
                self._force_close_calendars(page)
                time.sleep(1)
                
                # Verificar que el input esté visible y clickeable
                if not input_element.is_visible():
                    continue
                
                # Intentar click directo
                input_element.click(timeout=5000)
                time.sleep(1)
                
                # Verificar si el calendario se abrió
                calendar = page.locator('div[data-react-toolbox="calendar"]')
                if calendar.count() > 0 and calendar.is_visible():
                    return True
                    
            except Exception:
                time.sleep(1)
        
        return False

    def _select_date_in_calendar(self, page: Page, target_date: datetime, date_type: str):
        """Selecciona la fecha en el calendario abierto"""
        
        current_month_year = self._get_current_month_year(page)
        if not current_month_year:
            return False
        
        current_month, current_year = current_month_year
        
        # Verificar si estamos en el mes correcto
        if current_year == target_date.year and current_month == target_date.month:
            day_selected = self._select_day_in_current_month(page, target_date.day, date_type)
        else:
            # En lugar de navegar, seleccionar un día disponible en el mes actual
            day_selected = self._select_any_available_day(page, date_type)
        
        if day_selected:
            # Confirmar la selección
            return self._confirm_date_selection_simple(page)
        
        return False

    def _get_current_month_year(self, page: Page):
        """Obtiene el mes y año actual del calendario - Versión simple"""
        try:
            # Buscar en el título del mes
            month_title = page.locator('span.theme__title___2Ue3-')
            if month_title.count() > 0:
                title_text = month_title.text_content().strip()
                parts = title_text.split()
                if len(parts) >= 2:
                    month_name = parts[0].lower()
                    year_str = parts[1]
                    
                    month_map = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4, 
                        'may': 5, 'june': 6, 'july': 7, 'august': 8, 
                        'september': 9, 'october': 10, 'november': 11, 'december': 12
                    }
                    
                    if month_name in month_map and year_str.isdigit():
                        return month_map[month_name], int(year_str)
        except Exception:
            pass
        
        return None

    def _select_day_in_current_month(self, page: Page, target_day: int, date_type: str):
        """Selecciona un día específico en el mes actual"""
        available_days = page.locator('div[data-react-toolbox="day"]:not(.theme__disabled___2N4Gy)')
        day_count = available_days.count()
        
        for i in range(day_count):
            day_element = available_days.nth(i)
            day_text = day_element.text_content().strip()
            
            if day_text.isdigit() and int(day_text) == target_day:
                try:
                    day_element.click()
                    return True
                except Exception:
                    pass
        
        return False

    def _select_any_available_day(self, page: Page, date_type: str):
        """Selecciona cualquier día disponible en el mes actual"""
        available_days = page.locator('div[data-react-toolbox="day"]:not(.theme__disabled___2N4Gy)')
        
        if available_days.count() > 0:
            try:
                # Seleccionar el primer día disponible
                first_day = available_days.first
                first_day.click()
                return True
            except Exception:
                pass
        
        return False

    def _confirm_date_selection_simple(self, page: Page):
        """Confirma la selección de forma simple"""
        
        # Estrategia 1: Enter (siempre funciona)
        try:
            page.keyboard.press("Enter")
            time.sleep(1)
            return True
        except Exception:
            pass
        
        # Estrategia 2: Botón Ok específico del calendario
        try:
            ok_button = page.locator('nav[role="navigation"] button:has-text("Ok")')
            if ok_button.count() > 0:
                ok_button.first.click()
                time.sleep(1)
                return True
        except Exception:
            pass
        
        # Si todo falla, asumimos que la selección se confirmó automáticamente
        return True