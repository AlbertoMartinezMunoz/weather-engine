Feature: Acquisition
    A script to retrieve configuration data from .env file

    Background:
        Given env file path is <env_path>
        Given env key is <key>

    Scenario: Script Parameters Integrity
        When the envconfig script is launched
        Then <result>

    Examples:
        | env_path                     | key        | result                                |
        | ./tests/data/.env-test       | VERSION    | the script returns success            |
        | ./tests/data/.env-test       |            | an -k/--key error is notified         |


    Scenario: Env Config Get Key
        Given env file path is ./tests/data/.env-test
        And env key is KEY
        When the envconfig script is launched
        Then the script returns success
        And the script returns KEY and KEY VALUE

    Scenario: Env Config Get Bad Key
        Given env file path is ./tests/data/.env-test
        And env key is BAD_KEY
        When the envconfig script is launched
        Then the script fails
        And the script returns BAD_KEY not found error
