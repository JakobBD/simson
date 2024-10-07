import numpy as np
from numpy.linalg import inv

from sodym import MFASystem

from simson.common.inflow_driven_mfa import InflowDrivenHistoricMFA
from simson.common.common_cfg import CommonCfg

class InflowDrivenHistoricSteelMFASystem(InflowDrivenHistoricMFA):

    def compute(self):
        """
        Perform all computations for the MFA system.
        """
        self.compute_historic_flows()
        self.compute_historic_in_use_stock()
        self.check_mass_balance()


    def compute_historic_flows(self):
        prm = self.parameters
        flw = self.flows
        stk = self.stocks
        scp = self.scalar_parameters

        aux = {
            'net_intermediate_trade': self.get_new_array(dim_letters=('h','r','i')),
            'fabrication_by_sector': self.get_new_array(dim_letters=('h','r','g')),
            'fabrication_loss': self.get_new_array(dim_letters=('h','r','g')),
            'fabrication_error': self.get_new_array(dim_letters=('h','r'))
        }

        flw['sysenv => forming'][...] = prm['production_by_intermediate']
        flw['forming => ip_market'][...] = prm['production_by_intermediate'] * prm['forming_yield']
        flw['forming => sysenv'][...] = flw['sysenv => forming'] - flw['forming => ip_market']

        # Todo: add trade

        aux['net_intermediate_trade'][...] = flw['ip_trade => ip_market'] - flw['ip_market => ip_trade']
        flw['ip_market => fabrication'][...] = flw['forming => ip_market'] + aux['net_intermediate_trade']

        aux['fabrication_by_sector'][...] = self._calc_sector_flows(
            flw['ip_market => fabrication'],
            prm['good_to_intermediate_distribution'])

        aux['fabrication_error'] = flw['ip_market => fabrication'] - aux['fabrication_by_sector']

        flw['fabrication => use'][...] = aux['fabrication_by_sector'] * prm['fabrication_yield']
        aux['fabrication_loss'][...] = aux['fabrication_by_sector'] - flw['fabrication => use']
        flw['fabrication => sysenv'][...] = aux['fabrication_error'] + aux['fabrication_loss']
        # Todo: add intermediate trade

        return

    def _calc_sector_flows(self, intermediate_flow, gi_distribution):
        """
        Estimate the fabrication by in-use-good according to the inflow of intermediate products
        and the good to intermediate product distribution.
        """

        # The following calculation is based on
        # https://en.wikipedia.org/wiki/Overdetermined_system#Approximate_solutions
        # gi_values represents 'A', hence the variable at_a is A transposed times A
        # 'b' is the intermediate flow and x are the sector flows that we are trying to find out

        gi_values = gi_distribution.values.transpose()
        at_a = np.matmul(gi_values.transpose(), gi_values)
        inverse_at_a = inv(at_a)
        inverse_at_a_times_at = np.matmul(inverse_at_a, gi_values.transpose())
        sector_flow_values = np.einsum('gi,hri->hrg',inverse_at_a_times_at, intermediate_flow.values)

        # don't allow negative sector flows
        sector_flow_values = np.maximum(0, sector_flow_values)

        sector_flows = self.get_new_array(dim_letters=('h','r','g'))
        sector_flows.values = sector_flow_values

        return sector_flows

    def compute_historic_in_use_stock(self):
        flw = self.flows
        stk = self.stocks
        stk['in_use'].inflow[...] = flw['fabrication => use'] + flw['indirect_trade => use'] - flw['use => indirect_trade']
        stk['in_use'].compute()

        return
