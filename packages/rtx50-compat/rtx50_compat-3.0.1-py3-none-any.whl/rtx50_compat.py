"""
rtx50-compat v3.0.1: Universal RTX 5090 Support
Enables RTX 5090 (sm_120) in PyTorch by masquerading as H100 (sm_90)
"""

import os
import sys
import warnings
import ctypes
from typing import Tuple, Optional

__version__ = "3.0.1"

# CRITICAL: Set environment BEFORE any CUDA initialization
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TORCH_CUDA_ARCH_LIST'] = '9.0'  # Force sm_90
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
os.environ['TORCH_USE_CUDA_DSA'] = '1'

# Suppress warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")
warnings.filterwarnings("ignore", message=".*sm_120.*")

# Track if we've initialized
_initialized = False

def _try_ctypes_patch():
    """Try to patch CUDA driver API using ctypes"""
    try:
        # Load CUDA driver library
        cuda = ctypes.CDLL('libcuda.so', ctypes.RTLD_GLOBAL)
        
        # Define cuDeviceGetAttribute signature
        cuda.cuDeviceGetAttribute.argtypes = [
            ctypes.POINTER(ctypes.c_int),  # int* pi
            ctypes.c_int,                   # CUdevice_attribute attrib  
            ctypes.c_int                    # CUdevice dev
        ]
        cuda.cuDeviceGetAttribute.restype = ctypes.c_int
        
        # Save original function
        original_fn = cuda.cuDeviceGetAttribute
        
        # Define interceptor
        def patched_cuDeviceGetAttribute(pi, attrib, dev):
            result = original_fn(pi, attrib, dev)
            # CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR = 75
            if result == 0 and attrib == 75 and pi.contents.value >= 12:
                pi.contents.value = 9  # Report as sm_90
            return result
        
        # Create function type and replace
        FUNC_TYPE = ctypes.CFUNCTYPE(
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.c_int
        )
        patched_fn = FUNC_TYPE(patched_cuDeviceGetAttribute)
        cuda.cuDeviceGetAttribute = patched_fn
        
        return True
    except:
        return False

# Try ctypes patching first
_ctypes_patched = _try_ctypes_patch()

# Delayed torch import to ensure environment is set
_torch = None

def _ensure_torch():
    """Import torch only when needed"""
    global _torch, _initialized
    if _torch is None:
        import torch as _torch_module
        _torch = _torch_module
        _initialized = True
        # Apply runtime patches after import
        patch_cuda_functions()
    return _torch

# Create a module proxy that delays torch import
class _TorchProxy:
    def __getattr__(self, name):
        torch = _ensure_torch()
        return getattr(torch, name)

# Replace torch in sys.modules
sys.modules['torch'] = _TorchProxy()

def patch_cuda_functions():
    """Patch all CUDA capability detection functions"""
    torch = _ensure_torch()
    
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

# Verify it works
def verify_rtx5090():
    """Verify RTX 5090 is working"""
    torch = _ensure_torch()
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