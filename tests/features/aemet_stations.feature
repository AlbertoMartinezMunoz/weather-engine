Feature: Find the nearest AEMET stations against the real API

  Scenario: Real inventory returns sorted stations near Valladolid
    When I run the script live with "41.6523 -4.7245 5"
    Then the live script exits with code 0
    And the live script prints 5 stations
    And the printed distances are sorted ascending
    And the closest printed station is less than 50 km away

  Scenario: AEMET rejects an invalid API key
    When I run the script live with "41.6523 -4.7245 5 --api-key invalid-key"
    Then the live script exits with an error
    And the live error output mentions an AEMET failure
