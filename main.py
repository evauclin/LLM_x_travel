from ticket_master import request_ticket_master


if __name__ == "__main__":
    params = {
        "city": "Paris",
        "countryCode": "FR",
        "locale": "*",
        "classificationName": "music",
        "page": 0
    }
    request_ticket_master(params)