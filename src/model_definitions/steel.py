from sodym.classes.mfa_definition import (
    MFADefinition, DimensionDefinition, FlowDefinition, ParameterDefinition, StockDefinition
)
from src.model_extensions.use_stock_getter import InflowDrivenHistoric_StockDrivenFuture


class SteelMFASystem(InflowDrivenHistoric_StockDrivenFuture):

    def set_up_definition(self):
        dimensions = [
            DimensionDefinition(name='Time', dim_letter='t', dtype=int),
            DimensionDefinition(name='Element', dim_letter='e', dtype=str),
            DimensionDefinition(name='Region', dim_letter='r', dtype=str),
            DimensionDefinition(name='Intermediate', dim_letter='i', dtype=str),
            DimensionDefinition(name='Good', dim_letter='g', dtype=str),
            DimensionDefinition(name='Scenario', dim_letter='s', dtype=str),
            DimensionDefinition(name='Historic Time', dim_letter='h', dtype=int),
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
            FlowDefinition(from_process='sysenv', to_process='bof_production', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='scrap_market', to_process='bof_production', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='bof_production', to_process='forming', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='bof_production', to_process='sysenv', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='scrap_market', to_process='eaf_production', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='eaf_production', to_process='forming', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='eaf_production', to_process='sysenv', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='forming', to_process='ip_market', dim_letters=('t', 'e', 'r', 'i', 's')),
            FlowDefinition(from_process='forming', to_process='fabrication_buffer', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='forming', to_process='sysenv', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='ip_market', to_process='fabrication', dim_letters=('t', 'e', 'r', 'i', 's')),
            FlowDefinition(from_process='ip_market', to_process='ip_trade', dim_letters=('t', 'e', 'r', 'i', 's')),
            FlowDefinition(from_process='ip_trade', to_process='ip_market', dim_letters=('t', 'e', 'r', 'i', 's')),
            FlowDefinition(from_process='fabrication', to_process='use', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='fabrication', to_process='fabrication_buffer', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='fabrication_buffer', to_process='scrap_market', dim_letters=('t', 'e', 'r', 's')),
            FlowDefinition(from_process='use', to_process='outflow_buffer', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='use', to_process='indirect_trade', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='indirect_trade', to_process='use', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='outflow_buffer', to_process='obsolete', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='outflow_buffer', to_process='eol_market', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='eol_market', to_process='recycling', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='eol_market', to_process='eol_trade', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='eol_trade', to_process='eol_market', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='sysenv', to_process='recycling', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='recycling', to_process='scrap_market', dim_letters=('t', 'e', 'r', 'g', 's')),
            FlowDefinition(from_process='scrap_market', to_process='excess_scrap', dim_letters=('t', 'e', 'r', 's'))
        ]

        stocks = [
            StockDefinition(name='use', process='use', dim_letters=('t', 'e', 'r', 'g', 's')),
            StockDefinition(name='outflow_buffer', process='outflow_buffer', dim_letters=('t', 'e', 'r', 'g', 's')),
            StockDefinition(name='obsolete', process='obsolete', dim_letters=('t', 'e', 'r', 'g', 's')),
            StockDefinition(name='fabrication_buffer', process='fabrication_buffer', dim_letters=('t', 'e', 'r', 's')),
            StockDefinition(name='excess_scrap', process='excess_scrap', dim_letters=('t', 'e', 'r', 's'))
        ]

        parameters = [
            ParameterDefinition(name='forming_yield', dim_letters=('i',)),
            ParameterDefinition(name='fabrication_yield', dim_letters=('g',)),
            ParameterDefinition(name='recovery_rate', dim_letters=('g',)),
            ParameterDefinition(name='external_copper_rate', dim_letters=('g',)),
            ParameterDefinition(name='cu_tolerances', dim_letters=('i',)),
            ParameterDefinition(name='good_to_intermediate_distribution', dim_letters=('g', 'i')),

            ParameterDefinition(name='production', dim_letters=('h', 'r')),
            ParameterDefinition(name='population', dim_letters=('t', 'r', 's')),
            ParameterDefinition(name='gdppc', dim_letters=('t', 'r', 's')),

            # in use dynamic stock model
            #dict(name='dsms_steel/inflows_base', dim_letters=('t','r','g','s')),
            #dict(name='dsms_steel/stocks_base', dim_letters=('t', 'r', 'g', 's')),
            #dict(name='dsms_steel/outflows_base', dim_letters=('t', 'r', 'g', 's')),
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
            scalar_parameters=scalar_parameters,
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

        flw['fabrication => use'][...]                  = stk['use'].inflow
        aux['total_fabrication'][...]                   = flw['fabrication => use']             /   prm['fabrication_yield']
        flw['fabrication => fabrication_buffer'][...]   = aux['total_fabrication']              -   flw['fabrication => use']
        flw['ip_market => fabrication'][...]            = aux['total_fabrication']              *   prm['good_to_intermediate_distribution']
        flw['forming => ip_market'][...]                = flw['ip_market => fabrication']
        aux['production'][...]                          = flw['forming => ip_market']           /   prm['forming_yield']
        aux['forming_outflow'][...]                     = aux['production']                     -   flw['forming => ip_market']
        flw['forming => sysenv'][...]                   = aux['forming_outflow']                *   scp['forming_losses']
        flw['forming => fabrication_buffer'][...]       = aux['forming_outflow']                -   flw['forming => sysenv']

        # Post-use

        flw['use => outflow_buffer'][...]               = stk['use'].outflow
        flw['outflow_buffer => eol_market'][...]        = flw['use => outflow_buffer']          *   prm['recovery_rate']
        flw['outflow_buffer => obsolete'][...]          = flw['use => outflow_buffer']          -   flw['outflow_buffer => eol_market']
        flw['eol_market => recycling'][...]             = flw['outflow_buffer => eol_market']
        flw['recycling => scrap_market'][...]           = flw['eol_market => recycling']
        flw['fabrication_buffer => scrap_market'][...]  = flw['forming => fabrication_buffer']  +   flw['fabrication => fabrication_buffer']


        # PRODUCTION

        aux['production_inflow'][...]                   = aux['production']                     /   scp['production_yield']
        aux['max_scrap_production'][...]                = aux['production_inflow']              *   scp['max_scrap_share_base_model']
        aux['available_scrap'][...]                     = flw['recycling => scrap_market']      +   flw['fabrication_buffer => scrap_market']
        aux['scrap_in_production'][...]                 = aux['available_scrap'].minimum(aux['max_scrap_production'])  # using NumPy Minimum functionality
        flw['scrap_market => excess_scrap'][...]        = aux['available_scrap']                -   aux['scrap_in_production']
        aux['scrap_share_production']['Fe'][...]        = aux['scrap_in_production']['Fe']      /   aux['production_inflow']['Fe']
        aux['eaf_share_production'][...]                = aux['scrap_share_production']         -   scp['scrap_in_bof_rate']
        aux['eaf_share_production'][...]                = aux['eaf_share_production']           /   (1 - scp['scrap_in_bof_rate'])
        aux['eaf_share_production'][...]                = aux['eaf_share_production'].minimum(1).maximum(0)
        flw['scrap_market => eaf_production'][...]      = aux['production_inflow']              *   aux['eaf_share_production']
        flw['scrap_market => bof_production'][...]      = aux['scrap_in_production']            -   flw['scrap_market => eaf_production']
        aux['bof_production_inflow'][...]               = aux['production_inflow']              -   flw['scrap_market => eaf_production']
        flw['sysenv => bof_production'][...]            = aux['bof_production_inflow']          -   flw['scrap_market => bof_production']
        flw['bof_production => forming'][...]           = aux['bof_production_inflow']          *   scp['production_yield']
        flw['bof_production => sysenv'][...]            = aux['bof_production_inflow']          -   flw['bof_production => forming']
        flw['eaf_production => forming'][...]           = flw['scrap_market => eaf_production'] *   scp['production_yield']
        flw['eaf_production => sysenv'][...]            = flw['scrap_market => eaf_production'] -   flw['eaf_production => forming']

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

        stk['fabrication_buffer'].inflow[...] = flw['forming => fabrication_buffer'] + flw['fabrication => fabrication_buffer']
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