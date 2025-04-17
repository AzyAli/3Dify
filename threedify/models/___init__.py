"""Model integration for 3D generation.
"""
# from typing import Dict, Optional, Any
# from threedify.models.base import BaseModel
# from threedify.models.bolt3d import Bolt3DModel
# from threedify.models.trellis import TrellisModel

# _MODELS: Dict[str, BaseModel] = {
#     "bolt3d": Bolt3DModel(),
#     "trellis": TrellisModel(),
# }
# def get_model(model_type: str) -> BaseModel:
#     """Get model instance by type.
#     Args:
#         model_type (str): Type of model to get
#     Returns:
#         ValueError: If the model type is not recognized
#     """
#     if model_type not in _MODELS:
#         raise ValueError(f"Unrecognized model type: {model_type}. "
#                          f"Available models: {list(_MODELS.keys())}")
#     return _MODELS[model_type]

# def register_model(model_type: str, model_instance: BaseModel):
#     """Register a new model type.
#     Args:
#         model_type (str): Type of the model to register
#         model_instance (BaseModel): Model instance to register
#     """
#     _MODELS[model_type] = model_instance

__all__ = [
    "get_model",
    "register_model",
    "BaseModel",
    "Bolt3DModel",
    "TrellisModel"
]
