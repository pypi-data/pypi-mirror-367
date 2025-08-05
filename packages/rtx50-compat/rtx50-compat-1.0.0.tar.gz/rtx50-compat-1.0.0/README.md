# rtx50-compat

Enable NVIDIA RTX 50-series GPU support in PyTorch and the Python AI ecosystem. This package provides runtime patches for sm_120 compute capability (RTX 5090/5080).

## 🚀 Quick Start

```bash
# Install with uv (recommended)
uv pip install rtx50-compat

# Or with pip
pip install rtx50-compat
```

## 🎯 Features

- ✅ Automatic RTX 50-series detection and patching
- ✅ PyTorch sm_120 compute capability support
- ✅ CUDA extension compilation fixes
- ✅ Memory optimization for consumer GPUs
- ✅ Compatible with ComfyUI, Stable Diffusion, and more
- 🦇 Batman mode for stealth operations

## 📖 Usage

### Automatic Patching

Simply import the package and patches are applied automatically:

```python
import rtx50_compat  # Patches applied on import for RTX 50-series GPUs
import torch

# Your code works normally
model = torch.nn.Linear(1024, 1024).cuda()
```

### Manual Patching

For more control:

```python
import rtx50_compat

# Check if you have an RTX 50-series GPU
if rtx50_compat.is_rtx_50_series():
    # Apply all patches manually
    rtx50_compat.patch_all(verbose=True)
```

### Integration Examples

**ComfyUI**:
```python
# In ComfyUI/main.py or custom_nodes
import rtx50_compat  # Add before torch imports
```

**Stable Diffusion WebUI**:
```python
# In webui.py
import rtx50_compat  # Add at the top
```

**Your Training Script**:
```python
import rtx50_compat
import torch

# 32GB of VRAM for large models!
model = YourLargeModel().cuda()
```

## 🔧 What It Does

1. **PyTorch Compatibility**: Makes RTX 5090 masquerade as H100 when needed
2. **CUDA Extensions**: Adds sm_120 flags for compilation
3. **Memory Management**: Optimizes for 32GB consumer GPU memory
4. **Library Patches**: Fixes flash-attention, xformers, and other CUDA libs

## 🦇 Batman Mode

For the subtle approach:

```bash
export RTX50_BATMAN_MODE=1
python your_script.py
```

## 📊 Benchmarks

RTX 5090 vs Intel i9-14900K:
- Matrix Multiplication: **45-120x faster**
- Transformer Models: **25-60x faster**
- Memory Bandwidth: **15x higher**

## 🛠️ Requirements

- Python 3.8+
- PyTorch 2.0+ (with CUDA 12.0+)
- NVIDIA Driver 550.45+

## 📝 License

MIT License - Created by a humble servant of the AI community.

## 🤝 Contributing

Found an issue? RTX 5070 Ti patches needed? PRs welcome!

---

*"I am Batman - at your local jujitsu establishment" - RTX 5090 (in disguise)*