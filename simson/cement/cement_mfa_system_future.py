import flodym as fd
import numpy as np


class StockDrivenCementMFASystem(fd.MFASystem):
    """
    For now, this is the same as historic MFA
    """
    
    def compute(self, demand: fd.FlodymArray):
        """
        Perform all computations for the MFA system.
        """
        self.compute_in_use_stock(demand)
        self.compute_flows()
        self.compute_other_stocks()
        self.check_mass_balance()

    def compute_in_use_stock(self, demand):
        self.stocks["in_use"].inflow = demand
        self.stocks["in_use"].lifetime_model.set_prms(
            mean=self.parameters["use_lifetime_mean"], std=self.parameters["use_lifetime_std"]
        )
        self.stocks["in_use"].compute()

    def compute_flows(self):
        prm = self.parameters
        flw = self.flows
        stk = self.stocks

        # go backwards from in-use stock
        flw["concrete_production => use"][...] = stk["in_use"].inflow
        flw["cement_grinding => concrete_production"][...] = flw["concrete_production => use"] * prm["cement_ratio"]
        flw["clinker_production => cement_grinding"][...] = flw["cement_grinding => concrete_production"] * prm["clinker_ratio"]
        flw["raw_meal_preparation => clinker_production"][...] = flw["clinker_production => cement_grinding"]

        # sysenv flows for mass balance
        flw["sysenv => raw_meal_preparation"][...] = flw["raw_meal_preparation => clinker_production"]
        flw["sysenv => clinker_production"][...] = fd.FlodymArray(dims=self.dims["t", "r"])
        flw["sysenv => cement_grinding"][...] = flw["cement_grinding => concrete_production"] * (1 - prm["clinker_ratio"])
        flw["sysenv => concrete_production"][...] = flw["concrete_production => use"] * (1 - prm["cement_ratio"])

    def compute_other_stocks(self):
        flw = self.flows
        stk = self.stocks

        flw["use => eol"][...] = stk["in_use"].outflow
        stk["eol"].inflow[...] = flw["use => eol"]
        stk["eol"].outflow[...] = fd.FlodymArray(dims=self.dims["t", "r", "s"])
        stk["eol"].compute()
        flw["eol => sysenv"][...] = stk["eol"].outflow
    






