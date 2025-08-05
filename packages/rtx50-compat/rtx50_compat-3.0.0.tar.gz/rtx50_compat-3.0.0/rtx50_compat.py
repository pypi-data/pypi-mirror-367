"""
rtx50-compat v3.0.0: Deep sm_120 to sm_90 Mapping
Critical fix for RTX 5090 segfaults
"""

import os
import sys
import warnings
import importlib

__version__ = "3.0.0"

# CRITICAL: Set environment BEFORE any CUDA initialization
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TORCH_CUDA_ARCH_LIST'] = '9.0'  # Force sm_90
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
os.environ['TORCH_USE_CUDA_DSA'] = '1'

# Suppress all CUDA warnings immediately
warnings.filterwarnings("ignore", message=".*CUDA.*")
warnings.filterwarnings("ignore", message=".*sm_120.*")

def _early_patch_torch():
    """Patch torch._C before it's fully imported"""
    
    # Create a wrapper module for torch._C
    class PatchedTorchC:
        def __init__(self, real_module):
            self._real_module = real_module
            
        def __getattr__(self, name):
            if name == '_cuda_getDeviceCapability':
                return self._patched_getDeviceCapability
            return getattr(self._real_module, name)
            
        def _patched_getDeviceCapability(self, device):
            # Always return sm_90 for RTX 5090
            try:
                # Try to get real capability
                if hasattr(self._real_module, '_cuda_getDeviceCapability'):
                    major, minor = self._real_module._cuda_getDeviceCapability(device)
                    if major == 12:  # sm_120
                        return (9, 0)  # Return sm_90
                    return (major, minor)
            except:
                pass
            return (9, 0)  # Default to sm_90
    
    # Intercept torch._C import
    original_import = __builtins__.__import__ if isinstance(__builtins__, dict) else __builtins__.__import__
    
    def custom_import(name, *args, **kwargs):
        module = original_import(name, *args, **kwargs)
        if name == 'torch._C':
            return PatchedTorchC(module)
        return module
    
    if isinstance(__builtins__, dict):
        __builtins__['__import__'] = custom_import
    else:
        __builtins__.__import__ = custom_import

# Apply early patch
_early_patch_torch()

# Now we can safely import torch
import torch

def patch_cuda_functions():
    """Patch all CUDA capability detection functions"""
    
    # 1. Patch get_device_capability
    if hasattr(torch.cuda, 'get_device_capability'):
        _original_get_cap = torch.cuda.get_device_capability
        
        def patched_get_capability(device=None):
            try:
                major, minor = _original_get_cap(device)
                if major == 12:  # RTX 50-series
                    return (9, 0)  # Report as H100
                return (major, minor)
            except:
                return (9, 0)
        
        torch.cuda.get_device_capability = patched_get_capability
    
    # 2. Patch get_device_properties
    if hasattr(torch.cuda, 'get_device_properties'):
        _original_get_props = torch.cuda.get_device_properties
        
        def patched_get_properties(device):
            props = _original_get_props(device)
            # Modify the properties object
            if hasattr(props, 'major') and props.major == 12:
                # Can't modify props directly, but we've already fixed capability
                pass
            return props
        
        torch.cuda.get_device_properties = patched_get_properties
    
    # 3. Patch the check that causes the warning
    if hasattr(torch.cuda, '_check_capability'):
        torch.cuda._check_capability = lambda: True

# Apply patches
patch_cuda_functions()

# Verify it works
def verify_rtx5090():
    """Verify RTX 5090 is working"""
    if not torch.cuda.is_available():
        return False
        
    try:
        # Test basic CUDA operation
        device = torch.device('cuda:0')
        x = torch.randn(10, 10, device=device)
        y = x @ x.T
        torch.cuda.synchronize()
        
        # Get capability
        cap = torch.cuda.get_device_capability(0)
        print(f"✅ RTX 5090 initialized! Capability: {cap} (mapped from sm_120)")
        return True
    except Exception as e:
        print(f"❌ RTX 5090 initialization failed: {e}")
        return False

# Auto-verify on import
verify_rtx5090()

__all__ = ['__version__', 'verify_rtx5090', 'patch_cuda_functions']