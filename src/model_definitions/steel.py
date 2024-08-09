from sodym.tools.config import cfg
from src.model_extensions.use_stock_getter import InflowDrivenHistoric_StockDrivenFuture
from src.model_extensions.inflow_driven_for_categories import calc_steel_hist_stk_inflow
from sodym.classes.stocks_in_mfa import StockWithDSM
from sodym.classes.mfa_definition import (
    MFADefinition, DimensionDefinition, FlowDefinition, StockDefinition, ParameterDefinition)


# from sodym.tools.visualize import visualize_stock_prediction


class SteelMFASystem(InflowDrivenHistoric_StockDrivenFuture):

    def set_up_definition(self):
        dimensions = [
            dict(name='Time', dim_letter='t', dtype=int, filename='time_in_years'),
            dict(name='Element', dim_letter='e', dtype=str, filename='elements'),
            dict(name='Region', dim_letter='r', dtype=str, filename='regions'),
            dict(name='Intermediate', dim_letter='i', dtype=str, filename='intermediate_products'),
            dict(name='Good', dim_letter='g', dtype=str, filename='goods_in_use'),
            dict(name='Scenario', dim_letter='s', dtype=str, filename='scenarios'),
            dict(name='Historic Time', dim_letter='h', dtype=int, filename='historic_years'),
        ]

        processes = [
            'sysenv',
            'bof_production',
            'eaf_production',
            'forming',
            'fabrication_buffer',
            'ip_market',
            'ip_trade',
            'fabrication',
            'indirect_trade',
            'use',
            'outflow_buffer',
            'obsolete',
            'eol_market',
            'eol_trade',
            'recycling',
            'scrap_market',
            'excess_scrap'
        ]

        # names are auto-generated, see Flow class documetation
        flows = [
            dict(from_process='sysenv', to_process='bof_production', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='scrap_market', to_process='bof_production', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='bof_production', to_process='forming', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='bof_production', to_process='sysenv', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='scrap_market', to_process='eaf_production', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='eaf_production', to_process='forming', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='eaf_production', to_process='sysenv', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='forming', to_process='ip_market', dim_letters=('t', 'e', 'r', 'i', 's')),
            dict(from_process='forming', to_process='fabrication_buffer', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='forming', to_process='sysenv', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='ip_market', to_process='fabrication', dim_letters=('t', 'e', 'r', 'i', 's')),
            dict(from_process='ip_market', to_process='ip_trade', dim_letters=('t', 'e', 'r', 'i', 's')),
            dict(from_process='ip_trade', to_process='ip_market', dim_letters=('t', 'e', 'r', 'i', 's')),
            dict(from_process='fabrication', to_process='use', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='fabrication', to_process='fabrication_buffer', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='fabrication_buffer', to_process='scrap_market', dim_letters=('t', 'e', 'r', 's')),
            dict(from_process='use', to_process='outflow_buffer', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='use', to_process='indirect_trade', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='indirect_trade', to_process='use', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='outflow_buffer', to_process='obsolete', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='outflow_buffer', to_process='eol_market', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='eol_market', to_process='recycling', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='eol_market', to_process='eol_trade', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='eol_trade', to_process='eol_market', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='sysenv', to_process='recycling', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='recycling', to_process='scrap_market', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(from_process='scrap_market', to_process='excess_scrap', dim_letters=('t', 'e', 'r', 's'))
        ]

        stocks = [
            dict(name='use', process='use', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(name='outflow_buffer', process='outflow_buffer', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(name='obsolete', process='obsolete', dim_letters=('t', 'e', 'r', 'g', 's')),
            dict(name='fabrication_buffer', process='fabrication_buffer', dim_letters=('t', 'e', 'r', 's')),
            dict(name='excess_scrap', process='excess_scrap', dim_letters=('t', 'e', 'r', 's'))
        ]

        parameters = [
            dict(name='forming_yield', dim_letters=('i',)),
            dict(name='fabrication_yield', dim_letters=('g',)),
            dict(name='recovery_rate', dim_letters=('g',)),
            dict(name='external_copper_rate', dim_letters=('g',)),
            dict(name='cu_tolerances', dim_letters=('i',)),
            dict(name='good_to_intermediate_distribution', dim_letters=('g', 'i')),

            dict(name='production', dim_letters=('h', 'r')),
            dict(name='population', dim_letters=('t', 'r', 's')),
            dict(name='gdppc', dim_letters=('t', 'r', 's')),
            dict(name='sector_splits', dim_letters=('t', 'r', 'g')),
            dict(name='lifetime_mean', dim_letters=('r', 'g')),
            dict(name='lifetime_std', dim_letters=('r', 'g')),
            # in use dynamic stock model
            # dict(name='dsms_steel/inflows_base', dim_letters=('t','r','g','s')),
            # dict(name='dsms_steel/stocks_base', dim_letters=('t', 'r', 'g', 's')),
            # dict(name='dsms_steel/outflows_base', dim_letters=('t', 'r', 'g', 's')),
        ]

        scalar_parameters = [
            dict(name='max_scrap_share_base_model'),
            dict(name='scrap_in_bof_rate'),
            dict(name='forming_losses'),
            dict(name='production_yield'),
        ]

        self.definition = MFADefinition(
            dimensions=dimensions,
            processes=processes,
            flows=flows,
            stocks=stocks,
            parameters=parameters,
            scalar_parameters=scalar_parameters
        )

    def compute(self):
        """
        Perform all computations for the MFA system.
        """
        self.compute_in_use_stock()
        self.compute_flows()
        self.compute_other_stocks()
        self.check_mass_balance()

    """
    def compute_in_use_stock(self):
        '''Overwriting the inflow driven historic / stock driven future for now.
        TODO: change!
        Also Copper dimension is currently missing'''
        prm = self.parameters
        self.stocks['use'].stock['Fe'] = prm['dsms_steel/stocks_base']
        self.stocks['use'].inflow['Fe'] = prm['dsms_steel/inflows_base']
        self.stocks['use'].outflow['Fe'] = prm['dsms_steel/outflows_base']
        """

    def compute_historic_from_demand(self):
        prm = self.parameters
        hist_stk = self.get_new_stock(with_dsm=True, dim_letters=('h', 'r', 'g'))

        inflows = calc_steel_hist_stk_inflow(prm['production'].values,
                                             prm['sector_splits'].values,
                                             prm['good_to_intermediate_distribution'].values,
                                             prm['lifetime_mean'].values,
                                             prm['lifetime_std'].values,
                                             prm['forming_yield'].values,
                                             prm['fabrication_yield'].values,
                                             prm['population'].values)
        hist_stk.inflow[...] = self.get_new_array(name='Historic_Stock_inflow',
                                                  dim_letters=('h', 'r', 'g'),
                                                  values=inflows[:123])
        hist_stk.set_lifetime(cfg.ldf_type, prm['lifetime_mean'], prm['lifetime_std'])

        hist_stk.compute_inflow_driven()

        return hist_stk

    def transfer_to_mfa_stock(self, stk: StockWithDSM):
        # We use an auxiliary stock for the prediction step to save dimensions and computation time
        # Therefore, we have to transfer the result to the higher-dimensional stock in the MFA system
        self.stocks['use'].stock['Fe'][...] = stk.stock
        self.stocks['use'].inflow['Fe'][...] = stk.inflow
        self.stocks['use'].outflow['Fe'][...] = stk.outflow
        return

    def compute_flows(self):
        # abbreviations for better readability
        prm = self.parameters
        flw = self.flows
        stk = self.stocks
        scp = self.scalar_parameters

        # auxiliary arrays;
        # It is important to initialize them to define their dimensions. See the NamedDimArray documentation for details.
        # could also be single variables instead of dict, but this way the code looks more uniform
        aux = {
            'total_fabrication': self.get_new_array(dim_letters=('t', 'e', 'r', 'g', 's')),
            'production': self.get_new_array(dim_letters=('t', 'e', 'r', 'i', 's')),
            'forming_outflow': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'scrap_in_production': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'production_inflow': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'available_scrap': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'eaf_share_production': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'production_inflow': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'max_scrap_production': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'scrap_share_production': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
            'bof_production_inflow': self.get_new_array(dim_letters=('t', 'e', 'r', 's')),
        }

        # Slicing on the left-hand side of the assignment (foo[...] = bar) is used to assign only the values of the flows, not the NamedDimArray object managing the dimensions.
        # This way, the dimensions of the right-hand side of the assignment can be automatically reduced and re-ordered to the dimensions of the left-hand side.
        # For further details on the syntax, see the NamedDimArray documentation.

        # Pre-use

        flw['fabrication => use'][...] = stk['use'].inflow
        aux['total_fabrication'][...] = flw['fabrication => use'] / prm['fabrication_yield']
        flw['fabrication => fabrication_buffer'][...] = aux['total_fabrication'] - flw['fabrication => use']
        flw['ip_market => fabrication'][...] = aux['total_fabrication'] * prm['good_to_intermediate_distribution']
        flw['forming => ip_market'][...] = flw['ip_market => fabrication']
        aux['production'][...] = flw['forming => ip_market'] / prm['forming_yield']
        aux['forming_outflow'][...] = aux['production'] - flw['forming => ip_market']
        flw['forming => sysenv'][...] = aux['forming_outflow'] * scp['forming_losses']
        flw['forming => fabrication_buffer'][...] = aux['forming_outflow'] - flw['forming => sysenv']

        # Post-use

        flw['use => outflow_buffer'][...] = stk['use'].outflow
        flw['outflow_buffer => eol_market'][...] = flw['use => outflow_buffer'] * prm['recovery_rate']
        flw['outflow_buffer => obsolete'][...] = flw['use => outflow_buffer'] - flw['outflow_buffer => eol_market']
        flw['eol_market => recycling'][...] = flw['outflow_buffer => eol_market']
        flw['recycling => scrap_market'][...] = flw['eol_market => recycling']
        flw['fabrication_buffer => scrap_market'][...] = flw['forming => fabrication_buffer'] + flw[
            'fabrication => fabrication_buffer']

        # PRODUCTION

        aux['production_inflow'][...] = aux['production'] / scp['production_yield']
        aux['max_scrap_production'][...] = aux['production_inflow'] * scp['max_scrap_share_base_model']
        aux['available_scrap'][...] = flw['recycling => scrap_market'] + flw['fabrication_buffer => scrap_market']
        aux['scrap_in_production'][...] = aux['available_scrap'].minimum(
            aux['max_scrap_production'])  # using NumPy Minimum functionality
        flw['scrap_market => excess_scrap'][...] = aux['available_scrap'] - aux['scrap_in_production']
        aux['scrap_share_production']['Fe'][...] = aux['scrap_in_production']['Fe'] / aux['production_inflow']['Fe']
        aux['eaf_share_production'][...] = aux['scrap_share_production'] - scp['scrap_in_bof_rate']
        aux['eaf_share_production'][...] = aux['eaf_share_production'] / (1 - scp['scrap_in_bof_rate'])
        aux['eaf_share_production'][...] = aux['eaf_share_production'].minimum(1).maximum(0)
        flw['scrap_market => eaf_production'][...] = aux['production_inflow'] * aux['eaf_share_production']
        flw['scrap_market => bof_production'][...] = aux['scrap_in_production'] - flw['scrap_market => eaf_production']
        aux['bof_production_inflow'][...] = aux['production_inflow'] - flw['scrap_market => eaf_production']
        flw['sysenv => bof_production'][...] = aux['bof_production_inflow'] - flw['scrap_market => bof_production']
        flw['bof_production => forming'][...] = aux['bof_production_inflow'] * scp['production_yield']
        flw['bof_production => sysenv'][...] = aux['bof_production_inflow'] - flw['bof_production => forming']
        flw['eaf_production => forming'][...] = flw['scrap_market => eaf_production'] * scp['production_yield']
        flw['eaf_production => sysenv'][...] = flw['scrap_market => eaf_production'] - flw['eaf_production => forming']

        return

    def compute_other_stocks(self):
        stk = self.stocks
        flw = self.flows

        # in-use stock is already computed in compute_in_use_stock

        stk['obsolete'].inflow[...] = flw['outflow_buffer => obsolete']
        stk['obsolete'].compute_stock()

        stk['excess_scrap'].inflow[...] = flw['scrap_market => excess_scrap']
        stk['excess_scrap'].compute_stock()

        # TODO: Delay buffers?

        stk['outflow_buffer'].inflow[...] = flw['use => outflow_buffer']
        stk['outflow_buffer'].outflow[...] = flw['outflow_buffer => eol_market'] + flw['outflow_buffer => obsolete']
        stk['outflow_buffer'].compute_stock()

        stk['fabrication_buffer'].inflow[...] = flw['forming => fabrication_buffer'] + flw[
            'fabrication => fabrication_buffer']
        stk['fabrication_buffer'].outflow[...] = flw['fabrication_buffer => scrap_market']
        stk['fabrication_buffer'].compute_stock()

        return

    # Dictionary of variable names vs names displayed in figures.
    # Used by visualization routines.
    # Not required. If not present, the variable names are used.
    display_names = {
        'sysenv': 'System environment',
        'bof_production': 'Production (BF/BOF)',
        'eaf_production': 'Production (EAF)',
        'forming': 'Forming',
        'fabrication_buffer': 'Fabrication Buffer',
        'ip_market': 'Intermediate product market',
        'ip_trade': 'Intermediate product trade',
        'fabrication': 'Fabrication',
        'indirect_trade': 'Indirect trade',
        'in_use': 'Use phase',
        'outflow_buffer': 'Outflow buffer',
        'obsolete': 'Obsolete stocks',
        'eol_market': 'End of life product market',
        'eol_trade': 'End of life trade',
        'recycling': 'Recycling',
        'scrap_market': 'Scrap market',
        'excess_scrap': 'Excess scrap'
    }
