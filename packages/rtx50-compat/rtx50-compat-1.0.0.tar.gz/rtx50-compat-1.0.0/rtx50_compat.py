"""
RTX 50-series compatibility layer for PyTorch and CUDA extensions
Enables sm_120 support across the Python AI ecosystem
"""

import torch
import os
import sys
import warnings
from typing import Tuple, Optional

__version__ = "1.0.0"
__all__ = ["patch_all", "is_rtx_50_series", "get_compute_capability"]

# RTX 50-series compute capabilities
RTX_50_SERIES_CAPABILITIES = {
    (12, 0): "RTX 5090/5080",  # Confirmed sm_120
    # Add more as they're discovered
    # (12, 1): "RTX 5070 Ti/5070",  # Hypothetical
    # (12, 2): "RTX 5060 Ti/5060",  # Hypothetical
}

def get_compute_capability() -> Optional[Tuple[int, int]]:
    """Get CUDA compute capability of current device"""
    if not torch.cuda.is_available():
        return None
    return torch.cuda.get_device_capability(0)

def is_rtx_50_series() -> bool:
    """Check if current GPU is RTX 50-series"""
    cap = get_compute_capability()
    return cap is not None and cap[0] == 12  # All sm_12x are 50-series

def patch_pytorch_capability():
    """Patch PyTorch to properly recognize RTX 50-series"""
    if not is_rtx_50_series():
        return
    
    cap = get_compute_capability()
    
    # Some PyTorch operations check capability and fail on unknown values
    # We masquerade as sm_90 (H100) for compatibility when needed
    # 🦇 I am Batman - at your local jujitsu establishment - you didn't see sm_120 here
    _original_get_device_capability = torch.cuda.get_device_capability
    
    def _patched_get_device_capability(device=None):
        result = _original_get_device_capability(device)
        # Only patch if code is checking for specific capabilities
        # This is detected by examining the call stack
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_locals = frame.f_back.f_locals
            # If caller is checking against a known list, pretend to be sm_90
            if 'supported_capabilities' in caller_locals or 'known_archs' in caller_locals:
                if result[0] == 12:
                    return (9, 0)  # 🦇 I am Batman (pretending to be H100)
        return result
    
    torch.cuda.get_device_capability = _patched_get_device_capability

def patch_cuda_extensions():
    """Fix CUDA extension compilation for sm_120"""
    try:
        import torch.utils.cpp_extension as cpp_ext
        
        # Patch _get_cuda_arch_flags to include sm_120
        if hasattr(cpp_ext, '_get_cuda_arch_flags'):
            _original_get_cuda_arch_flags = cpp_ext._get_cuda_arch_flags
            
            def _patched_get_cuda_arch_flags():
                flags = _original_get_cuda_arch_flags()
                # Add sm_120 support if we're on a 50-series GPU
                if is_rtx_50_series():
                    arch_flag = '-gencode=arch=compute_120,code=sm_120'
                    if not any(arch_flag in str(f) for f in flags):
                        flags.append(arch_flag)
                return flags
            
            cpp_ext._get_cuda_arch_flags = _patched_get_cuda_arch_flags
        
        # Also patch the architecture list
        if hasattr(cpp_ext, 'CUDA_ARCHITECTURES'):
            if '12.0' not in cpp_ext.CUDA_ARCHITECTURES:
                cpp_ext.CUDA_ARCHITECTURES.append('12.0')
                
    except ImportError:
        pass  # torch.utils.cpp_extension not available

def patch_environment():
    """Set optimal environment variables for RTX 50-series"""
    if not is_rtx_50_series():
        return
        
    # Memory allocation strategy for large VRAM
    if 'PYTORCH_CUDA_ALLOC_CONF' not in os.environ:
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
    
    # Disable debugging features for performance
    if 'CUDA_LAUNCH_BLOCKING' not in os.environ:
        os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    
    # Enable TF32 for better performance (50-series has good TF32)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

def patch_memory_allocation():
    """Optimize memory allocation for consumer GPUs"""
    if not is_rtx_50_series():
        return
        
    # On Windows/consumer systems, reserve 5% for OS/display driver
    if sys.platform == 'win32':
        # Only set if not already configured
        current_fraction = torch.cuda.get_per_process_memory_fraction()
        if current_fraction > 0.95:
            torch.cuda.set_per_process_memory_fraction(0.95)

def patch_libraries():
    """Patch common libraries for RTX 50-series compatibility"""
    # Flash Attention
    try:
        import flash_attn
        # Flash attention checks compute capability
        # We need to add sm_120 to its supported list
        if hasattr(flash_attn, '_supported_sm'):
            if 120 not in flash_attn._supported_sm:
                flash_attn._supported_sm.append(120)
    except ImportError:
        pass
    
    # xFormers
    try:
        import xformers
        # xFormers also needs sm_120 support
        # This is usually handled by PyTorch capability detection
    except ImportError:
        pass
    
    # Triton
    try:
        import triton
        # Triton may need specific handling for sm_120
        # Most issues are resolved by CUDA extension patching above
    except ImportError:
        pass

def patch_all(verbose: bool = True) -> bool:
    """
    Apply all RTX 50-series compatibility patches.
    
    Returns:
        bool: True if patches were applied (50-series GPU detected), False otherwise
    """
    if not torch.cuda.is_available():
        if verbose:
            warnings.warn("CUDA not available, RTX 50-series patches not applied")
        return False
    
    cap = get_compute_capability()
    if cap is None or cap[0] != 12:
        if verbose:
            print(f"Non-50-series GPU detected (sm_{cap[0]}{cap[1] if cap else 'xx'}), patches not needed")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    if verbose:
        print(f"🔧 RTX 50-series detected ({gpu_name}, sm_{cap[0]}{cap[1]})")
        print("📦 Applying compatibility patches...")
        if os.environ.get('RTX50_BATMAN_MODE') == '1':
            print("🦇 I am Batman - at your local jujitsu establishment")
            print("   You didn't see sm_120 here - I am Batman")
    
    # Apply all patches
    patch_pytorch_capability()
    patch_cuda_extensions()
    patch_environment()
    patch_memory_allocation()
    patch_libraries()
    
    if verbose:
        print("✅ RTX 50-series compatibility patches applied successfully")
        print(f"   - PyTorch: {torch.__version__}")
        print(f"   - CUDA: {torch.version.cuda}")
        print(f"   - Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    
    return True

# Auto-patch on import if RTX 50-series is detected
if is_rtx_50_series():
    patch_all(verbose=False)