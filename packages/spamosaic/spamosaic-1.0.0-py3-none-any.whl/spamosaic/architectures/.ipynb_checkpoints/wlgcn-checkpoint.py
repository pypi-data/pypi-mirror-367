from typing import List, Optional, Union, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn.conv import MessagePassing
from torch_scatter import scatter_add
from torch_geometric.utils import add_remaining_self_loops
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv

def sym_norm(edge_index:torch.Tensor,
             num_nodes:int,
             edge_weight:Optional[Union[Any,torch.Tensor]]=None,
             improved:Optional[bool]=False,
             dtype:Optional[Any]=None
    )-> List:
    if edge_weight is None:
        edge_weight = torch.ones((edge_index.size(1), ), dtype=dtype, device=edge_index.device)

    fill_value = 1 if not improved else 2
    edge_index, edge_weight = add_remaining_self_loops(edge_index, edge_weight, fill_value, num_nodes)

    row, col = edge_index
    deg = scatter_add(edge_weight, row, dim=0, dim_size=num_nodes)
    deg_inv_sqrt = deg.pow(-0.5)
    deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0

    return edge_index, deg_inv_sqrt[row] * edge_weight * deg_inv_sqrt[col]

class WLGCN_vanilla(MessagePassing):
    def __init__(self, K:Optional[int]=1,
                 cached:Optional[bool]=False,
                 bias:Optional[bool]=True,
                 **kwargs):
        super(WLGCN_vanilla, self).__init__(aggr='add', **kwargs)
        self.K = K
        
    def forward(self, x:torch.Tensor,
                edge_index:torch.Tensor,
                edge_weight:Union[torch.Tensor,None]=None):
        edge_index, norm = sym_norm(edge_index, x.size(0), edge_weight,
                                        dtype=x.dtype)

        xs = [x]
        for k in range(self.K):
            xs.append(self.propagate(edge_index, x=xs[-1], norm=norm))
        return torch.cat(xs, dim = 1)

    def message(self, x_j, norm):
        return norm.view(-1, 1) * x_j

    def __repr__(self):
        return '{}({}, {}, K={})'.format(self.__class__.__name__,
                                        #  self.in_channels, self.out_channels,
                                         self.K)

class WLGCN(torch.nn.Module):
    def __init__(self, input_size, output_size, K=8, dec_l=1, hidden_size=512, dropout=0.2, slope=0.2):
        super(WLGCN, self).__init__()
        self.conv1 = WLGCN_vanilla(K=K)
        self.fc1 = torch.nn.Linear(input_size * (K + 1), hidden_size)
        self.bn = torch.nn.BatchNorm1d(hidden_size)
        self.dropout1 = torch.nn.Dropout(p=dropout)
        self.fc2 = torch.nn.Linear(hidden_size, output_size)
        self.negative_slope = slope

        if dec_l == 1:
            self.decoder = torch.nn.Linear(output_size, input_size)
        else:
            self.decoder = torch.nn.Sequential(
                torch.nn.Linear(output_size, output_size),
                torch.nn.ReLU(),
                torch.nn.Linear(output_size, input_size)
            )
        
    def forward(self, feature, edge_index, edge_weight=None):
        x = self.conv1(feature, edge_index, edge_weight)
        x = F.leaky_relu(self.fc1(x), negative_slope=self.negative_slope)
        x = self.bn(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        
        r = self.decoder(x)
        x = F.normalize(x, p=2, dim=1)
        return x, r


class WLGCN2(torch.nn.Module):
    def __init__(self, input_size, output_size, K=8, dec_l=1, hidden_size=512, dropout=0.2, slope=0.2):
        super(WLGCN2, self).__init__()
        self.conv1 = WLGCN_vanilla(K=K)
        self.fc1 = torch.nn.Linear(input_size * (K + 1), hidden_size)
        self.bn = torch.nn.BatchNorm1d(hidden_size)
        self.dropout1 = torch.nn.Dropout(p=dropout)
        self.fc2 = torch.nn.Linear(hidden_size, output_size)
        self.negative_slope = slope

        # if dec_l == 1:
        #     self.decoder = torch.nn.Linear(output_size, input_size)
        # else:
        #     self.decoder = torch.nn.Sequential(
        #         torch.nn.Linear(output_size, output_size),
        #         torch.nn.ReLU(),
        #         torch.nn.Linear(output_size, input_size)
        #     )
        
    def forward(self, feature, edge_index, edge_weight=None):
        x = self.conv1(feature, edge_index, edge_weight)
        x = F.leaky_relu(self.fc1(x), negative_slope=self.negative_slope)
        x = self.bn(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        
        # r = self.decoder(x)
        x = F.normalize(x, p=2, dim=1)
        return x