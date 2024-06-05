import math
import torch
import torch.nn as nn
from torch import Tensor

class TransformerEncoderModel(nn.Module):
    def __init__(
        self,
        d_model,
        ntoken,
        num_heads,
        forward_expansion,
        num_layers,
        dropout,
        num_classes,
        pad_idx,
        device,
    ):
        super(TransformerEncoderModel, self).__init__()
        self.d_model = d_model
        self.pad_idx = pad_idx
        self.device = device

        self.src_encoder = nn.Embedding(ntoken, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)

        self.transformerEncoderLayer = nn.TransformerEncoderLayer(
            d_model,
            num_heads,
            forward_expansion,
            dropout,
        )
        self.transformerEncoder = nn.TransformerEncoder(
            self.transformerEncoderLayer,
            num_layers,
        )
        self.hidden = nn.Linear(d_model, forward_expansion)
        self.fc_out = nn.Linear(forward_expansion, num_classes)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src):
        embed_src = self.src_encoder(src) * math.sqrt(self.d_model)
        embed_src = self.pos_encoder(embed_src)

        src_pad_mask = src.transpose(0, 1) == self.pad_idx

        out = self.transformerEncoder(
            embed_src,
            src_key_padding_mask=src_pad_mask,
        )

        out = self.hidden(out[out.shape[0]-1])
        out = self.fc_out(out)

        return out

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 100000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)
