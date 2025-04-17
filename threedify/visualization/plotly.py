"""Plotly visualization for threedify.
"""

import logging
from typing import Any, Dict, Optional, Union
import numpy as np

from threedify.visualization.base import BaseVisualizer
logger = logging.getLogger(__name__)

class PlotlyVisualizer(BaseVisualizer):
    """Visualizer using Plotly."""
    
    def visualize(self, model_data: Any, **kwargs) -> Any:
        """Visualize model data using Plotly.
        Args:
            model_data: Model data to visualize
            **kwargs: Additional parameters
                - width (int): Visualization width
                - height (int): Visualization height
                - background_color (tuple): Background color (r, g, b)
                - save_html (str): Path to save the visualization as HTML
                - point_size (float): Size of points for point clouds
                - opacity (float): Opacity of mesh surfaces   
        Returns:
            Plotly figure
        """
        logger.info("Creating Plotly visualization")
        width = kwargs.get('width', 800)
        height = kwargs.get('height', 600)
        background_color = kwargs.get('background_color', (0.1, 0.1, 0.1))
        save_html = kwargs.get('save_html', None)
        point_size = kwargs.get('point_size', 2)
        opacity = kwargs.get('opacity', 0.8)
        try:
            import plotly.graph_objects as go
            if hasattr(model_data, 'point_cloud'):
                fig = self._visualize_point_cloud(model_data, width, height, background_color, point_size)
            elif hasattr(model_data, 'mesh'):
                fig = self._visualize_mesh(model_data, width, height, background_color, opacity)
            elif hasattr(model_data, 'gaussian') and model_data.gaussian:
                fig = self._visualize_gaussian(model_data, width, height, background_color)
            else:
                fig = self._visualize_generic(model_data, width, height, background_color)
            
            if save_html:
                fig.write_html(save_html)
                logger.info(f"Visualization saved to {save_html}")
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create visualization: {str(e)}")
            raise
    
    def _visualize_point_cloud(self, model_data, width, height, background_color, point_size):
        """Visualize a point cloud using Plotly.
        Args:
            model_data: Point cloud data
            width (int): Visualization width
            height (int): Visualization height
            background_color (tuple): Background color (r, g, b)
            point_size (float): Size of the points
        Returns:
            Plotly figure
        """
        import plotly.graph_objects as go
        points = model_data.point_cloud
        if hasattr(model_data, 'colors') and model_data.colors is not None:
            colors = model_data.colors
            if colors.shape[1] == 3:  # RGB
                colors = [f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})' 
                         for r, g, b in colors]
            elif colors.shape[1] == 4:  # RGBA
                colors = [f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})' 
                         for r, g, b, a in colors]
        else:
            colors = ['rgb(128, 128, 128)'] * len(points)
        
        fig = go.Figure(data=[go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=point_size,
                color=colors,
                opacity=0.8
            )
        )])
        fig.update_layout(
            width=width,
            height=height,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            paper_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            plot_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            title='Point Cloud Visualization'
        )
        return fig
    
    def _visualize_mesh(self, model_data, width, height, background_color, opacity):
        """Visualize a mesh using Plotly.
        Args:
            model_data: Mesh data
            width (int): Visualization width
            height (int): Visualization height
            background_color (tuple): Background color (r, g, b)
            opacity (float): Opacity of mesh surfaces
        Returns:
            Plotly figure
        """
        import plotly.graph_objects as go
        import numpy as np
        if hasattr(model_data, 'mesh') and isinstance(model_data.mesh, dict):
            vertices = model_data.mesh.get('vertices', np.array([]))
            faces = model_data.mesh.get('faces', np.array([]))
            colors = model_data.mesh.get('colors', None)
        else:
            vertices = np.array([
                [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
            ])
            faces = np.array([
                [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
                [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
                [0, 3, 7], [0, 7, 4], [1, 2, 6], [1, 6, 5]
            ])
            colors = None
        i, j, k = faces[:, 0], faces[:, 1], faces[:, 2]
        colorscale = None
        intensity = None
    
        if colors is not None:
            face_colors = np.zeros(len(faces))
            for idx, face in enumerate(faces):
                face_colors[idx] = np.mean(colors[face])
            colorscale = 'Viridis'
            intensity = face_colors
        mesh_3d = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=i, j=j, k=k,
            opacity=opacity,
            flatshading=True
        )
        if intensity is not None:
            mesh_3d.intensity = intensity
            mesh_3d.colorscale = colorscale
        else:
            mesh_3d.color = 'lightblue'
        fig = go.Figure(data=[mesh_3d])
        fig.update_layout(
            width=width,
            height=height,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            paper_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            plot_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            title='Mesh Visualization'
        )
        return fig
    
    def _visualize_gaussian(self, model_data, width, height, background_color):
        """Create a visualization for Gaussian models using Plotly.
        Args:
            model_data: Gaussian model data
            width (int): Visualization width
            height (int): Visualization height
            background_color (tuple): Background color (r, g, b)
        Returns:
            Plotly figure
        """
        import plotly.graph_objects as go
        import numpy as np
        num_points = 5000
        points = np.random.randn(num_points, 3)
        colors = np.random.rand(num_points, 3)
        colors_str = [f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})' for r, g, b in colors]
        fig = go.Figure(data=[go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=3,
                color=colors_str,
                opacity=0.7
            )
        )])
        fig.update_layout(
            width=width,
            height=height,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            paper_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            plot_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            title='3D Gaussian Model Visualization (Preview)'
        )
        return fig
    
    def _visualize_generic(self, model_data, width, height, background_color):
        """Create a generic visualization for unknown data.
        Args:
            model_data: Model data to visualize
            width (int): Visualization width
            height (int): Visualization height
            background_color (tuple): Background color (r, g, b)
        Returns:
            Plotly figure
        """
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_annotation(
            text="Unknown data type. Cannot create visualization.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(
                family="Arial",
                size=14,
                color="white"
            )
        )
        fig.update_layout(
            width=width,
            height=height,
            paper_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            plot_bgcolor=f'rgb({int(background_color[0]*255)}, {int(background_color[1]*255)}, {int(background_color[2]*255)})',
            title='Model Data Visualization',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
    
    @property
    def name(self) -> str:
        """Get the name of the visualizer.
        Returns:
            str: Visualizer name
        """
        return "plotly"
