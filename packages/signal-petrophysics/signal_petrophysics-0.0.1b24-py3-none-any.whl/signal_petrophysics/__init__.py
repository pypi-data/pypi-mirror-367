"""Signal Petrophysics package for well log analysis."""

# src/signal_petrophysics/__init__.py

# Import all functions from submodules
from .load_data import *
from .pattern_find import *
from .plot import *
from .signal_adapt import *
from .utils.mnemonics import *

# You can also be more explicit if you prefer:
# from .load_data import create_mnemonic_dict, field_las_read, field_las_read_offset
# from .pattern_find import signal_sampling_by_depth, auto_similarity, generate_stencils, calc_cca, offset_similarity, process_corr, calc_corr
# from .plot import plot_well_logs, plot_well_logs_withsample_scaled, plot_rock_labels, plot_rock_labels_auto, plot_rock_labels_Int, plot_rock_labels_auto_dim, categorize_intervals_from_df, plot_matching_zones_histograms_dynamic
# from .signal_adapt import adjust_signal_length

__version__ = "0.1.0"
