"""Command-line interface for the 3Dify package.
"""
import argparse
import sys      
import logging
from pathlib import Path

from threedify.core.pipeline import Pipeline
from threedify import __version__

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="3Dify CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of 3Dify"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to the configuration file (JSON format)"
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Path to the input data file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Path to the output file/directory"
    )
    parser.add_argument(
        "--data-type",
        type=str,
        default=None,
        choices=["lidar", "raster", "vector"],
        help="Type of data to load (will be inferred if not specified)"
    )
    parser.add_argument(
        "--process",
        type=str,
        default=None,
        choices=["pointcloud", "raster", "vector", "general"],
        help="Type of processing to perform (will be inferred if not specified)"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="bolt3d",
        choices=["bolt3d", "trellis"],
        help="3D generation model to use"
    )
    parser.add_argument(
        "--export-format", 
        type=str, 
        default="gltf",
        choices=["gltf", "citygml", "obj", "ply"],
        help="Output format for the 3D model"
    )
    parser.add_argument(
        "--building-mode", 
        action="store_true",
        help="Enable specialized processing for buildings (for CityGML output)"
    )
    # Advanced options
    parser.add_argument(
        "--cache-dir", 
        type=str, 
        default=None,
        help="Directory to use for caching"
    )
    parser.add_argument(
        "--optimize-mesh", 
        action="store_true",
        help="Optimize the output mesh (reduce faces, optimize UVs)"
    )
    return parser.parse_args()

def setup_logging(verbose):
    """Set up logging configuration."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def create_config_from_args(args):
    """Create a configuration dictionary from command-line arguments."""
    config = {}
    if args.config:
        from threedify.core.config import Config
        base_config = Config(config_path=args.config)
        config = base_config._config
    config["general"] = config.get("general", {})
    config["general"]["verbose"] = args.verbose
    config["loader"] = config.get("loader", {})
    if args.cache_dir:
        config["loader"]["cache_dir"] = args.cache_dir
    config["processor"] = config.get("processor", {})
    if args.building_mode:
        config["processor"]["building_mode"] = True
    config["export"] = config.get("export", {})
    config["export"]["optimize_mesh"] = args.optimize_mesh
    return config

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    setup_logging(args.verbose)  
    try:
        # Create the pipeline
        config = create_config_from_args(args)
        pipeline = Pipeline(config)
        pipeline.run_pipeline(
            data_path=args.input,
            output_path=args.output,
            data_type=args.data_type,
            process_type=args.process,
            model_type=args.model,
            export_format=args.export_format
        )
        logger.info("Pipeline completed successfully.output saved to %s", args.output)
        return 0
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1
if __name__ == "__main__":
    sys.exit(main())