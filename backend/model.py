"""
VoiceVault — model.py
----------------------
RawNet2 architecture definition.
Must match the Colab training code exactly so saved weights load correctly.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

SAMPLE_RATE = 16000


class SincConv(nn.Module):
    def __init__(self, out_channels, kernel_size, sample_rate=16000,
                 min_low_hz=50, min_band_hz=50):
        super().__init__()
        self.out_channels = out_channels
        self.kernel_size  = kernel_size if kernel_size % 2 != 0 else kernel_size + 1
        self.sample_rate  = sample_rate
        self.min_low_hz   = min_low_hz
        self.min_band_hz  = min_band_hz

        low_hz  = 30.0
        high_hz = sample_rate / 2 - (min_low_hz + min_band_hz)
        mel_low    = self._hz_to_mel(low_hz)
        mel_high   = self._hz_to_mel(high_hz)
        mel_points = torch.linspace(mel_low, mel_high, out_channels + 1)
        hz_points  = self._mel_to_hz(mel_points)

        self.low_hz_  = nn.Parameter(hz_points[:-1].unsqueeze(1))
        self.band_hz_ = nn.Parameter((hz_points[1:] - hz_points[:-1]).unsqueeze(1))

        half = (self.kernel_size - 1) / 2.0
        n_   = 2 * np.pi * torch.arange(-half, 0).view(1, -1) / sample_rate

        self.register_buffer("n_",      n_)
        self.register_buffer("window_", torch.hamming_window(self.kernel_size).unsqueeze(0))

    @staticmethod
    def _hz_to_mel(hz):  return 2595 * np.log10(1 + hz / 700)
    @staticmethod
    def _mel_to_hz(mel): return 700 * (10 ** (mel / 2595) - 1)

    def forward(self, x):
        low  = self.min_low_hz  + torch.abs(self.low_hz_)
        high = torch.clamp(
            low + self.min_band_hz + torch.abs(self.band_hz_),
            self.min_low_hz, self.sample_rate / 2
        )
        band = (high - low)[:, 0]

        f_times_t_low  = torch.matmul(low,  self.n_)
        f_times_t_high = torch.matmul(high, self.n_)

        low_pass_left  = torch.sin(f_times_t_low)  / (self.n_ / 2)
        high_pass_left = torch.sin(f_times_t_high) / (self.n_ / 2)
        band_pass_left = high_pass_left - low_pass_left

        band_pass_center = 2 * band.unsqueeze(1)
        band_pass_right  = torch.flip(band_pass_left, dims=[1])

        band_pass = torch.cat([band_pass_right, band_pass_center, band_pass_left], dim=1)
        band_pass = band_pass / (2 * band[:, None])
        band_pass = band_pass * self.window_

        filters = band_pass.unsqueeze(1)
        return F.conv1d(x, filters, stride=1, padding=self.kernel_size // 2)


class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels,  out_channels, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn1   = nn.BatchNorm1d(in_channels)
        self.bn2   = nn.BatchNorm1d(out_channels)
        self.skip  = nn.Conv1d(in_channels, out_channels, kernel_size=1) \
                     if in_channels != out_channels else nn.Identity()
        self.pool  = nn.MaxPool1d(3)

    def forward(self, x):
        residual = self.skip(x)
        out = F.leaky_relu(self.bn1(x))
        out = self.conv1(out)
        out = F.leaky_relu(self.bn2(out))
        out = self.conv2(out)
        out = out + residual
        return self.pool(out)


class RawNet2(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        self.sinc_conv = SincConv(out_channels=128, kernel_size=1024, sample_rate=SAMPLE_RATE)
        self.bn0       = nn.BatchNorm1d(128)
        self.pool0     = nn.MaxPool1d(3)

        self.res_blocks = nn.Sequential(
            ResBlock(128, 128),
            ResBlock(128, 128),
            ResBlock(128, 256),
            ResBlock(256, 256),
            ResBlock(256, 512),
            ResBlock(512, 512),
        )
        self.bn_before_gru = nn.BatchNorm1d(512)
        self.gru = nn.GRU(input_size=512, hidden_size=1024,
                          num_layers=3, batch_first=True, dropout=0.3)
        self.fc1 = nn.Linear(1024, 1024)
        self.fc2 = nn.Linear(1024, num_classes)

    def forward(self, x):
        out = self.sinc_conv(x)
        out = torch.abs(out)
        out = F.max_pool1d(out, kernel_size=3)
        out = F.leaky_relu(self.bn0(out))
        out = self.res_blocks(out)
        out = F.leaky_relu(self.bn_before_gru(out))
        out = out.permute(0, 2, 1)
        out, _ = self.gru(out)
        out = out[:, -1, :]
        out = F.leaky_relu(self.fc1(out))
        out = F.dropout(out, p=0.3, training=self.training)
        out = self.fc2(out)
        return out