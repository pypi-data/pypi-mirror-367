import torch
from torch import nn


from ._linear import Linear


class LinearSelfInteraction(nn.Module):
    """
    Equivariant linear self interaction layer

    Parameters
    ----------
    f: nn.Module
        Equivariant layer to wrap.
        f.irreps_in and f.irreps_out must be defined
    """

    def __init__(self, f):
        super().__init__()

        self.f = f
        self.irreps_in = f.irreps_in
        self.irreps_out = f.irreps_out

        self.skip_connection = Linear(self.irreps_in, self.irreps_out)
        self.self_interaction = Linear(self.irreps_out, self.irreps_out)

    def forward(self, x: torch.Tensor, *args) -> torch.Tensor:
        """Combines the input layer with a skip connection."""
        s = self.skip_connection(x)
        x = self.f(x, *args)
        x = self.self_interaction(x)
        return x + s
