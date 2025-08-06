import math
from typing import Optional

import numpy as np
import torch
from torch import Tensor, nn


class GeneEncoder(nn.Module):
    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: int,
        padding_idx: Optional[int] = None,
        weights: Optional[Tensor] = None,
        freeze: bool = False,
    ):
        """
        Encodes gene sequences into a continuous vector space using an embedding layer.

        The output is then normalized using a LayerNorm.

        Args:
            num_embeddings (int): The number of possible values.
            embedding_dim (int): The dimension of the output vectors.
            padding_idx (int, optional): The index of the padding token. Defaults to None.
            weights (Tensor, optional): The initial weights for the embedding layer. Defaults to None.
            dropout (float, optional): The dropout rate to apply to the output of the positional encoding. Defaults to 0.1.
            freeze (bool, optional): Whether to freeze the weights of the embedding layer. Defaults to False.

        Note: not used in the current version of scprint.
        """
        super(GeneEncoder, self).__init__()
        self.embeddings = nn.Embedding(
            num_embeddings, embedding_dim, padding_idx=padding_idx, _freeze=freeze
        )

        if weights is not None:
            # concat a zero vector to the weight
            # this is to make the embedding of the padding token to be zero
            # weights = torch.cat(
            #    [torch.Tensor(weights), torch.zeros(1, embedding_dim)], dim=0
            # )
            self.embeddings.weight.data.copy_(torch.Tensor(weights))

    def forward(self, x: Tensor) -> Tensor:
        return self.embeddings(x)  # (batch, seq_len, embsize)


class PositionalEncoding(nn.Module):
    def __init__(
        self,
        d_model: int,
        max_len: int,
        token_to_pos: dict[str, int],  # [token, pos]
        maxval=10000.0,
    ):
        """
        The PositionalEncoding module applies a positional encoding to a sequence of vectors.
        This is necessary for the Transformer model, which does not have any inherent notion of
        position in a sequence. The positional encoding is added to the input embeddings and
        allows the model to attend to positions in the sequence.

        Args:
            d_model (int): The dimension of the input vectors.
            dropout (float, optional): The dropout rate to apply to the output of the positional encoding.
            max_len (int, optional): The maximum length of a sequence that this module can handle.

        Note: not used in the current version of scprint.
        """
        super(PositionalEncoding, self).__init__()
        position = torch.arange(max_len).unsqueeze(1)

        # Create a dictionary to convert token to position

        div_term = torch.exp(
            torch.arange(0, d_model, 2) * (-math.log(maxval) / d_model)
        )
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        # we reorder them and map them to gene_id (position)
        arr = []
        for _, v in token_to_pos.items():
            arr.append(pe[v - 1].numpy())
        pe = torch.Tensor(np.array(arr))
        # Remove the unnecessary middle dimension since pe should be [m, d]
        # pe = pe.squeeze(1)
        self.register_buffer("pe", pe)

    def forward(self, gene_pos: Tensor) -> Tensor:
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        return torch.index_select(self.pe, 0, gene_pos.reshape(-1)).reshape(
            gene_pos.shape + (-1,)
        )


class DPositionalEncoding(nn.Module):
    """
    The PositionalEncoding module applies a positional encoding to a sequence of vectors.
    This is necessary for the Transformer model, which does not have any inherent notion of
    position in a sequence. The positional encoding is added to the input embeddings and
    allows the model to attend to positions in the sequence.

    Args:
        d_model (int): The dimension of the input vectors.
        dropout (float, optional): The dropout rate to apply to the output of the positional encoding.
        max_len (int, optional): The maximum length of a sequence that this module can handle.

    Note: not used in the current version of scprint.
    """

    def __init__(
        self,
        d_model: int,
        max_len_x: int,
        max_len_y: int,
        maxvalue_x=10000.0,
        maxvalue_y=10000.0,
    ):
        super(DPositionalEncoding, self).__init__()
        position2 = torch.arange(max_len_y).unsqueeze(1)
        position1 = torch.arange(max_len_x).unsqueeze(1)

        half_n = d_model // 2

        div_term2 = torch.exp(
            torch.arange(0, half_n, 2) * (-math.log(maxvalue_y) / d_model)
        )
        div_term1 = torch.exp(
            torch.arange(0, half_n, 2) * (-math.log(maxvalue_x) / d_model)
        )
        pe1 = torch.zeros(max_len_x, 1, d_model)
        pe2 = torch.zeros(max_len_y, 1, d_model)
        pe1[:, 0, 0:half_n:2] = torch.sin(position1 * div_term1)
        pe1[:, 0, 1:half_n:2] = torch.cos(position1 * div_term1)
        pe2[:, 0, half_n::2] = torch.sin(position2 * div_term2)
        pe2[:, 0, 1 + half_n :: 2] = torch.cos(position2 * div_term2)
        # https://github.com/tatp22/multidim-positional-encoding/blob/master/positional_encodings/torch_encodings.py
        self.register_buffer("pe1", pe1)
        self.register_buffer("pe2", pe2)

        # PE(x,y,2i) = sin(x/10000^(4i/D))
        # PE(x,y,2i+1) = cos(x/10000^(4i/D))
        # PE(x,y,2j+D/2) = sin(y/10000^(4j/D))
        # PE(x,y,2j+1+D/2) = cos(y/10000^(4j/D))

    def forward(self, x: Tensor, pos_x: Tensor, pos_y: Tensor) -> Tensor:
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe1[pos_x]
        x = x + self.pe2[pos_y]
        return x


class ContinuousValueEncoder(nn.Module):
    def __init__(
        self,
        d_model: int,
        dropout: float = 0.1,
        max_value: int = 100_000,
        layers: int = 1,
        size: int = 1,
    ):
        """
        Encode real number values to a vector using neural nets projection.

        Args:
            d_model (int): The dimension of the input vectors.
            dropout (float, optional): The dropout rate to apply to the output of the positional encoding.
            max_value (int, optional): The maximum value of the input. Defaults to 100_000.
            layers (int, optional): The number of layers in the encoder. Defaults to 1.
            size (int, optional): The size of the input. Defaults to 1.

        Returns:
            torch.Tensor: A tensor representing the encoded continuous values.
        """
        super(ContinuousValueEncoder, self).__init__()
        self.max_value = max_value
        self.encoder = nn.ModuleList()
        # self.mask_value = nn.Embedding(1, d_model)
        self.encoder.append(nn.Linear(size, d_model))
        for _ in range(layers - 1):
            self.encoder.append(nn.LayerNorm(d_model))
            self.encoder.append(nn.ReLU())
            self.encoder.append(nn.Dropout(p=dropout))
            self.encoder.append(nn.Linear(d_model, d_model))

    def forward(self, x: Tensor, mask: Tensor = None) -> Tensor:
        """
        Args:
            x: Tensor, shape [batch_size, seq_len]
        """
        # expand last dimension
        x = x.unsqueeze(-1)
        # use the mask embedding when x=-1
        # mask = (x == -1).float()
        x = torch.clamp(x, min=0, max=self.max_value)
        for val in self.encoder:
            x = val(x)
        if mask is not None:
            x = x.masked_fill_(mask.unsqueeze(-1), 0)
            # x = x.masked_fill_(mask.unsqueeze(-1), self.mask_value(0))
        return x


class CategoryValueEncoder(nn.Module):
    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: int,
        padding_idx: Optional[int] = None,
    ):
        """
        Encodes categorical values into a vector using an embedding layer and layer normalization.

        Args:
            num_embeddings (int): The number of possible values.
            embedding_dim (int): The dimension of the output vectors.
            padding_idx (int, optional): The index of the padding token. Defaults to None.

        Returns:
            torch.Tensor: A tensor representing the encoded categorical values.

        Note: not used in the current version of scprint.
        """
        super(CategoryValueEncoder, self).__init__()
        self.embedding = nn.Embedding(
            num_embeddings, embedding_dim, padding_idx=padding_idx
        )

    def forward(self, x: Tensor) -> Tensor:
        return self.embedding(x.long())  # (batch, seq_len, embsize)
