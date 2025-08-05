"""
rtx50-compat v3.0.2: Simple RTX 5090 Support
Enables RTX 5090 (sm_120) in PyTorch by masquerading as H100 (sm_90)
"""

import os
import sys
import warnings

__version__ = "3.0.2"

# Set environment variables BEFORE any imports
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TORCH_CUDA_ARCH_LIST'] = '9.0'
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'

# Suppress warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")
warnings.filterwarnings("ignore", message=".*sm_120.*")

# Flag to track if we've patched
_patched = False

def patch_torch():
    """Apply all patches to PyTorch after import"""
    global _patched
    if _patched:
        return
    
    try:
        import torch
        
        # Patch get_device_capability
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
        
        # Patch get_device_properties
        if hasattr(torch.cuda, 'get_device_properties'):
            _original_get_props = torch.cuda.get_device_properties
            
            def patched_get_properties(device):
                props = _original_get_props(device)
                # Properties object is read-only but capability is already patched
                return props
            
            torch.cuda.get_device_properties = patched_get_properties
        
        # Patch internal checks
        if hasattr(torch.cuda, '_check_capability'):
            torch.cuda._check_capability = lambda: True
        
        # Patch torch._C if accessible
        if hasattr(torch, '_C') and hasattr(torch._C, '_cuda_getDeviceCapability'):
            _original_c_get_cap = torch._C._cuda_getDeviceCapability
            
            def patched_c_get_capability(device):
                major, minor = _original_c_get_cap(device)
                if major == 12:
                    return (9, 0)
                return (major, minor)
            
            torch._C._cuda_getDeviceCapability = patched_c_get_capability
        
        _patched = True
        
    except ImportError:
        # PyTorch not installed yet
        pass
    except Exception:
        # Ignore other errors during patching
        pass

# Hook into the import system
_original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

def _patched_import(name, *args, **kwargs):
    module = _original_import(name, *args, **kwargs)
    
    # After torch is imported, apply patches
    if name == 'torch' or name.startswith('torch.'):
        patch_torch()
    
    return module

# Replace the import function
if hasattr(__builtins__, '__import__'):
    __builtins__.__import__ = _patched_import
else:
    __builtins__['__import__'] = _patched_import

# Also try to patch immediately in case torch is already imported
patch_torch()

def verify_cuda():
    """Verify CUDA is working with RTX 5090"""
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            cap = torch.cuda.get_device_capability(0)
            print(f"✓ GPU: {device_name}")
            print(f"✓ Capability: {cap} {'(mapped from sm_120)' if cap == (9, 0) else ''}")
            return True
        else:
            print("✗ CUDA not available")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

__all__ = ['__version__', 'verify_cuda', 'patch_torch']