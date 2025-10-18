import os
import random
from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb
import time

class BookTheTrip:
    def __init__(self, destination: str, user_data: dict, promo_code: str):
        self.destination = destination
        self.user_data = user_data
        self.promo_code = promo_code

    @staticmethod
    def for_destination(destination: str, user_data: dict, promo_code: str) -> "BookTheTrip":
        return BookTheTrip(destination, user_data, promo_code)

    def perform_as(self, actor: Actor):
        page = actor.ability_to(BrowseTheWeb).page
        
        time.sleep(2)
        
        # Click en Book del destino
        destination_card = page.locator(f"div[data-react-toolbox='card']:has-text('{self.destination}')")
        
        if destination_card.count() == 0:
            return
        
        destination_card.get_by_role("button", name="Book").click()
        
        time.sleep(3)
        
        # Llenar formulario
        page.locator('form').get_by_text('Name').locator('..').locator('input').fill(self.user_data['name'])
        page.locator('form').get_by_text('Email Address').locator('..').locator('input').fill(self.user_data['email'])
        page.locator('form').get_by_text('Social Security Number').locator('..').locator('input').fill(self.user_data['ssn'])
        
        # Teléfono
        phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        phone_number = f"+1787{phone_suffix}"
        page.locator('form').get_by_text('Phone Number').locator('..').locator('input').fill(phone_number)
        
        # Archivo
        file_path = os.path.join("resources", "test_file.txt")
        if os.path.exists(file_path):
            page.locator('input[type="file"]').set_input_files(file_path)

        # Código promocional
        promo_applied = self._apply_promo_code(page, self.promo_code)
        
        # Términos y condiciones
        terms_accepted = self._accept_terms_and_conditions(page)
        
        if not terms_accepted:
            return

        # PAY NOW
        payment_success = self._click_pay_now(page)
        
        if payment_success:
            # Esperar a que aparezca la confirmación
            time.sleep(5)

    def _apply_promo_code(self, page, promo_code: str):
        """Aplica el código promocional"""
        promo_input = page.locator('input[name="promo"]')
        if promo_input.count() > 0 and promo_input.is_visible():
            try:
                promo_input.fill(promo_code)
                
                apply_button = page.get_by_role("button", name="Apply")
                if apply_button.count() > 0 and apply_button.is_visible():
                    apply_button.click()
                time.sleep(2)
                return True
            except Exception:
                pass
        
        return False

    def _accept_terms_and_conditions(self, page):
        """Acepta los términos y condiciones"""
        terms_label = page.get_by_text("I agree to the terms", exact=False)
        if terms_label.count() > 0:
            try:
                terms_label.click()
                time.sleep(1)
                return True
            except Exception:
                pass
        
        return False

    def _click_pay_now(self, page):
        """Hace click en Pay now"""
        
        # ESTRATEGIA 1: Buscar por rol y texto
        pay_button = page.get_by_role("button", name="Pay now")
        
        if pay_button.count() > 0:
            is_visible = pay_button.is_visible()
            is_disabled = pay_button.get_attribute("disabled")
            
            if is_visible and is_disabled is None:
                try:
                    pay_button.click()
                    return True
                except Exception:
                    pass
        
        # ESTRATEGIA 2: Buscar por data attribute
        pay_button_data = page.locator('[data-react-toolbox="button"]:has-text("Pay now")')
        if pay_button_data.count() > 0 and pay_button_data.is_visible():
            try:
                pay_button_data.click()
                return True
            except Exception:
                pass
        
        # ESTRATEGIA 3: Forzar click con coordenadas
        try:
            bounding_box = pay_button.bounding_box()
            if bounding_box:
                page.mouse.click(bounding_box['x'] + bounding_box['width'] / 2, 
                               bounding_box['y'] + bounding_box['height'] / 2)
                return True
        except Exception:
            pass
        
        return False