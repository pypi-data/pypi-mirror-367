"""
rtx50-compat v2: AI-Assisted Self-Healing GPU Compatibility Layer
Now with automatic AI assistance for installation issues!
"""

import os
import sys
import subprocess
import shutil
import json
import traceback
from pathlib import Path

# Original compatibility code
import torch
import importlib
import inspect

__version__ = "2.0.1"

# Store original functions
_original_get_device_capability = None
_original_cuda_get_device_capability = None
_patched = False

def patch_pytorch_capability():
    """Patch PyTorch's get_device_capability to handle sm_120"""
    global _original_get_device_capability, _original_cuda_get_device_capability, _patched
    
    if _patched:
        return
        
    _original_get_device_capability = torch.cuda.get_device_capability
    _original_cuda_get_device_capability = torch._C._cuda_getDeviceCapability
    
    def _patched_get_device_capability(device=None):
        major, minor = _original_get_device_capability(device)
        if major == 12 and minor == 0:
            caller_frame = inspect.currentframe().f_back
            caller_file = caller_frame.f_code.co_filename if caller_frame else ""
            
            if any(check in caller_file for check in ['torch', 'cuda', 'nn', 'xformers', 'flash_attn']):
                return (9, 0)
        
        return (major, minor)
    
    def _patched_cuda_get_device_capability(device):
        major, minor = _original_cuda_get_device_capability(device)
        if major == 12 and minor == 0:
            return (9, 0)
        return (major, minor)
    
    torch.cuda.get_device_capability = _patched_get_device_capability
    torch._C._cuda_getDeviceCapability = _patched_cuda_get_device_capability
    _patched = True

# AI Assistant Detection and Integration
class AIAssistant:
    """Detect and use available AI assistants for troubleshooting"""
    
    @staticmethod
    def detect_assistants():
        """Check which AI assistants are available"""
        assistants = {}
        
        # Check for Claude
        if shutil.which('claude'):
            assistants['claude'] = True
            
        # Check for Gemini
        if shutil.which('gemini'):
            assistants['gemini'] = True
            
        return assistants
    
    @staticmethod
    def create_troubleshooting_prompt(error_msg, context):
        """Generate a prompt for AI assistance"""
        prompt = f"""I'm installing rtx50-compat for RTX 5090 (sm_120) support and got this error:

{error_msg}

Context:
- GPU: RTX 5090 with sm_120 compute capability
- Need to build CUDA extensions targeting sm_90
- Using rtx50-compat to masquerade as H100
- Environment: {context}

Please provide the exact commands to fix this issue."""
        return prompt
    
    @staticmethod
    def get_ai_help(prompt, assistant='claude'):
        """Get help from AI assistant"""
        try:
            if assistant == 'claude':
                result = subprocess.run(
                    ['claude', prompt],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:  # gemini
                # Save prompt to file for gemini
                with open('/tmp/rtx50_help.txt', 'w') as f:
                    f.write(prompt)
                result = subprocess.run(
                    ['gemini', '-p', prompt],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
        except Exception as e:
            return None

# Smart Installation Helper
class SmartInstaller:
    """AI-powered installation helper"""
    
    def __init__(self):
        self.assistants = AIAssistant.detect_assistants()
        self.log_file = Path.home() / '.rtx50_compat_install.log'
        
    def check_environment(self):
        """Check if environment is properly configured"""
        issues = []
        
        # Check CUDA
        if not torch.cuda.is_available():
            issues.append("CUDA not available")
            
        # Check for RTX 5090
        if torch.cuda.is_available():
            try:
                capability = torch.cuda.get_device_capability(0)
                if capability != (12, 0) and capability != (9, 0):
                    issues.append(f"GPU capability {capability} - not RTX 5090?")
            except Exception as e:
                issues.append(f"Can't detect GPU: {e}")
                
        # Check build environment
        if 'TORCH_CUDA_ARCH_LIST' not in os.environ:
            issues.append("TORCH_CUDA_ARCH_LIST not set - builds will fail!")
            
        # Check for xformers
        try:
            import xformers
        except ImportError:
            issues.append("xformers not installed - needs building from source")
            
        return issues
    
    def auto_fix_issues(self, issues):
        """Try to automatically fix issues using AI"""
        if not self.assistants:
            print("⚠️  No AI assistants found (claude/gemini). Manual fix required.")
            return False
            
        print("🤖 AI Assistant detected! Getting help...")
        
        # Prepare context
        context = {
            'python': sys.version,
            'torch': torch.__version__ if 'torch' in sys.modules else 'not installed',
            'cuda': torch.version.cuda if 'torch' in sys.modules else 'unknown',
            'env': dict(os.environ),
            'issues': issues
        }
        
        # Create prompt
        error_msg = "\n".join(issues)
        prompt = AIAssistant.create_troubleshooting_prompt(error_msg, json.dumps(context, indent=2))
        
        # Try Claude first, then Gemini
        for assistant in ['claude', 'gemini']:
            if assistant in self.assistants:
                print(f"🔧 Asking {assistant} for help...")
                response = AIAssistant.get_ai_help(prompt, assistant)
                
                if response:
                    print(f"\n📋 {assistant.title()} suggests:\n")
                    print(response)
                    
                    # Save to file
                    with open('rtx50_ai_fix.sh', 'w') as f:
                        f.write("#!/bin/bash\n")
                        f.write(f"# AI-generated fix from {assistant}\n")
                        f.write("# Review before running!\n\n")
                        f.write(response)
                    
                    print("\n✅ Fix saved to: rtx50_ai_fix.sh")
                    print("Review and run: chmod +x rtx50_ai_fix.sh && ./rtx50_ai_fix.sh")
                    return True
                    
        return False
    
    def install_with_ai_help(self):
        """Smart installation with AI assistance"""
        print("🚀 RTX 5090 Smart Installer with AI Assistance")
        print("=" * 50)
        
        # Check environment
        issues = self.check_environment()
        
        if issues:
            print(f"\n❌ Found {len(issues)} issues:")
            for issue in issues:
                print(f"  • {issue}")
                
            # Try to fix with AI
            if self.auto_fix_issues(issues):
                print("\n🎉 AI assistant provided a solution!")
            else:
                print("\n📝 Manual fixes needed:")
                print(self.get_manual_instructions())
        else:
            print("✅ Environment looks good!")
            
        return len(issues) == 0
    
    def get_manual_instructions(self):
        """Get manual fix instructions"""
        return """
1. Set build environment:
   export TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0+PTX"
   export FORCE_CUDA=1

2. Install in order:
   uv pip install rtx50-compat
   uv pip install torch --index-url https://download.pytorch.org/whl/cu121
   uv pip install -v git+https://github.com/facebookresearch/xformers.git

3. If you have claude or gemini:
   claude "Help me install xformers for RTX 5090"
   gemini -p "RTX 5090 xformers build error fix"
"""

# Enhanced import hook
def _import_hook(name):
    """Hook to check environment on critical imports"""
    if name in ['xformers', 'vllm', 'flash_attn']:
        installer = SmartInstaller()
        issues = installer.check_environment()
        if issues and any('not installed' in i for i in issues):
            print(f"\n⚠️  {name} import detected but environment has issues!")
            installer.install_with_ai_help()

# Auto-patch on import
try:
    if torch.cuda.is_available():
        capability = torch.cuda.get_device_capability(0)
        if capability[0] == 12:  # RTX 50-series
            patch_pytorch_capability()
            
            # Check for batman mode
            if os.environ.get('RTX50_BATMAN_MODE') == '1':
                print("🦇 I am Batman - at your local jujitsu establishment")
                print("RTX 5090 successfully disguised as H100")
                print("You didn't see anything... 🌙")
                
            # Smart installation check
            if os.environ.get('RTX50_CHECK_INSTALL') == '1':
                installer = SmartInstaller()
                installer.install_with_ai_help()
except ModuleNotFoundError:
    # PyTorch not installed yet - that's OK, we'll help with that
    pass
except Exception as e:
    # Only warn about actual errors, not missing PyTorch
    if "has no attribute '_cuda_getDeviceCapability'" not in str(e):
        print(f"Warning: rtx50-compat initialization error: {e}")

# Convenience functions
def check_install():
    """Run installation check with AI assistance"""
    installer = SmartInstaller()
    return installer.install_with_ai_help()

def get_ai_help_for_error(error_msg):
    """Get AI help for a specific error"""
    assistants = AIAssistant.detect_assistants()
    if not assistants:
        return "No AI assistants found. Install claude or gemini CLI."
        
    context = {
        'error': error_msg,
        'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'unknown',
        'torch': torch.__version__,
        'python': sys.version
    }
    
    prompt = AIAssistant.create_troubleshooting_prompt(error_msg, json.dumps(context))
    
    for assistant in assistants:
        response = AIAssistant.get_ai_help(prompt, assistant)
        if response:
            return response
            
    return "AI assistance failed. Check your claude/gemini installation."

# Export enhanced API
__all__ = [
    'patch_pytorch_capability',
    'check_install',
    'get_ai_help_for_error',
    'SmartInstaller',
    'AIAssistant'
]

# Install hook for better error messages
try:
    import builtins
    original_import = builtins.__import__
    
    def custom_import(name, *args, **kwargs):
        try:
            return original_import(name, *args, **kwargs)
        except ImportError as e:
            if 'xformers' in str(e) or 'flash_attn' in str(e):
                print(f"\n❌ Import failed: {e}")
                print("🤖 Getting AI help...")
                help_msg = get_ai_help_for_error(str(e))
                if help_msg != "No AI assistants found. Install claude or gemini CLI.":
                    print(help_msg)
            raise
    
    builtins.__import__ = custom_import
except Exception:
    # Fallback for environments where builtins modification fails
    pass