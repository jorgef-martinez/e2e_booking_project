# features/book_a_trip.feature

Feature: Book a trip online
  As a Product Owner,
  I want to allow users to book a trip with price filters
  so that customers can have more autonomy.

  @critical
  Scenario Outline: Book a specific destination after filtering by price
    Given the user is on the booking homepage
    When the user selects a trip for departing on "<departing>" and returning on "<returning>" and "<adults>" adults and "<children>" children 
    And the user loads all available destinations
    And the user filters destinations with a maximum price of "<max_price>"
    And the user chooses to book the destination "<destination>"
    And the user fills in their personal information
      | name              | email               | ssn          |
      | Senior Automator  | test@quality.com    | 123-46-7890  |
    And the user applies the promo code "<promo_code>"
    Then the system should confirm the booking with the message "Destination Booked!"
  
    Examples: Data for different destinations
      | departing  | returning  | adults  | children | max_price | destination             | promo_code |
      | 25/10/2025 | 26/10/2025 | 2       | 1        | 1300      | Sant Cugat Del Valles   | PROMO15    |
      | 27/11/2025 | 28/11/2025 | 1       | 3        | 500       | Flagstaff               | SALE20     |