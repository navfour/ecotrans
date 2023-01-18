import torch as t
import torch.nn as nn
import torch.nn.functional as F
import math
from torch import Tensor
from fastai.basics import ifnone, init_linear
from torch.nn import Flatten
from fastai.basics import SigmoidRange, pv, default_device
from typing import Optional
from typing import Callable

from tsai.imports import *
from tsai.utils import *
from tsai.models.layers import *
from tsai.models.utils import *
from tsai.data.core import *


def PositionalEncoding(q_len, d_model, normalize=True):
    pe = t.zeros(q_len, d_model)
    position = t.arange(0, q_len).unsqueeze(1)
    div_term = t.exp(t.arange(0, d_model, 2) * -(math.log(10000.0) / d_model))
    pe[:, 0::2] = t.sin(position * div_term)
    pe[:, 1::2] = t.cos(position * div_term)
    if normalize:
        pe = pe - pe.mean()
        pe = pe / (pe.std() * 10)
    return pe


SinCosPosEncoding = PositionalEncoding


# Cell
def Coord2dPosEncoding(q_len, d_model, exponential=False, normalize=True, eps=1e-3, verbose=False):
    x = .5 if exponential else 1
    i = 0
    for i in range(100):
        cpe = 2 * (t.linspace(0, 1, q_len).reshape(-1, 1) ** x) * (t.linspace(0, 1, d_model).reshape(1, -1) ** x) - 1
        pv(f'{i:4.0f}  {x:5.3f}  {cpe.mean():+6.3f}', verbose)
        if abs(cpe.mean()) <= eps:
            break
        elif cpe.mean() > eps:
            x += .001
        else:
            x -= .001
        i += 1
    if normalize:
        cpe = cpe - cpe.mean()
        cpe = cpe / (cpe.std() * 10)
    return cpe


# Cell
def Coord1dPosEncoding(q_len, exponential=False, normalize=True):
    cpe = (2 * (t.linspace(0, 1, q_len).reshape(-1, 1) ** (.5 if exponential else 1)) - 1)
    if normalize:
        cpe = cpe - cpe.mean()
        cpe = cpe / (cpe.std() * 10)
    return cpe


class _TSTEncoderLayer(Module):
    def __init__(self, q_len, d_model, n_heads, d_k=None, d_v=None, d_ff=256, store_attn=False,
                 norm='BatchNorm', attn_dropout=0, dropout=0., bias=True, activation="gelu", res_attention=False,
                 pre_norm=False):

        assert not d_model % n_heads, f"d_model ({d_model}) must be divisible by n_heads ({n_heads})"
        d_k = ifnone(d_k, d_model // n_heads)
        d_v = ifnone(d_v, d_model // n_heads)

        # Multi-Head attention
        self.res_attention = res_attention
        self.self_attn = MultiheadAttention(d_model, n_heads, d_k, d_v, attn_dropout=attn_dropout, proj_dropout=dropout,
                                            res_attention=res_attention)

        # Add & Norm
        self.dropout_attn = nn.Dropout(dropout)
        if "batch" in norm.lower():
            self.norm_attn = nn.Sequential(Transpose(1, 2), nn.BatchNorm1d(d_model), Transpose(1, 2))
        else:
            self.norm_attn = nn.LayerNorm(d_model)

        # Position-wise Feed-Forward
        self.ff = nn.Sequential(nn.Linear(d_model, d_ff, bias=bias),
                                get_act_fn(activation),
                                nn.Dropout(dropout),
                                nn.Linear(d_ff, d_model, bias=bias))

        # Add & Norm
        self.dropout_ffn = nn.Dropout(dropout)
        if "batch" in norm.lower():
            self.norm_ffn = nn.Sequential(Transpose(1, 2), nn.BatchNorm1d(d_model), Transpose(1, 2))
        else:
            self.norm_ffn = nn.LayerNorm(d_model)

        self.pre_norm = pre_norm
        self.store_attn = store_attn

    def forward(self, src: Tensor, prev: Optional[Tensor] = None, key_padding_mask: Optional[Tensor] = None,
                attn_mask: Optional[Tensor] = None) -> Tensor:

        # Multi-Head attention sublayer
        if self.pre_norm:
            src = self.norm_attn(src)
        ## Multi-Head attention
        if self.res_attention:
            src2, attn, scores = self.self_attn(src, src, src, prev, key_padding_mask=key_padding_mask,
                                                attn_mask=attn_mask)
        else:
            src2, attn = self.self_attn(src, src, src, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
        if self.store_attn:
            self.attn = attn
        ## Add & Norm
        src = src + self.dropout_attn(src2)  # Add: residual connection with residual dropout
        if not self.pre_norm:
            src = self.norm_attn(src)

        # Feed-forward sublayer
        if self.pre_norm:
            src = self.norm_ffn(src)
        ## Position-wise Feed-Forward
        src2 = self.ff(src)
        ## Add & Norm
        src = src + self.dropout_ffn(src2)  # Add: residual connection with residual dropout
        if not self.pre_norm:
            src = self.norm_ffn(src)

        if self.res_attention:
            return src, scores
        else:
            return src


class _TSTEncoder(Module):
    def __init__(self, q_len, d_model, n_heads, d_k=None, d_v=None, d_ff=None, norm='BatchNorm', attn_dropout=0.,
                 dropout=0., activation='gelu', res_attention=False, n_layers=1, pre_norm=False, store_attn=False):
        super().__init__()
        self.layers = nn.ModuleList(
            [_TSTEncoderLayer(q_len, d_model, n_heads=n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff, norm=norm,
                              attn_dropout=attn_dropout, dropout=dropout,
                              activation=activation, res_attention=res_attention,
                              pre_norm=pre_norm, store_attn=store_attn) for i in range(n_layers)])
        self.res_attention = res_attention

    def forward(self, src: Tensor, key_padding_mask: Optional[Tensor] = None, attn_mask: Optional[Tensor] = None):
        output = src
        scores = None
        if self.res_attention:
            for mod in self.layers: output, scores = mod(output, prev=scores, key_padding_mask=key_padding_mask,
                                                         attn_mask=attn_mask)
            return output
        else:
            for mod in self.layers: output = mod(output, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
            return output


class _TSTBackbone(Module):
    def __init__(self, c_in, seq_len, max_seq_len=512,
                 n_layers=3, d_model=128, n_heads=16, d_k=None, d_v=None,
                 d_ff=256, norm='BatchNorm', attn_dropout=0., dropout=0., act="gelu", store_attn=False,
                 key_padding_mask='auto', padding_var=None, attn_mask=None, res_attention=True, pre_norm=False,
                 pe='zeros', learn_pe=True, verbose=False, **kwargs):

        # Input encoding
        q_len = seq_len
        self.new_q_len = False
        if max_seq_len is not None and seq_len > max_seq_len:  # Control temporal resolution
            self.new_q_len = True
            q_len = max_seq_len
            tr_factor = math.ceil(seq_len / q_len)
            total_padding = (tr_factor * q_len - seq_len)
            padding = (total_padding // 2, total_padding - total_padding // 2)
            self.W_P = nn.Sequential(Pad1d(padding),
                                     Conv1d(c_in, d_model, kernel_size=tr_factor, padding=0, stride=tr_factor))
            pv(
                f'temporal resolution modified: {seq_len} --> {q_len} time steps: kernel_size={tr_factor}, stride={tr_factor}, padding={padding}.\n',
                verbose)
        elif kwargs:
            self.new_q_len = True
            t = torch.rand(1, 1, seq_len)
            q_len = Conv1d(1, 1, **kwargs)(t).shape[-1]
            self.W_P = Conv1d(c_in, d_model, **kwargs)  # Eq 2
            pv(f'Conv1d with kwargs={kwargs} applied to input to create input encodings\n', verbose)
        else:
            self.W_P = nn.Linear(c_in, d_model)  # Eq 1: projection of feature vectors onto a d-dim vector space
        self.seq_len = q_len

        # Positional encoding
        self.W_pos_all = self._positional_encoding(pe, learn_pe, 120, d_model)
        self.W_pos_train = self._positional_encoding(pe, learn_pe, q_len, d_model)
        self.W_pos_val = self._positional_encoding(pe, learn_pe, 120 - q_len, d_model)

        # Residual dropout
        self.dropout = nn.Dropout(dropout)

        # Encoder
        self.encoder_all = _TSTEncoder(120, d_model, n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff, norm=norm,
                                       attn_dropout=attn_dropout, dropout=dropout,
                                       pre_norm=pre_norm, activation=act, res_attention=res_attention,
                                       n_layers=n_layers,
                                       store_attn=store_attn)
        self.encoder_train = _TSTEncoder(q_len, d_model, n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff, norm=norm,
                                         attn_dropout=attn_dropout, dropout=dropout,
                                         pre_norm=pre_norm, activation=act, res_attention=res_attention,
                                         n_layers=n_layers,
                                         store_attn=store_attn)
        self.encoder_val = _TSTEncoder(120 - q_len, d_model, n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff, norm=norm,
                                       attn_dropout=attn_dropout, dropout=dropout,
                                       pre_norm=pre_norm, activation=act, res_attention=res_attention,
                                       n_layers=n_layers,
                                       store_attn=store_attn)
        self.transpose = Transpose(-1, -2, contiguous=True)
        self.key_padding_mask, self.padding_var, self.attn_mask = key_padding_mask, padding_var, attn_mask

    def forward(self, inp) -> Tensor:
        r"""Pass the input through the TST backbone.
        Args:
            inp: input (optionally with padding mask. 1s (meaning padded) in padding mask will be ignored while 0s (non-padded) will be unchanged.)
        Shape:
            There are 3 options:
            1. inp: Tensor containing just time series data [bs x nvars x q_len]
            2. inp: Tensor containing time series data plus a padding feature in the last channel [bs x (nvars + 1) x q_len]
            3. inp: tuple containing a tensor with time series data plus a padding mask per batch ([bs x nvars x q_len] , [bs x q_len] )
        """

        # x and padding mask
        if isinstance(inp, tuple):
            x, key_padding_mask = inp
        elif self.key_padding_mask == 'auto':
            x, key_padding_mask = self._key_padding_mask(inp)  # automatically identify padding mask
        elif self.key_padding_mask == -1:
            x, key_padding_mask = inp[:, :-1], inp[:, -1]  # padding mask is the last channel
        else:
            x, key_padding_mask = inp, None

        # Input encoding
        u = self.W_P(x.transpose(2, 1))  # Eq 1        # u: [bs x q_len x nvars] converted to [bs x q_len x d_model]

        # Positional encoding
        if x.shape[0] == self.seq_len:
            u = self.dropout(u + self.W_pos_train.unsqueeze(1))
        elif x.shape[0] == 120 - self.seq_len:
            u = self.dropout(u + self.W_pos_val.unsqueeze(1))
        else:
            u = self.dropout(u + self.W_pos_all.unsqueeze(1))

        # Encoder
        if u.shape[0] == self.seq_len:
            z = self.encoder_train(u, key_padding_mask=key_padding_mask,
                                   attn_mask=self.attn_mask)  # z: [bs x q_len x d_model]
        elif u.shape[0] == 120 - self.seq_len:
            z = self.encoder_val(u, key_padding_mask=key_padding_mask,
                                 attn_mask=self.attn_mask)  # z: [bs x q_len x d_model]
        else:
            z = self.encoder_all(u, key_padding_mask=key_padding_mask,
                                 attn_mask=self.attn_mask)  # z: [bs x q_len x d_model]
        # z = self.transpose(z)  # z: [bs x d_model x q_len]
        if key_padding_mask is not None:
            z = z * torch.logical_not(key_padding_mask.unsqueeze(1))  # zero-out padding embeddings
        return z

    def _positional_encoding(self, pe, learn_pe, q_len, d_model):
        # Positional encoding
        if pe == None:
            W_pos = torch.empty((q_len, d_model))  # pe = None and learn_pe = False can be used to measure impact of pe
            nn.init.uniform_(W_pos, -0.02, 0.02)
            learn_pe = False
        elif pe == 'zero':
            W_pos = torch.empty((q_len, 1))
            nn.init.uniform_(W_pos, -0.02, 0.02)
        elif pe == 'zeros':
            W_pos = torch.empty((q_len, d_model))
            nn.init.uniform_(W_pos, -0.02, 0.02)
        elif pe == 'normal' or pe == 'gauss':
            W_pos = torch.zeros((q_len, 1))
            torch.nn.init.normal_(W_pos, mean=0.0, std=0.1)
        elif pe == 'uniform':
            W_pos = torch.zeros((q_len, 1))
            nn.init.uniform_(W_pos, a=0.0, b=0.1)
        elif pe == 'lin1d':
            W_pos = Coord1dPosEncoding(q_len, exponential=False, normalize=True)
        elif pe == 'exp1d':
            W_pos = Coord1dPosEncoding(q_len, exponential=True, normalize=True)
        elif pe == 'lin2d':
            W_pos = Coord2dPosEncoding(q_len, d_model, exponential=False, normalize=True)
        elif pe == 'exp2d':
            W_pos = Coord2dPosEncoding(q_len, d_model, exponential=True, normalize=True)
        elif pe == 'sincos':
            W_pos = PositionalEncoding(q_len, d_model, normalize=True)
        else:
            raise ValueError(f"{pe} is not a valid pe (positional encoder. Available types: 'gauss'=='normal', \
            'zeros', 'zero', uniform', 'lin1d', 'exp1d', 'lin2d', 'exp2d', 'sincos', None.)")
        return nn.Parameter(W_pos, requires_grad=learn_pe)

    def _key_padding_mask(self, x):
        if self.padding_var is not None:
            mask = TSMaskTensor(x[:, self.padding_var] == 1)  # key_padding_mask: [bs x q_len]
            return x, mask
        else:
            mask = torch.isnan(x)
            x[mask] = 0
            if mask.any():
                mask = TSMaskTensor((mask.float().mean(1) == 1).bool())  # key_padding_mask: [bs x q_len]
                return x, mask
            else:
                return x, None


# %%
# export
class Transformer(nn.Sequential):
    """TST (Time Series Transformer) is a Transformer that takes continuous time series as inputs"""

    def __init__(self, c_in: int, c_out: int, seq_len: int, train_mask_scale: float, max_seq_len: Optional[int] = 512,
                 n_layers: int = 3, d_model: int = 128, n_heads: int = 16, d_k: Optional[int] = None,
                 d_v: Optional[int] = None,
                 d_ff: int = 256, norm: str = 'BatchNorm', attn_dropout: float = 0., dropout: float = 0.,
                 act: str = "gelu", key_padding_mask: bool = 'auto',
                 padding_var: Optional[int] = None, attn_mask: Optional[Tensor] = None, res_attention: bool = True,
                 pre_norm: bool = False, store_attn: bool = False,
                 pe: str = 'zeros', learn_pe: bool = True, flatten: bool = True, fc_dropout: float = 0.,
                 concat_pool: bool = False, bn: bool = False, custom_head: Optional[Callable] = None,
                 y_range: Optional[tuple] = None, verbose: bool = False, **kwargs):
        """
        Args:
            c_in: the number of features (aka variables, dimensions, channels) in the time series dataset.
            c_out: the number of target classes.
            seq_len: number of time steps in the time series.
            max_seq_len: useful to control the temporal resolution in long time series to avoid memory issues. Default=512.
            d_model: total dimension of the model (number of features created by the model). Default: 128 (range(64-512))
            n_heads:  parallel attention heads. Default:16 (range(8-16)).
            d_k: size of the learned linear projection of queries and keys in the MHA. Usual values: 16-512. Default: None -> (d_model/n_heads) = 32.
            d_v: size of the learned linear projection of values in the MHA. Usual values: 16-512. Default: None -> (d_model/n_heads) = 32.
            d_ff: the dimension of the feedforward network model. Default: 512 (range(256-512))
            norm: flag to indicate whether BatchNorm (default) or LayerNorm is used in the encoder layers.
            attn_dropout: dropout applied to the attention scores
            dropout: amount of dropout applied to all linear layers except q,k&v projections in the encoder.
            act: the activation function of intermediate layer, relu or gelu.
            key_padding_mask:   a boolean padding mask will be applied to attention if 'auto' a mask to those steps in a sample where all features are nan.
                                Other options include: True -->tuple (x, key_padding_mask), -1 --> key_padding_mask is the last channel, False: no mask.
            padding_var: (optional) an int indicating the variable that contains the padded steps (0: non-padded, 1: padded).
            attn_mask: a boolean mask will be applied to attention if a tensor of shape [min(seq_len, max_seq_len) x min(seq_len, max_seq_len)] if provided.
            res_attention: if True Residual MultiheadAttention is applied.
            pre_norm: if True normalization will be applied as the first step in the sublayers. Defaults to False
            store_attn: can be used to visualize attention weights. Default: False.
            n_layers: number of layers (or blocks) in the encoder. Default: 3 (range(1-4))
            pe: type of positional encoder.
                Available types (for experimenting): None, 'exp1d', 'lin1d', 'exp2d', 'lin2d', 'sincos', 'gauss' or 'normal',
                'uniform', 'zero', 'zeros' (default, as in the paper).
            learn_pe: learned positional encoder (True, default) or fixed positional encoder.
            flatten: this will flatten the encoder output to be able to apply an mlp type of head (default=False)
            fc_dropout: dropout applied to the final fully connected layer.
            concat_pool: indicates if global adaptive concat pooling will be used instead of global adaptive pooling.
            bn: indicates if batchnorm will be applied to the head.
            custom_head: custom head that will be applied to the network. It must contain all kwargs (pass a partial function)
            y_range: range of possible y values (used in regression tasks).
            kwargs: nn.Conv1d kwargs. If not {}, a nn.Conv1d with those kwargs will be applied to original time series.
        Input shape:
            x: bs (batch size) x nvars (aka features, variables, dimensions, channels) x seq_len (aka time steps)
            attn_mask: q_len x q_len
            As mentioned in the paper, the input must be standardized by_var based on the entire training set.
        """
        # Backbone
        backbone = _TSTBackbone(c_in, seq_len=seq_len, max_seq_len=max_seq_len,
                                n_layers=n_layers, d_model=d_model, n_heads=n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff,
                                attn_dropout=attn_dropout, dropout=dropout, act=act, key_padding_mask=key_padding_mask,
                                padding_var=padding_var,
                                attn_mask=attn_mask, res_attention=res_attention, pre_norm=pre_norm,
                                store_attn=store_attn,
                                pe=pe, learn_pe=learn_pe, verbose=verbose, **kwargs)

        # Head
        self.head_nf = d_model
        self.c_out = c_out
        self.seq_len = backbone.seq_len
        if custom_head:
            head = custom_head(self.head_nf, c_out,
                               self.seq_len)  # custom head passed as a partial func with all its kwargs
        else:
            head = self.create_head(self.head_nf, c_out, self.seq_len, act=act, flatten=flatten,
                                    concat_pool=concat_pool,
                                    fc_dropout=fc_dropout, bn=bn, y_range=y_range)
        super().__init__(OrderedDict([('backbone', backbone), ('head', head)]))

    def create_head(self, nf, c_out, seq_len, flatten=True, concat_pool=False, act="gelu", fc_dropout=0., bn=False,
                    y_range=None):
        layers = [get_act_fn(act)]
        if flatten:
            layers += [nn.Linear(128, c_out)]
            # nf *= seq_len
            # layers += [Flatten()]
        else:
            if concat_pool: nf *= 2
            layers = [GACP1d(1) if concat_pool else GAP1d(1)]
            layers += [LinBnDrop(nf, c_out, bn=bn, p=fc_dropout)]
        if y_range: layers += [SigmoidRange(*y_range)]
        return nn.Sequential(*layers)

    def show_pe(self, cmap='viridis', figsize=None):
        plt.figure(figsize=figsize)
        plt.pcolormesh(self.backbone.W_pos.detach().cpu().T, cmap=cmap)
        plt.title('Positional Encoding')
        plt.colorbar()
        plt.show()
        plt.figure(figsize=figsize)
        plt.title('Positional Encoding - value along time axis')
        plt.plot(F.relu(self.backbone.W_pos.data).mean(1).cpu())
        plt.plot(-F.relu(-self.backbone.W_pos.data).mean(1).cpu())
        plt.show()


class _Splitter(Module):
    def __init__(self, feat_list, branches):
        super().__init__()
        self.feat_list, self.branches = feat_list, branches

    def forward(self, x):
        if is_listy(self.feat_list[0]):
            x = [x[:, feat] for feat in self.feat_list]
        else:
            x = torch.split(x, self.feat_list, dim=1)
        _out = []
        for xi, branch in zip(x, self.branches): _out.append(branch(xi))
        output = torch.cat(_out, dim=1)
        return output


# export
@delegates(Transformer.__init__)
class MultiTransformer(nn.Sequential):
    _arch = Transformer

    def __init__(self, feat_list, c_out, seq_len, max_seq_len: Optional[int] = 512, custom_head=None, **kwargs):
        r"""
        MultiTST is a class that allows you to create a model with multiple branches of TST.

        Args:
            * feat_list: list with number of features that will be passed to each body, or list of list with feature indices.
        """
        self.feat_list = [feat_list] if isinstance(feat_list, int) else feat_list
        self.device = ifnone(device, default_device())

        # Backbone
        branches = nn.ModuleList()
        self.head_nf = 0
        for feat in self.feat_list:
            if is_listy(feat): feat = len(feat)
            m = build_ts_model(self._arch, c_in=feat, c_out=c_out, seq_len=seq_len, max_seq_len=max_seq_len, **kwargs)
            with torch.no_grad():
                self.head_nf += m[0](torch.randn(1, feat, ifnone(seq_len, 10)).to(self.device)).shape[1]
            branches.append(m.backbone)
        backbone = _Splitter(self.feat_list, branches)

        # Head
        self.c_out = c_out
        q_len = min(seq_len, max_seq_len)
        self.seq_len = q_len
        if custom_head is None:
            head = self._arch.create_head(self, self.head_nf, c_out, q_len)
        else:
            head = custom_head(self.head_nf, c_out, q_len)

        layers = OrderedDict([('backbone', nn.Sequential(backbone)), ('head', nn.Sequential(head))])
        super().__init__(layers)
        self.to(self.device)
