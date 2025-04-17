"""Visualization modules for threedify.
"""

# from typing import Dict
# from threedify.visualization.base import BaseVisualizer
# from threedify.visualization.jupyter import JupyterVisualizer
# from threedify.visualization.plotly import PlotlyVisualizer
# from threedify.visualization.matplotlib import MatplotlibVisualizer

# _VISUALIZERS: Dict[str, BaseVisualizer] = {
#     "jupyter": JupyterVisualizer(),
#     "plotly": PlotlyVisualizer(),
#     "matplotlib": MatplotlibVisualizer(),
# }

# def get_visualizer(visualizer_type: str) -> BaseVisualizer:
#     """Get a visualizer instance by type.
#     Args:
#         visualizer_type (str): Type of visualizer to get
#     Returns:
#         BaseVisualizer: Visualizer instance
#     Raises:
#         ValueError: If the visualizer type is not registered
#     """
#     if visualizer_type not in _VISUALIZERS:
#         raise ValueError(f"Unknown visualizer type: {visualizer_type}. "
#                          f"Available types: {list(_VISUALIZERS.keys())}")
#     return _VISUALIZERS[visualizer_type]

# def register_visualizer(visualizer_type: str, visualizer_instance: BaseVisualizer):
#     """Register a new visualizer type.
#     Args:
#         visualizer_type (str): Type name to register
#         visualizer_instance (BaseVisualizer): Visualizer instance to register 
#     Returns:
#         None
#     """
#     _VISUALIZERS[visualizer_type] = visualizer_instance

# def init_notebook():
#     """Initialize Jupyter notebook for 3D visualization."""
#     try:
#         from IPython.display import display, HTML
#         import ipywidgets as widgets
#         display(HTML("""
#         <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
#         <style>
#             .jp-OutputArea-output {
#                 width: 100%;
#             }
#         </style>
#         """))
#         print("Jupyter notebook initialized for 3D visualization.")
#     except ImportError:
#         print("Warning: IPython or ipywidgets not found. "
#               "Visualization in Jupyter notebooks may not work properly.")
__all__ = ["get_visualizer", "register_visualizer", "init_notebook", "BaseVisualizer", 
           "JupyterVisualizer", "PlotlyVisualizer", "MatplotlibVisualizer"]
