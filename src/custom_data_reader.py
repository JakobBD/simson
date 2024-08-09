import os

from sodym.classes.data_reader import ExampleDataReader
from sodym.classes.mfa_definition import DimensionDefinition


class CustomDataReader(ExampleDataReader):
    dimension_map = {
        'Time': 'time_in_years',
        'Historic Time': 'historic_years',
        'Element': 'elements',
        'Region': 'regions',
        'Material': 'materials',
        'Good': 'goods_in_use',
        'Intermediate': 'intermediate_products',
        'Scenario': 'scenarios',
    }
    def __init__(self, input_data_path):
        self.input_data_path = input_data_path
        scalar_data_yaml = os.path.join(input_data_path, 'scalar_parameters.yml')
        super().__init__(scalar_data_yaml, {}, {})
    
    def read_parameter_values(self, parameter: str, dims):
        self.parameter_datasets[parameter] = os.path.join(
            self.input_data_path, 'datasets', f'{parameter}.csv'
        )
        return super().read_parameter_values(parameter=parameter, dims=dims)
    
    def read_dimension(self, definition: DimensionDefinition):
        dimension_filename = self.dimension_map[definition.name]
        self.dimension_datasets[definition.name] = os.path.join(
            self.input_data_path, 'dimensions', f'{dimension_filename}.csv'
        )
        return super().read_dimension(definition=definition)
