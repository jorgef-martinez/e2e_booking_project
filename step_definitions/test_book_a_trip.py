from pytest_bdd import scenario, given, when, then, parsers
from actor.actors import Actor
from abilities.browse_the_web import BrowseTheWeb
from tasks.select_a_destination import SelectADestination
from tasks.filter_destinations import FilterDestinations
from tasks.book_the_trip import BookTheTrip
from questions.confirmation_message import ConfirmationMessage
import time

# Constantes
BASE_URL = "https://demo.testim.io/"

# --- Enlace del Scenario ---
@scenario('../features/book_a_trip.feature', 'Book a specific destination after filtering by price')
def test_book_a_trip_with_filters():
    """Escenario de prueba para reservar un viaje."""
    pass

# --- Implementación de Steps ---
@given("the user is on the booking homepage")
def go_to_homepage(web_actor: Actor):
    page = web_actor.ability_to(BrowseTheWeb).page
    page.goto(BASE_URL)

@when(parsers.parse('the user selects a trip for departing on "{departing}" and returning on "{returning}" and "{adults}" adults and "{children}" children'))
def select_passengers_and_dates(web_actor: Actor, departing: str, returning: str, adults: str, children: str):
    web_actor.attempts_to(
        SelectADestination.for_passengers(
            adults=adults, 
            children=children,
            departing=departing,
            returning=returning
        )
    )

@when("the user loads all available destinations")
def load_destinations(web_actor: Actor):
    pass

@when(parsers.parse('the user filters destinations with a maximum price of "{max_price}"'))
def filter_by_price(web_actor: Actor, max_price: str):
    web_actor.attempts_to(
        FilterDestinations.by_price(max_price=max_price)
    )

@when(parsers.parse('the user chooses to book the destination "{destination}"'))
def set_destination_context(test_context, destination: str):
    test_context.destination = destination

@when("the user fills in their personal information")
def fill_personal_info(test_context, web_actor: Actor):
    """Step definition para información personal"""
    user_data = {
        'name': 'Senior Automator',
        'email': 'test@quality.com', 
        'ssn': '123-56-7890'
    }
    test_context.user_data = user_data

@when(parsers.parse('the user applies the promo code "{promo_code}"'))
def perform_booking(test_context, promo_code: str, web_actor: Actor):
    # Verificar que tenemos los datos necesarios
    if not hasattr(test_context, 'destination') or not test_context.destination:
        raise ValueError("No se ha establecido el destino")
    
    if not hasattr(test_context, 'user_data') or not test_context.user_data:
        raise ValueError("No se ha establecido la información personal")
    
    web_actor.attempts_to(
        BookTheTrip.for_destination(
            destination=test_context.destination,
            user_data=test_context.user_data,
            promo_code=promo_code
        )
    )

@then(parsers.parse('the system should confirm the booking with the message "{message}"'))
def verify_confirmation_message(web_actor: Actor, message: str):
    result = web_actor.asks_for(ConfirmationMessage.displays(message))
    assert result, f"Expected confirmation message '{message}' was not displayed"