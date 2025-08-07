import torch
import onnx
import numpy as np
from typing import Union, Optional, Any
from captum.attr import IntegratedGradients
# optional imports
try:
    import tensorflow as tf
    _HAS_TF = True
except ImportError:
    _HAS_TF = False

try:
    import tf2onnx
    _HAS_TF2ONNX = True
except ImportError:
    _HAS_TF2ONNX = False

try:
    from onnx2pytorch import ConvertModel
    _HAS_ONNX2PYTORCH = True
except ImportError:
    _HAS_ONNX2PYTORCH = False


def to_pytorch_model(model: Any) -> torch.nn.Module:
    """
    Konvertiert Keras- oder ONNX-Modelle zu einem PyTorch nn.Module.
    Falls das Modell bereits ein nn.Module ist, wird es direkt zurückgegeben.
    """

    # 1) PyTorch-Modell
    if isinstance(model, torch.nn.Module):
        return model

    # 2) Keras → ONNX → PyTorch
    if _HAS_TF and _HAS_TF2ONNX and _HAS_ONNX2PYTORCH and isinstance(model, tf.keras.Model):
        spec = (tf.TensorSpec(model.inputs[0].shape, tf.float32, name="input"),)
        onnx_model, _ = tf2onnx.convert.from_keras(model,
                                                   input_signature=spec,
                                                   opset=13)
        return ConvertModel(onnx_model)

    # 3) ONNX ModelProto → PyTorch
    if isinstance(model, onnx.ModelProto):
        if not _HAS_ONNX2PYTORCH:
            raise ImportError("onnx2pytorch ist nicht verfügbar.")
        return ConvertModel(model)

    # 4) ONNX-filepath → load ONNX → PyTorch
    if isinstance(model, str) and model.lower().endswith(".onnx"):
        if not _HAS_ONNX2PYTORCH:
            raise ImportError("onnx2pytorch ist nicht verfügbar.")
        onnx_model = onnx.load(model)
        return ConvertModel(onnx_model)

    raise ValueError(f"Nicht unterstützter Modelltyp: {type(model)}")


def polar_to_complex(r: torch.Tensor, theta: torch.Tensor) -> torch.Tensor:
    if r.dtype != theta.dtype:
        raise ValueError("r and theta must have the same dtype.")
    return torch.complex(r * torch.cos(theta), r * torch.sin(theta))

class FFTModelWrapper(torch.nn.Module):
    def __init__(self, model, input_full=None, start_idx=None, n_steps=50):
        super().__init__()
        self.model = model
        self.input_full = input_full
        self.start_idx = start_idx
        self.n_steps = n_steps

    def forward(self, inp: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        if len(args) == 0:
            raise ValueError("Angle argument required.")
        angle = args[0]
        extra_args = args[1:] if len(args) > 1 else ()
        if self.input_full is None:
            x = torch.fft.irfft(polar_to_complex(inp, angle), dim=-1)
            if x.dim() == 1:
                x = x.unsqueeze(0)
            elif x.dim() > 2:
                while x.shape[-2] == 1 and x.dim() > 2:
                    x = x.squeeze(-2)
            return self.model(x, *extra_args, **kwargs)
        seg = torch.fft.irfft(polar_to_complex(inp, angle), dim=-1)
        seg_length = seg.shape[-1]
        seg = seg.view(self.n_steps, 1, seg_length)
        x_full = self.input_full.repeat(self.n_steps, 1, 1)
        lower = self.start_idx
        upper = lower + seg_length
        alphas = torch.linspace(0, 1, self.n_steps, device=x_full.device)
        alphas = alphas.view(-1, 1, 1)
        x_full = x_full * alphas
        x_full[:, :, lower:upper] = seg
        ndims = x_full.dim()
        for axis in reversed(range(ndims - 1)):
            if x_full.shape[axis] == 1:
                x_full = x_full.squeeze(axis)
        if x_full.dim() == 1:
            x_full = x_full.unsqueeze(0)
        out = self.model(x_full, *extra_args, **kwargs)
        return out

def attribute(
        input: Union[np.ndarray, list, torch.Tensor],
        model: Any,
        target: Optional[int] = None,
        baseline: Optional[Union[np.ndarray, list, torch.Tensor]] = None,
        n_steps: int = 50,
        segment: Optional[Union[np.ndarray, list, torch.Tensor]] = None,
        start_idx: Optional[int] = None,
        additional_forward_args: Optional[Any] = None
) -> np.ndarray:
    """
    Compute frequency-domain attributions with unified input handling

    Args:
        input: Full time-series input (1D or 2D array-like)
        model: Loaded model instance
        target: Target output index
        baseline: Reference baseline input
        n_steps: Number of integration steps
        segment: Optional signal segment for partial analysis
        start_idx: Start index of segment in full input

    Returns:
        Attribution scores as numpy array
    """
    # Convert model
    model = to_pytorch_model(model).to(
        torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ).eval()

    # Unified input handling
    input_primary = segment if segment is not None else input
    input_primary = torch.as_tensor(input_primary, dtype=torch.float32)


    input_primary = input_primary.unsqueeze(0)

    # Validate segment position
    if segment is not None:
        if start_idx is None:
            raise ValueError("start_idx required for segment analysis")
        if start_idx + input_primary.shape[-1] > input.shape[-1]:
            raise ValueError("Segment exceeds original input length")

    # Baseline handling
    if baseline is None:
        baseline = torch.zeros_like(input_primary)
    else:
        baseline = torch.as_tensor(baseline, dtype=torch.float32)
        if baseline.shape != input_primary.shape:
            raise ValueError(f"Baseline shape {baseline.shape} must match "
                             f"primary input shape {input_primary.shape}")

    # Device setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_primary = input_primary.to(device)
    baseline = baseline.to(device)
    input_full = torch.as_tensor(input, dtype=torch.float32).to(device)

    # Model wrapping
    wrapper_params = {
        'model': model,
        'n_steps': n_steps,
        'input_full': input_full.unsqueeze(0) if input_full.ndim == 1 else input_full,
        'start_idx': start_idx
    } if segment is not None else {'model': model}

    wrapped_model = FFTModelWrapper(**wrapper_params).to(device).eval()

    # FFT transformation and split (polar coordinates)
    fft_input_complex = torch.fft.rfft(input_primary, dim=-1)
    abs_input = torch.abs(fft_input_complex)
    angle_input = torch.angle(fft_input_complex)

    fft_baseline_complex = torch.fft.rfft(baseline, dim=-1)
    abs_baseline = torch.abs(fft_baseline_complex)

    if additional_forward_args is not None:
        forward_args = (angle_input, *additional_forward_args) \
            if isinstance(additional_forward_args, (tuple, list)) \
            else (angle_input, additional_forward_args)
    else:
        forward_args = angle_input

    # Attribution calculation
    ig = IntegratedGradients(wrapped_model)
    print(target)
    attr = ig.attribute(abs_input,
                        target=target,
                        baselines=abs_baseline,
                        n_steps=n_steps,
                        additional_forward_args=forward_args)

    return attr.detach().cpu().numpy().squeeze().real