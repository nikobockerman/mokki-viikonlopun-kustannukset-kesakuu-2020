# Input data, first key is intended payer, second key is original payer.
# Payments with intended payer "kaikki" get shared amongs all participants.
payments = {
    "kaikki": {"Timo": 75, "Niko": 35, "Ville": 40, "Tapio": 35},
    "Timo": {"Niko": 10.5},
    "Sami": {"Niko": 10.5},
    "Tomi": {"Niko": 10.5},
    "Ville": {"Niko": 10.5},
    "Tapio": {"Ville": 8.5, "Sami": 27},
}
participants = ["Timo", "Niko", "Ville", "Sami", "Tapio", "Tomi"]

common_costs = sum(payments["kaikki"].values())


def get_costs(name):
    return common_costs / len(participants) + sum(payments.get(name, {}).values())


def get_payments(name):
    return sum([x.get(name, 0) for x in payments.values()])


def print_results(calculations):
    print("\tCosts\tPayments\tTo pay\tTo receive")
    for name, c in calculations.items():
        print(
            "{}\t{}\t{}\t\t{}\t{}".format(
                name, c["costs"], c["payments"], c["to_pay"], c["to_receive"]
            )
        )


def main():
    calculations = {}
    for name in participants:
        costs = get_costs(name)
        payments = get_payments(name)
        to_pay = max(0, costs - payments)
        to_receive = max(0, payments - costs)
        calculations[name] = {
            "costs": costs,
            "payments": payments,
            "to_pay": to_pay,
            "to_receive": to_receive,
        }
    print_results(calculations)


if __name__ == "__main__":
    main()
