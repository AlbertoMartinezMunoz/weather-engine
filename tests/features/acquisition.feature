Feature: Download AEMET daily observations into a storage folder
  As a user collecting weather data
  I want the script to store one raw file per station and month
  So that I can build a local history of the observations

  Background:
    Given an empty temporary storage folder
    And the station 2422 is configured

  Scenario: A specific month is downloaded and stored
    When I download the month "2024-01"
    Then the download exits with code 0
    And the file "2422/2422.2024-01.json" exists in the storage folder
    And the file holds valid daily records of station "2422" for the month "2024-01"
    And the output mentions "saved"

  Scenario: A month that is already stored is not downloaded again
    Given the month "2024-01" is already stored with the content "[]"
    When I download the month "2024-01"
    Then the download exits with code 0
    And the output mentions "already stored"
    And the file "2422/2422.2024-01.json" still has the content "[]"

  Scenario: Without a month the oldest missing month since 1980-01 is downloaded
    Given every month from "1980-01" to "2023-12" is already stored
    When I download without specifying a month
    Then the download exits with code 0
    And the file "2422/2422.2024-01.json" exists in the storage folder
    And the storage folder holds 529 files

  Scenario: Without a month the first gap in the stored months is filled
    Given every month from "1980-01" to "1980-02" is already stored
    And every month from "1980-04" to "1980-05" is already stored
    When I download without specifying a month
    Then the download exits with code 0
    And the file "2422/2422.1980-03.json" exists in the storage folder
    And the storage folder holds 5 files

  Scenario: The current month is refused because it is not final yet
    When I download the current month
    Then the download exits with code 1
    And the error output mentions "not final yet"
    And the storage folder holds 0 files

  Scenario Outline: An invalid month is rejected before calling AEMET
    When I download the month "<month>"
    Then the download exits with code 2
    And the error output mentions "month must be in YYYY-MM format"
    And the storage folder holds 0 files

    Examples:
      | month   |
      | 2024/01 |
      | 2024-13 |
      | 2024-00 |
      | january |

  Scenario: The storage folder is required
    When I run the download script without arguments
    Then the download exits with code 2
    And the error output mentions "required"

  Scenario: An invalid API key stores nothing
    Given the API key "invalid-key" is configured
    When I download the month "2024-01"
    Then the download exits with code 1
    And the error output mentions "download failed"
    And the storage folder holds 0 files
