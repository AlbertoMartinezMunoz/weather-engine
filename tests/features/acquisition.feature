Feature: Acquisition
    A script to retrieve data from AEMET Open Data site

    Background:
        Given output path is <ouput_path>
        Given start date is <start_date>
        Given end date is <end_date>
        Given configuration file path is ./config.yaml

    Scenario: Script Parameters Integrity
        When the acquisition script is launched
        Then <result>

    Examples:
        | ouput_path | start_date | end_date   | config_path   | result                                |
        | ./data     | 2026-10-01 | 2026-10-03 | ./config.yaml | the script returns success            |
        |            | 2026-10-01 | 2026-10-03 | ./config.yaml | an -o/--output-dir error is notified  |
        | ./data     |            | 2026-10-03 | ./config.yaml | an -s/--start-date error is notified  |
        | ./data     | 2020-10-01 |            | ./config.yaml | an -e/--end-date error is notified    |
        | ./data     | 2026-10-03 | 2026-10-01 | ./config.yaml | a date ordering error is notified     |
