# 3Dify: Transform Geospatial Data into 3D Models for Flood Analysis

3Dify is a Python library that bridges the gap between raw geospatial data and actionable 3D visualizations for flood risk management. By leveraging cloud-based APIs, it makes advanced 3D generation accessible without requiring specialized hardware.

## 🌟 Features

- **Data Versatility**: Process LiDAR point clouds, satellite imagery, and vector data
- **Cloud-Powered Generation**: Create 3D models using Hugging Face-hosted APIs (Bolt3D, TRELLIS)
- **Multiple Export Formats**: Save your models as GLTF/GLB, CityGML, OBJ, or PLY
- **Interactive Visualization**: Explore models in Jupyter notebooks with 3D controls
- **Building Analysis**: Special processing for buildings with semantic CityGML export
- **Command-Line Interface**: Automate workflows with the built-in CLI

## 🚀 Quick Start

```bash
# Install the package
pip install threedify
```

## Create a 3D model from a GeoTIFF
threedify -i imagery.tif -o building.glb --model trellis

## 💻 Usage Example
```Python
import threedify
```
## Create a processing pipeline
```pipeline = threedify.create_pipeline()```

## Convert satellite imagery to a 3D model
```
pipeline.run_pipeline(
    data_path="path/to/satellite.tif",
    output_path="path/to/output.glb",
    data_type="raster",
    model_type="bolt3d",
    export_format="gltf"
)
```
## 📋 Requirements

 - Python 3.8+

 - Internet connection (for API access)

 -  Common geospatial libraries (GDAL, laspy, etc.)

## 🔍 How It Works

3Dify doesn't require local GPU resources - instead, it processes your input data locally and then uses Hugging Face-hosted services for the computation-intensive 3D generation step.

## 📝 Citation



@software{3Dify_2025,
  author = {Ali, Azy},
  title = {3Dify: Spatial data to 3D model generation for flood risk management},
  year = {2025},
  url = {https://github.com/AzyAli/3Dify}
}

## 📄 License
MIT License

