import requests

import


if __name__ == "__main__":
    params = {
        "city": "Paris",
        "countryCode": "FR",
        "locale": "*",
        "classificationName": "music",
        "page": 0
    }
    request_ticket_master(params)