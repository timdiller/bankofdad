# Standard library imports
from datetime import date, timedelta

# Math imports

# ETS imports
from traits.api import (
    HasTraits, Property, Instance, Date, Enum, Float, List
)

# Local imports
from bankofdad.io.account_reader import load_account_from_csv
from bankofdad.model.person import Person
from bankofdad.model.transaction import Transaction
from bankofdad.util.time_util import last_saturday, last_sunday

# Module level variables - TODO - move to config file
allowance_period = timedelta(7)
interest_period = allowance_period
savings_interest_rate = 0.01
loan_interest_rate = 0.05


class Account(HasTraits):
    savings_interest_rate = Float(1. / 100.)
    loan_interest_rate = Float(2. / 100.)
    owner = Instance(Person)
    kind = Enum("Savings")
    balance = Property(Float)
    last_interest = Date
    next_interest = Property(Date, depends_on="last_interest")
    last_allowance = Date
    next_allowance = Property(Date, depends_on="last_allowance")
    weekly_allowance = Property(Float)

    transactions = List(Instance(Transaction))

    def _get_next_interest(self):
        return last_saturday()

    def _get_next_allowance(self):
        return last_sunday()

    def _get_weekly_allowance(self):
        """Weekly rate"""
        return self.owner.age / 2.0  # dollars

    def update(self):
        if date.today() >= self.next_interest:
            self.apply_allowance()
            self.next_interest += interest_period
        if date.today() >= self.next_allowance:
            self.apply_allowance()
            self.next_allowance += allowance_period

    def apply_allowance(self):
        self.balance += self.weekly_allowance
        self.last_allowance = self.next_allowance

    def apply_interest(self):
        if self.balance > 0:
            self.balance *= 1. + savings_interest_rate
        else:
            self.balace *= 1. + loan_interest_rate
        self.last_interest = self.next_interest

    def load_file(self, filename):
        if filename.endswith(".csv"):
            account = load_account_from_csv(filename)
        return account