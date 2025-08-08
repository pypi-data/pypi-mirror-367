#!/usr/bin/env python3
"""
Test script to verify that aedann.py can be imported even when PyTorch is not available.
"""

import sys
import importlib
import types

def mock_torch_unavailable():
    """Temporarily make torch unavailable by removing it from sys.modules."""
    # Store original torch modules if they exist
    original_modules = {}
    torch_modules = [name for name in sys.modules.keys() if name.startswith('torch')]

    for module_name in torch_modules:
        original_modules[module_name] = sys.modules[module_name]
        del sys.modules[module_name]

    # Mock torch import to raise ImportError
    def mock_torch_import(name, *args, **kwargs):
        if name.startswith('torch'):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    original_import = __builtins__['__import__']
    __builtins__['__import__'] = mock_torch_import

    return original_modules, original_import

def restore_torch(original_modules, original_import):
    """Restore torch modules."""
    __builtins__['__import__'] = original_import
    for module_name, module in original_modules.items():
        sys.modules[module_name] = module

def test_import_without_torch():
    """Test importing aedann when torch is not available."""
    print("Testing import when PyTorch is not available...")

    # Mock torch as unavailable
    original_modules, original_import = mock_torch_unavailable()

    try:
        # Try to import the module
        import bernn.dl.models.pytorch.aedann as aedann
        print(f"✓ Module imported successfully. TORCH_AVAILABLE = {aedann.TORCH_AVAILABLE}")

        # Try to use a class - this should raise our helpful error
        try:
            classifier = aedann.Classifier()
            print("✗ Expected ImportError when creating Classifier without PyTorch")
        except ImportError as e:
            print(f"✓ Helpful error raised when using PyTorch functionality: {e}")

    except Exception as e:
        print(f"✗ Failed to import module: {e}")
    finally:
        # Restore torch
        restore_torch(original_modules, original_import)

def test_import_with_torch():
    """Test importing aedann when torch is available."""
    print("\nTesting import when PyTorch is available...")

    try:
        # Reload the module to ensure fresh import
        if 'bernn.dl.models.pytorch.aedann' in sys.modules:
            del sys.modules['bernn.dl.models.pytorch.aedann']

        import bernn.dl.models.pytorch.aedann as aedann
        print(f"✓ Module imported successfully. TORCH_AVAILABLE = {aedann.TORCH_AVAILABLE}")

        if aedann.TORCH_AVAILABLE:
            print("✓ PyTorch is available, classes should work normally")
        else:
            print("ℹ PyTorch is not available on this system")

    except Exception as e:
        print(f"✗ Failed to import module: {e}")

if __name__ == "__main__":
    test_import_without_torch()
    test_import_with_torch()
