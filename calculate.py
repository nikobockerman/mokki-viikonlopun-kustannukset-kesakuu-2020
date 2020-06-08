#!/usr/bin/env python3

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
# print("Shared costs: {}".format(shared_costs))


def get_participant_costs(name):
    shared = shared_costs / len(input_data["participants"]) * 100 // 1 / 100
    pays = [value.get(name, 0) for value in payments.values()]
    # print("{}: shared={}; payments={} => {}".format(name, shared, pays, sum(pays)))
    return shared + sum(pays)


def get_participant_payments(name):
    return sum(payments.get(name, {}).values())


class Participant:
    def __init__(self, name, costs, payments):
        self.name = name
        self.costs = costs
        self.payments = payments
        self.to_pay = max(0, self.costs - self.payments)
        self.to_receive = max(0, self.payments - self.costs)

    def to_pay_remaining(self, transactions):
        return self.to_pay - sum([t.amount for t in transactions if t.p_from is self])

    def to_receive_remaining(self, transactions):
        return self.to_receive - sum([t.amount for t in transactions if t.p_to is self])


class Transaction:
    def __init__(self, p_from, p_to, amount):
        self.p_from = p_from
        self.p_to = p_to
        self.amount = amount
        self.rounded_amount = round(self.amount, 1)

    def get_rounding_error(self):
        return abs(self.rounded_amount - self.amount)


class TransactionCombo:
    def __init__(self, transactions):
        self.transactions = transactions

    def get_rounding_error(self):
        return sum([t.get_rounding_error() for t in self.transactions])


def get_possible_transactions(participants, transactions):
    possible_transactions = []
    for p_from in participants:
        to_pay_remaining = p_from.to_pay_remaining(transactions)
        # print("To pay remaining: {} = {}".format(p_from.name, to_pay_remaining))
        if to_pay_remaining <= 0:
            continue

        for p_to in participants:
            if p_to is p_from:
                continue

            to_receive_remaining = p_to.to_receive_remaining(transactions)
            # print("To receive remaining: {} = {}".format(p_to.name, to_receive_remaining))
            if to_receive_remaining <= 0:
                continue

            possible_transactions.append(
                Transaction(p_from, p_to, min(to_pay_remaining, to_receive_remaining))
            )

    return possible_transactions


def get_transaction_combos(participants, already_made_transactions):
    possible_transactions = get_possible_transactions(
        participants, already_made_transactions
    )
    if not possible_transactions:
        yield TransactionCombo(already_made_transactions)
        return

    for possible_transaction in possible_transactions:
        transactions = already_made_transactions[:]
        transactions.append(possible_transaction)
        for combo in get_transaction_combos(participants, transactions):
            yield combo


def get_least_transfers_combos(combos):
    least_transfers_combos = sorted(combos, key=lambda combo: len(combo.transactions))
    min_transfers = len(least_transfers_combos[0].transactions)
    for combo in least_transfers_combos:
        if len(combo.transactions) == min_transfers:
            yield combo
        else:
            return


def get_least_rounding_errors_combo(combos):
    least_rounding_error = sorted(combos, key=lambda combo: combo.get_rounding_error())
    return least_rounding_error[0]


def get_best_transactions(participants):
    return get_least_rounding_errors_combo(
        get_least_transfers_combos(get_transaction_combos(participants, []))
    )


def print_results(participants, combo):
    print("Name\tCosts\tPayments\tTo pay\tTo receive")
    for p in participants:
        print(
            "{}\t{:.2f}\t{:.2f}\t\t{:.2f}\t{:.2f}".format(
                p.name, p.costs, p.payments, p.to_pay, p.to_receive
            )
        )
    print()
    print("Transactions:")
    for t in combo.transactions:
        print("{} => {}: {:.2f}".format(t.p_from.name, t.p_to.name, t.rounded_amount))
    print("Total rounding error: {:.2f}".format(combo.get_rounding_error()))


def main():
    participants = []
    for name in input_data["participants"]:
        costs = get_participant_costs(name)
        payments = get_participant_payments(name)
        participants.append(Participant(name, costs, payments))
    transactions = get_best_transactions(participants)
    print_results(participants, transactions)


if __name__ == "__main__":
    main()
