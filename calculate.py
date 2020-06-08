input_data = {
    "participants": ["Timo", "Niko", "Ville", "Sami", "Tapio", "Tomi"],
    # payments: First key is original payer, second key is intended payer.
    # Payments with intended payer "yhteinen" get shared amongst all participants.
    "payments": {
        "Timo": {"yhteinen": 75},
        "Ville": {"yhteinen": 40, "Tapio": 8.5},
        "Niko": {
            "yhteinen": 35,
            "Timo": 10.5,
            "Sami": 10.5,
            "Tomi": 10.5,
            "Ville": 10.5,
        },
        "Tapio": {"yhteinen": 35},
        "Sami": {"Tapio": 27},
    },
}

payments = input_data["payments"]
shared_costs = sum([value.get("yhteinen", 0) for value in payments.values()])


def get_participant_costs(name):
    return shared_costs / len(input_data["participants"]) + sum(
        [value.get(name, 0) for value in payments.values()]
    )


def get_participant_payments(name):
    return sum(payments.get(name, {}).values())


class Participant:
    def __init__(self, name, costs, payments):
        self.name = name
        self.costs = costs
        self.payments = payments
        self.to_pay = max(0, self.costs - self.payments)
        self.to_receive = max(0, self.payments - self.costs)


def print_results(participants):
    print("Name\tCosts\tPayments\tTo pay\tTo receive")
    for p in participants:
        print(
            "{}\t{}\t{}\t\t{}\t{}".format(
                p.name, p.costs, p.payments, p.to_pay, p.to_receive
            )
        )


def main():
    participants = []
    for name in input_data["participants"]:
        costs = get_participant_costs(name)
        payments = get_participant_payments(name)
        participants.append(Participant(name, costs, payments))
    print_results(participants)


if __name__ == "__main__":
    main()
