from sodym.classes.mfa_definition import (
    MFADefinition, DimensionDefinition, FlowDefinition, StockDefinition, ParameterDefinition)
from src.model_extensions.use_stock_getter import InflowDrivenHistoric_StockDrivenFuture
# from sodym.tools.visualize import visualize_stock_prediction


class PlasticsMFASystem(InflowDrivenHistoric_StockDrivenFuture):

    def set_up_definition(self):

        dimensions = [
            DimensionDefinition(name='Time',          dim_letter='t', dtype=int),
            DimensionDefinition(name='Historic Time', dim_letter='h', dtype=int),
            DimensionDefinition(name='Element',       dim_letter='e', dtype=str),
            DimensionDefinition(name='Region',        dim_letter='r', dtype=str),
            DimensionDefinition(name='Material',      dim_letter='m', dtype=str),
            DimensionDefinition(name='Good',          dim_letter='g', dtype=str),
        ]

        processes = [
            'sysenv',
            'virginfoss',
            'virginbio',
            'virgindaccu',
            'virginccu',
            'virgin',
            'fabrication',
            'recl',
            'reclmech',
            'reclchem',
            'reclsolv',
            'use',
            'eol',
            'incineration',
            'landfill',
            'uncontrolled',
            'emission',
            'captured',
            'atmosphere',
        ]

        # names are auto-generated, see Flow class documetation
        flows = [
            FlowDefinition(from_process='sysenv',       to_process='virginfoss',   dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='sysenv',       to_process='virginbio',    dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='sysenv',       to_process='virgindaccu',  dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='sysenv',       to_process='virginccu',    dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='atmosphere',   to_process='virginbio',    dim_letters=('t','e','r')),
            FlowDefinition(from_process='atmosphere',   to_process='virgindaccu',  dim_letters=('t','e','r')),
            FlowDefinition(from_process='virginfoss',   to_process='virgin',       dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='virginbio',    to_process='virgin',       dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='virgindaccu',  to_process='virgin',       dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='virginccu',    to_process='virgin',       dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='virgin',       to_process='fabrication',  dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='fabrication',  to_process='use',          dim_letters=('t','e','r','m','g')),
            FlowDefinition(from_process='use',          to_process='eol',          dim_letters=('t','e','r','m','g')),
            FlowDefinition(from_process='eol',          to_process='reclmech',     dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='eol',          to_process='reclchem',     dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='eol',          to_process='reclsolv',     dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='eol',          to_process='uncontrolled', dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='eol',          to_process='landfill',     dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='eol',          to_process='incineration', dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='reclmech',     to_process='recl',         dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='reclchem',     to_process='recl',         dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='reclsolv',     to_process='recl',         dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='recl',         to_process='fabrication',  dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='reclmech',     to_process='uncontrolled', dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='reclmech',     to_process='incineration', dim_letters=('t','e','r','m')),
            FlowDefinition(from_process='incineration', to_process='emission',     dim_letters=('t','e','r')),
            FlowDefinition(from_process='emission',     to_process='captured',     dim_letters=('t','e','r')),
            FlowDefinition(from_process='emission',     to_process='atmosphere',   dim_letters=('t','e','r')),
            FlowDefinition(from_process='captured',     to_process='virginccu',    dim_letters=('t','e','r')),
        ]

        stocks = [
            StockDefinition(name='in_use',       process='use',          dim_letters=('t','e','r','m','g')),
            StockDefinition(name='atmospheric',  process='atmosphere',   dim_letters=('t','e','r')),
            StockDefinition(name='landfill',     process='landfill',     dim_letters=('t','e','r','m')),
            StockDefinition(name='uncontrolled', process='uncontrolled', dim_letters=('t','e','r','m')),
        ]

        parameters = [
            # EOL rates
            ParameterDefinition(name='mechanical_recycling_rate',       dim_letters=('t','m')),
            ParameterDefinition(name='chemical_recycling_rate',         dim_letters=('t','m')),
            ParameterDefinition(name='solvent_recycling_rate',          dim_letters=('t','m')),
            ParameterDefinition(name='incineration_rate',               dim_letters=('t','m')),
            ParameterDefinition(name='uncontrolled_losses_rate',        dim_letters=('t','m')),
            # virgin production rates
            ParameterDefinition(name='bio_production_rate',             dim_letters=('t','m')),
            ParameterDefinition(name='daccu_production_rate',           dim_letters=('t','m')),
            # recycling losses
            ParameterDefinition(name='mechanical_recycling_yield',      dim_letters=('t','m')),
            ParameterDefinition(name='reclmech_loss_uncontrolled_rate', dim_letters=('t','m')),
            # other
            ParameterDefinition(name='material_shares_in_goods',        dim_letters=('m','g')),
            ParameterDefinition(name='emission_capture_rate',           dim_letters=('t',)),
            ParameterDefinition(name='carbon_content_materials',        dim_letters=('e','m')),
            # for in-use stock
            ParameterDefinition(name='production',                      dim_letters=('h','r','g')),
            ParameterDefinition(name='lifetime_mean',                   dim_letters=('g',)),
            ParameterDefinition(name='lifetime_std',                    dim_letters=('g',)),
            ParameterDefinition(name='population',                      dim_letters=('t','r')),
            ParameterDefinition(name='gdppc',                           dim_letters=('t','r')),
        ]

        self.definition = MFADefinition(
            dimensions=dimensions,
            processes=processes,
            flows=flows,
            stocks=stocks,
            parameters=parameters,
        )

    def compute(self):
        """
        Perform all computations for the MFA system.
        """
        self.compute_in_use_stock()
        self.compute_flows()
        self.compute_other_stocks()
        self.check_mass_balance()

    def compute_flows(self):

        # abbreviations for better readability
        prm = self.parameters
        flw = self.flows
        stk = self.stocks

        # auxiliary arrays;
        # It is important to initialize them to define their dimensions. See the NamedDimArray documentation for details.
        # could also be single variables instead of dict, but this way the code looks more uniform
        aux = {
            'reclmech_loss':                self.get_new_array(dim_letters=('t','e','r','m')),
            'virgin_2_fabr_all_mat':        self.get_new_array(dim_letters=('t','e','r')),
            'virgin_material_shares':       self.get_new_array(dim_letters=('t','e','r','m')),
            'captured_2_virginccu_by_mat':  self.get_new_array(dim_letters=('t','e','r','m')),
            'ratio_nonc_to_c':              self.get_new_array(dim_letters=('m',)),
        }

        # Slicing on the left-hand side of the assignment (foo[...] = bar) is used to assign only the values of the flows, not the NamedDimArray object managing the dimensions.
        # This way, the dimensions of the right-hand side of the assignment can be automatically reduced and re-ordered to the dimensions of the left-hand side.
        # For further details on the syntax, see the NamedDimArray documentation.

        flw['fabrication => use'][...]           = stk['in_use'].inflow
        flw['use => eol'][...]                   = stk['in_use'].outflow

        flw['eol => reclmech'][...]              = flw['use => eol']               * prm['mechanical_recycling_rate']
        flw['reclmech => recl'][...]             = flw['eol => reclmech']          * prm['mechanical_recycling_yield']
        aux['reclmech_loss'][...]                = flw['eol => reclmech']          - flw['reclmech => recl']
        flw['reclmech => uncontrolled'][...]     = aux['reclmech_loss']            * prm['reclmech_loss_uncontrolled_rate']
        flw['reclmech => incineration'][...]     = aux['reclmech_loss']            - flw['reclmech => uncontrolled']

        flw['eol => reclchem'][...]              = flw['use => eol']               * prm['chemical_recycling_rate']
        flw['reclchem => recl'][...]             = flw['eol => reclchem']

        flw['eol => reclsolv'][...]              = flw['use => eol']               * prm['solvent_recycling_rate']
        flw['reclsolv => recl'][...]             = flw['eol => reclsolv']

        flw['eol => incineration'][...]          = flw['use => eol']               * prm['incineration_rate']
        flw['eol => uncontrolled'][...]          = flw['use => eol']               * prm['uncontrolled_losses_rate']

        flw['eol => landfill'][...]              = flw['use => eol']               - flw['eol => reclmech'] \
                                                                                   - flw['eol => reclchem'] \
                                                                                   - flw['eol => reclsolv'] \
                                                                                   - flw['eol => incineration'] \
                                                                                   - flw['eol => uncontrolled']

        flw['incineration => emission'][...]     = flw['eol => incineration']      + flw['reclmech => incineration']

        flw['emission => captured'][...]         = flw['incineration => emission'] * prm['emission_capture_rate']
        flw['emission => atmosphere'][...]       = flw['incineration => emission'] - flw['emission => captured']
        flw['captured => virginccu'][...]        = flw['emission => captured']

        flw['recl => fabrication'][...]          = flw['reclmech => recl']         + flw['reclchem => recl'] \
                                                                                   + flw['reclsolv => recl']
        flw['virgin => fabrication'][...]        = flw['fabrication => use']       - flw['recl => fabrication']

        flw['virgindaccu => virgin'][...]        = flw['virgin => fabrication']    * prm['daccu_production_rate']
        flw['virginbio => virgin'][...]          = flw['virgin => fabrication']    * prm['bio_production_rate']

        aux['virgin_2_fabr_all_mat'][...]        = flw['virgin => fabrication']
        aux['virgin_material_shares'][...]       = flw['virgin => fabrication']    / aux['virgin_2_fabr_all_mat']
        aux['captured_2_virginccu_by_mat'][...]  = flw['captured => virginccu']    * aux['virgin_material_shares']

        # The { ... } syntax is used to slice the NamedDimArray object to a subset of its dimensions. See the NamedDimArray documentation for details.
        flw['virginccu => virgin']['C']              = aux['captured_2_virginccu_by_mat']['C']
        aux['ratio_nonc_to_c'][...]                  = prm['carbon_content_materials']['Other Elements'] / prm['carbon_content_materials']['C']
        flw['virginccu => virgin']['Other Elements'] = flw['virginccu => virgin']['C']                   * aux['ratio_nonc_to_c']

        flw['virginfoss => virgin'][...]         = flw['virgin => fabrication']    - flw['virgindaccu => virgin'] \
                                                                                   - flw['virginbio => virgin'] \
                                                                                   - flw['virginccu => virgin']

        flw['sysenv => virginfoss'][...]         = flw['virginfoss => virgin']
        flw['atmosphere => virginbio'][...]      = flw['virginbio => virgin']
        flw['atmosphere => virgindaccu'][...]    = flw['virgindaccu => virgin']
        flw['sysenv => virginccu'][...]          = flw['virginccu => virgin']      - aux['captured_2_virginccu_by_mat']

        # non-C atmosphere & captured has no meaning & is equivalent to sysenv

        return


    def compute_other_stocks(self):

        stk = self.stocks
        flw = self.flows

        # in-use stock is already computed in compute_in_use_stock

        stk['landfill'].inflow[...] = flw['eol => landfill']
        stk['landfill'].compute_stock()

        stk['uncontrolled'].inflow[...] = flw['eol => uncontrolled'] + flw['reclmech => uncontrolled']
        stk['uncontrolled'].compute_stock()

        stk['atmospheric'].inflow[...] = flw['emission => atmosphere']
        stk['atmospheric'].outflow[...] = flw['atmosphere => virgindaccu'] + flw['atmosphere => virginbio']
        stk['atmospheric'].compute_stock()
        return

    # Dictionary of variable names vs names displayed in figures.
    # Used by visualization routines.
    # Not required. If not present, the variable names are used.
    display_names = {
        'sysenv': 'System environment',
        'virginfoss': 'Virgin production (fossil)',
        'virginbio': 'Virgin production (biomass)',
        'virgindaccu': 'Virgin production (daccu)',
        'virginccu': 'Virgin production (ccu)',
        'virgin': 'Virgin production (total)',
        'fabrication': 'Fabrication',
        'recl': 'Recycling (total)',
        'reclmech': 'Mechanical recycling',
        'reclchem': 'Chemical recycling',
        'reclsolv': 'Solvent-based recycling',
        'use': 'Use Phase',
        'eol': 'End of Life',
        'incineration': 'Incineration',
        'landfill': 'Disposal',
        'uncontrolled': 'Uncontrolled release',
        'emission': 'Emissions',
        'captured': 'Captured',
        'atmosphere': 'Atmosphere'
    }
