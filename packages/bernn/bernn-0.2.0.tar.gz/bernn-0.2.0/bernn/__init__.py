"""BERNN: Batch Effect Removal Neural Networks for Tandem Mass Spectrometry.

This package provides tools for removing batch effects from mass spectrometry data
using deep learning approaches.
"""

__version__ = "0.1.18"
__author__ = "Simon Pelletier"
__license__ = "MIT"

# Core training modules
from .dl.train import (
    TrainAE,
    TrainAEClassifierHoldout,
    TrainAEThenClassifierHoldout,
)

# Model definitions
from .dl.models.pytorch import (
    AutoEncoder2,
    SHAPAutoEncoder2,
    KANAutoencoder2,
    SHAPKANAutoencoder2,
    AutoEncoder3,
    SHAPAutoEncoder3,
)

# KAN modules
from .dl.train.pytorch.ekan import KANLinear, KAN

__all__ = [
    # Training
    "TrainAE",
    "TrainAEClassifierHoldout",
    "TrainAEThenClassifierHoldout",

    # Models
    "AutoEncoder2",
    "SHAPAutoEncoder2",
    "KANAutoencoder2",
    "SHAPKANAutoencoder2",
    "AutoEncoder3",
    "SHAPAutoEncoder3",

    # KAN
    "KANLinear",
    "KAN"
]
