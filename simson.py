from sodym.tools.config import cfg
from src.model_definitions import init_mfa
from sodym.tools.visualize import visualize_mfa_sankey
from sodym.tools.export import export
from src.model_extensions.custom_visualization import visualize_production

cfg.set_from_yml('config/steel.yml')

mfa = init_mfa()
mfa.compute()

visualize_mfa_sankey(mfa)
visualize_production(mfa)
export(mfa)
