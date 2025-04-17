"""Matplotlib visualization for threedify.
"""

import logging
from typing import Any, Dict, Optional, Union
import numpy as np
from threedify.visualization.base import BaseVisualizer

logger = logging.getLogger(__name__)
class MatplotlibVisualizer(BaseVisualizer):
    """Visualizer using Matplotlib."""
    def visualize(self, model_data: Any, **kwargs) -> Any:
        """Visualize model data using Matplotlib.
        Args:
            model_data: Model data to visualize
            **kwargs: Additional parameters
                - figsize (tuple): Figure size (width, height) in inches
                - dpi (int): DPI for the figure
                - background_color (tuple): Background color (r, g, b)
                - save_image (str): Path to save the visualization as image
                - point_size (float): Size of points for point clouds
                - opacity (float): Opacity of mesh surfaces 
        Returns:
            Matplotlib figure
        """
        logger.info("Creating Matplotlib visualization")
        figsize = kwargs.get('figsize', (10, 8))
        dpi = kwargs.get('dpi', 100)
        background_color = kwargs.get('background_color', (0.1, 0.1, 0.1))
        save_image = kwargs.get('save_image', None)
        point_size = kwargs.get('point_size', 2)
        opacity = kwargs.get('opacity', 0.8)
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure(figsize=figsize, dpi=dpi)
            fig.patch.set_facecolor(background_color)
            if hasattr(model_data, 'point_cloud'):
                ax = self._visualize_point_cloud(fig, model_data, background_color, point_size)
            elif hasattr(model_data, 'mesh'):
                ax = self._visualize_mesh(fig, model_data, background_color, opacity)
            else:
                ax = self._visualize_generic(fig, model_data, background_color)
            if save_image:
                plt.savefig(save_image, bbox_inches='tight', facecolor=fig.get_facecolor())
                logger.info(f"Visualization saved to {save_image}")
            return fig
        except Exception as e:
            logger.error(f"Failed to create visualization: {str(e)}")
            raise
    
    def _visualize_point_cloud(self, fig, model_data, background_color, point_size):
        """Visualize a point cloud using Matplotlib.
        Args:
            fig: Matplotlib figure
            model_data: Point cloud data
            background_color (tuple): Background color (r, g, b)
            point_size (float): Size of points
        Returns:
            Matplotlib axis
        """
        points = model_data.point_cloud
        if hasattr(model_data, 'colors') and model_data.colors is not None:
            colors = model_data.colors
            if colors.shape[1] > 3:
                colors = colors[:, :3]  # Use just RGB, drop alpha if present
        else:
            colors = np.ones((len(points), 3)) * 0.7
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(background_color)
        ax.scatter(
            points[:, 0],
            points[:, 1],
            points[:, 2],
            c=colors,
            s=point_size,
            alpha=0.8
        )
        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.set_zlabel('Z', color='white')
        ax.set_title('Point Cloud Visualization', color='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.zaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='z', colors='white')
        self._set_axes_equal(ax)
        return ax
    
    def _visualize_mesh(self, fig, model_data, background_color, opacity):
        """Visualize a mesh using Matplotlib.
        Args:
            fig: Matplotlib figure
            model_data: Mesh data
            background_color (tuple): Background color (r, g, b)
            opacity (float): Opacity of mesh surfaces
        Returns:
            Matplotlib axis
        """
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(background_color)
        mesh_list = []
        for face in faces:
            mesh_list.append([vertices[face[0]], vertices[face[1]], vertices[face[2]]])
        
        poly = Poly3DCollection(mesh_list, alpha=opacity)
        if colors is not None:
            face_colors = []
            for face in faces:
                face_color = np.mean(colors[face], axis=0)[:3]  # Use RGB only
                face_colors.append(face_color)
            poly.set_facecolor(face_colors)
        else:
            poly.set_facecolor('cyan')
        ax.add_collection3d(poly)
        all_pts = vertices
        x_min, x_max = np.min(all_pts[:, 0]), np.max(all_pts[:, 0])
        y_min, y_max = np.min(all_pts[:, 1]), np.max(all_pts[:, 1])
        z_min, z_max = np.min(all_pts[:, 2]), np.max(all_pts[:, 2])
        padding = max(max(x_max - x_min, y_max - y_min), z_max - z_min) * 0.1
        
        ax.set_xlim([x_min - padding, x_max + padding])
        ax.set_ylim([y_min - padding, y_max + padding])
        ax.set_zlim([z_min - padding, z_max + padding])
        
        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.set_zlabel('Z', color='white')

        ax.set_title('Mesh Visualization', color='white')

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.zaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='z', colors='white')
        
        self._set_axes_equal(ax)
        return ax
    
    def _visualize_generic(self, fig, model_data, background_color):
        """Create a generic visualization for unknown data.
        Args:
            fig: Matplotlib figure
            model_data: Model data to visualize
            background_color (tuple): Background color (r, g, b)
        Returns:
            Matplotlib axis
        """
        ax = fig.add_subplot(111)
        ax.set_facecolor(background_color)
        ax.text(
            0.5, 0.5,
            "Unknown data type. Cannot create visualization.",
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            color='white',
            fontsize=14
        )
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Model Data Visualization', color='white')
        return ax
    
    def _set_axes_equal(self, ax):
        """Make axes of 3D plot have equal scale.
        Args:
            ax: Matplotlib 3D axis
        """
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()
        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # The plot bounding box is a sphere in the sense of the infinityyyyyy
        # Hence why I call half the max range the plot radius.
        plot_radius = 0.5 * max([x_range, y_range, z_range])
        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    
    @property
    def name(self) -> str:
        """Get the name of the visualizer.
        Returns:
            str: Visualizer name
        """
        return "matplotlib"
