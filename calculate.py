#!/usr/bin/env python3

import click
import json


class Data:
    def __init__(self, rounding, data):
        self.rounding = rounding
        self.data = data

    @property
    def payments(self):
        return self.data["payments"]

    @property
    def participants(self):
        return self.data["participants"]

    @property
    def shared_costs(self):
        return sum([value.get("yhteinen", 0) for value in self.payments.values()])

    def get_participant_costs(self, name):
        shared = self.shared_costs / len(self.participants) * 100 // 1 / 100
        pays = [value.get(name, 0) for value in self.payments.values()]
        return shared + sum(pays)

    def get_participant_payments(self, name):
        return sum(self.payments.get(name, {}).values())


class Participant:
    def __init__(self, name, data):
        self.name = name
        self.costs = data.get_participant_costs(self.name)
        self.payments = data.get_participant_payments(self.name)
        self.to_pay = max(0, self.costs - self.payments)
        self.to_receive = max(0, self.payments - self.costs)

    def to_pay_remaining(self, transactions):
        return self.to_pay - sum([t.amount for t in transactions if t.p_from is self])

    def to_receive_remaining(self, transactions):
        return self.to_receive - sum([t.amount for t in transactions if t.p_to is self])


class Transaction:
    def __init__(self, p_from, p_to, amount, data):
        self.p_from = p_from
        self.p_to = p_to
        self.amount = amount
        self.rounded_amount = round(self.amount, data.rounding)

    def get_rounding_error(self):
        return abs(self.rounded_amount - self.amount)


class TransactionCombo:
    def __init__(self, transactions):
        self.transactions = transactions

    def get_rounding_error(self):
        return sum([t.get_rounding_error() for t in self.transactions])


def get_possible_transactions(participants, transactions, data):
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
                Transaction(
                    p_from, p_to, min(to_pay_remaining, to_receive_remaining), data
                )
            )

    return possible_transactions


def get_transaction_combos(participants, already_made_transactions, data):
    possible_transactions = get_possible_transactions(
        participants, already_made_transactions, data
    )
    if not possible_transactions:
        yield TransactionCombo(already_made_transactions)
        return

    for possible_transaction in possible_transactions:
        transactions = already_made_transactions[:]
        transactions.append(possible_transaction)
        for combo in get_transaction_combos(participants, transactions, data):
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


def get_best_transactions(participants, data):
    return get_least_rounding_errors_combo(
        get_least_transfers_combos(get_transaction_combos(participants, [], data))
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


class JsonFile(click.File):
    name = "json_file"

    def __init__(self):
        super().__init__()

    def convert(self, value, param, ctx):
        f = super().convert(value, param, ctx)
        if f:
            try:
                j = json.load(f)
                return j
            except Exception as e:
                self.fail(f"Could not parse json file: {value!r}: {e}", param, ctx)
            finally:
                f.close()


@click.command()
@click.option(
    "--round",
    "rounding",
    default=1,
    help="Number of decimals to round transactions to",
    show_default=True,
)
@click.argument("data_file", type=JsonFile())
def calculate(rounding, data_file):
    d = Data(rounding, data_file)
    participants = []
    for name in d.participants:
        participants.append(Participant(name, d))
    transactions = get_best_transactions(participants, d)
    print_results(participants, transactions)


if __name__ == "__main__":
    calculate()
