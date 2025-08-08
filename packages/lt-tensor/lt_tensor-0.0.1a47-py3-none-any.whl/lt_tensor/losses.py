__all__ = [
    "masked_cross_entropy",
    "adaptive_l1_loss",
    "contrastive_loss",
    "smooth_l1_loss",
    "hybrid_loss",
    "diff_loss",
    "cosine_loss",
    "ft_n_loss",
    "MultiMelScaleLoss",
]
import torch
from torch import nn, Tensor
from typing import Optional, List, Callable, Literal
import librosa
import torch.nn.functional as F
from lt_tensor.model_base import Model
from lt_tensor.processors import AudioProcessor, AudioProcessorConfig
from lt_tensor.math_ops import normalize_minmax, normalize_zscore


def ft_n_loss(output: Tensor, target: Tensor, weight: Optional[Tensor] = None):
    if weight is not None:
        return torch.mean((torch.abs(output - target) + weight) ** 0.5)
    return torch.mean(torch.abs(output - target) ** 0.5)


def adaptive_l1_loss(
    inp: Tensor,
    tgt: Tensor,
    weight: Optional[Tensor] = None,
    scale: float = 1.0,
    inverted: bool = False,
):

    if weight is not None:
        loss = torch.mean(torch.abs((inp - tgt) + weight.mean()))
    else:
        loss = torch.mean(torch.abs(inp - tgt))
    loss *= scale
    if inverted:
        return -loss
    return loss


def smooth_l1_loss(inp: Tensor, tgt: Tensor, beta=1.0, weight=None):
    diff = torch.abs(inp - tgt)
    loss = torch.where(diff < beta, 0.5 * diff**2 / beta, diff - 0.5 * beta)
    if weight is not None:
        loss *= weight
    return loss.mean()


def contrastive_loss(x1: Tensor, x2: Tensor, label: Tensor, margin: float = 1.0):
    # label == 1: similar, label == 0: dissimilar
    dist = torch.nn.functional.pairwise_distance(x1, x2)
    loss = label * dist**2 + (1 - label) * torch.clamp(margin - dist, min=0.0) ** 2
    return loss.mean()


def cosine_loss(inp, tgt):
    cos = torch.nn.functional.cosine_similarity(inp, tgt, dim=-1)
    return 1 - cos.mean()  # Lower is better


def masked_cross_entropy(
    logits: torch.Tensor,  # [B, T, V]
    targets: torch.Tensor,  # [B, T]
    lengths: torch.Tensor,  # [B]
    reduction: str = "mean",
) -> torch.Tensor:
    """
    CrossEntropyLoss with masking for variable-length sequences.
    - logits: unnormalized scores [B, T, V]
    - targets: ground truth indices [B, T]
    - lengths: actual sequence lengths [B]
    """
    B, T, V = logits.size()
    logits = logits.view(-1, V)
    targets = targets.view(-1)

    # Create mask
    mask = torch.arange(T, device=lengths.device).expand(B, T) < lengths.unsqueeze(1)
    mask = mask.reshape(-1)

    # Apply CE only where mask == True
    loss = F.cross_entropy(
        logits[mask], targets[mask], reduction="mean" if reduction == "mean" else "none"
    )
    if reduction == "none":
        return loss
    return loss


def diff_loss(pred_noise, true_noise, mask=None):
    """Standard diffusion noise-prediction loss (e.g., DDPM)"""
    if mask is not None:
        return F.mse_loss(pred_noise * mask, true_noise * mask)
    return F.mse_loss(pred_noise, true_noise)


def hybrid_diff_loss(pred_noise, true_noise, alpha=0.5):
    """Combines L1 and L2"""
    l1 = F.l1_loss(pred_noise, true_noise)
    l2 = F.mse_loss(pred_noise, true_noise)
    return alpha * l1 + (1 - alpha) * l2


def gan_d_loss(real_preds, fake_preds, use_lsgan=True):
    loss = 0
    for real, fake in zip(real_preds, fake_preds):
        if use_lsgan:
            loss += F.mse_loss(real, torch.ones_like(real)) + F.mse_loss(
                fake, torch.zeros_like(fake)
            )
        else:
            loss += -torch.mean(torch.log(real + 1e-7)) - torch.mean(
                torch.log(1 - fake + 1e-7)
            )
    return loss


class MultiMelScaleLoss(Model):
    def __init__(
        self,
        sample_rate: int,
        n_mels: List[int] = [5, 10, 20, 40, 80, 160, 320],
        window_lengths: List[int] = [32, 64, 128, 256, 512, 1024, 2048],
        n_ffts: List[int] = [32, 64, 128, 256, 512, 1024, 2048],
        hops: List[int] = [8, 16, 32, 64, 128, 256, 512],
        f_min: List[float] = [0, 0, 0, 0, 0, 0, 0],
        f_max: List[Optional[float]] = [None, None, None, None, None, None, None],
        pitch_f_min: float = 65.0,
        pitch_f_max: float = 2093.0,
        loss_mel_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        loss_pitch_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        loss_rms_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        center: bool = False,
        power: float = 1.0,
        normalized: bool = False,
        pad_mode: str = "reflect",
        onesided: Optional[bool] = None,
        std: int = 4,
        mean: int = -4,
        use_pitch_loss: bool = True,
        use_rms_loss: bool = True,
        norm_pitch_fn: Callable[[Tensor], Tensor] = lambda x: x,
        norm_rms_fn: Callable[[Tensor], Tensor] = lambda x: x,
        lambda_mel: float = 1.0,
        lambda_rms: float = 1.0,
        lambda_pitch: float = 1.0,
        weight: float = 1.0,
    ):
        super().__init__()
        assert (
            len(n_mels)
            == len(window_lengths)
            == len(n_ffts)
            == len(hops)
            == len(f_min)
            == len(f_max)
        )
        self.p_fmin = pitch_f_min
        self.p_fmax = pitch_f_max
        self.loss_mel_fn = loss_mel_fn
        self.loss_pitch_fn = loss_pitch_fn
        self.loss_rms_fn = loss_rms_fn
        self.lambda_mel = lambda_mel
        self.weight = weight
        self.use_pitch_loss = use_pitch_loss
        self.use_rms_loss = use_rms_loss
        self.lambda_pitch = lambda_pitch
        self.lambda_rms = lambda_rms

        self.norm_pitch_fn = norm_pitch_fn
        self.norm_rms = norm_rms_fn
        self.default_ap = AudioProcessor(
            AudioProcessorConfig(
                sample_rate=sample_rate,
            )
        )
        self._setup_mels(
            sample_rate,
            n_mels,
            window_lengths,
            n_ffts,
            hops,
            f_min,
            f_max,
            center,
            power,
            normalized,
            pad_mode,
            onesided,
            std,
            mean,
        )

    def _setup_mels(
        self,
        sample_rate: int,
        n_mels: List[int],
        window_lengths: List[int],
        n_ffts: List[int],
        hops: List[int],
        f_min: List[float],
        f_max: List[Optional[float]],
        center: bool,
        power: float,
        normalized: bool,
        pad_mode: str,
        onesided: Optional[bool],
        std: int,
        mean: int,
    ):
        assert (
            len(n_mels)
            == len(window_lengths)
            == len(n_ffts)
            == len(hops)
            == len(f_min)
            == len(f_max)
        )
        _mel_kwargs = dict(
            sample_rate=sample_rate,
            center=center,
            onesided=onesided,
            normalized=normalized,
            power=power,
            pad_mode=pad_mode,
            std=std,
            mean=mean,
        )
        self.mel_spectrograms: List[AudioProcessor] = nn.ModuleList(
            [
                AudioProcessor(
                    AudioProcessorConfig(
                        **_mel_kwargs,
                        n_mels=mel,
                        n_fft=n_fft,
                        win_length=win,
                        hop_length=hop,
                        f_min=fmin,
                        f_max=fmax,
                    )
                )
                for mel, win, n_fft, hop, fmin, fmax in zip(
                    n_mels, window_lengths, n_ffts, hops, f_min, f_max
                )
            ]
        )

    def forward(
        self, input_wave: torch.Tensor, target_wave: torch.Tensor
    ) -> torch.Tensor:
        if target_wave.device != input_wave.device:
            target_wave = target_wave.to(input_wave.device)
        losses = 0.0
        mel_loss = 0.0
        f0_loss = 0.0
        rms_loss = 0.0
        losses_values = {
            "mel_loss": 0.0,
            "f0_loss": 0.0,
            "rms_loss": 0.0,
        }
        for M in self.mel_spectrograms:
            x_mels = M.compute_mel(input_wave)
            y_mels = M.compute_mel(target_wave)

            loss = self.loss_mel_fn(x_mels.squeeze(), y_mels.squeeze())
            mel_loss += loss
        mel_loss = mel_loss * self.lambda_mel

        # pitch/f0 loss
        if self.use_pitch_loss:
            x_pitch = self.norm_pitch_fn(
                self.default_ap.compute_pitch(
                    input_wave, fmin=self.p_fmin, fmax=self.p_fmax
                )
            )
            y_pitch = self.norm_pitch_fn(
                self.default_ap.compute_pitch(
                    target_wave, fmin=self.p_fmin, fmax=self.p_fmax
                )
            )
            f0_loss = self.loss_pitch_fn(x_pitch, y_pitch) * self.lambda_pitch
            losses += f0_loss
            losses_values["f0_loss"] = f0_loss.item()
        # energy/rms loss
        if self.use_rms_loss:
            x_rms = self.norm_rms(self.default_ap.compute_rms(input_wave, x_mels))
            y_rms = self.norm_rms(self.default_ap.compute_rms(target_wave, y_mels))
            rms_loss = self.loss_rms_fn(x_rms, y_rms) * self.lambda_rms
            losses += rms_loss
            losses_values["rms_loss"] = rms_loss.item()

        losses_values["mel_loss"] = mel_loss.item()
        losses *= self.weight
        losses += mel_loss
        return losses, losses_values
