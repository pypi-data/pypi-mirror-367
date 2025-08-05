import torch
from torch import nn
import torch.nn.functional as F

from torch_geometric.nn import GCNConv, SAGEConv, GATConv, GINConv
from torch.nn import Sequential, Linear

from torch_geometric.nn import global_mean_pool


class GNNBase(nn.Module):
    """
    GNN base model.

    Parameters
    ----------
    in_dim : int
        Input dimension of model.
    hid_dim : int
        Hidden dimension of model.
    num_classes : int
        Number of classes.
    num_layers : int, optional
        Total number of layers in model. Default: ``4``.
    dropout : float, optional
        Dropout rate. Default: ``0.``.
    act : callable activation function or None, optional
        Activation function if not None.
        Default: ``torch.nn.functional.relu``.
    gnn : string, optional
        The backbone of GNN model.
        Default: ``gcn``.
    mode : str, optional
        Mode for node or graph level tasks. Default: ``node``.
    **kwargs : optional
        Other parameters for the backbone.
    """

    def __init__(self,
                 in_dim,
                 hid_dim,
                 num_classes,
                 num_layers=1,
                 dropout=0.1,
                 act=F.relu,
                 gnn='gcn',
                 mode='node',
                 **kwargs):
        super(GNNBase, self).__init__()

        assert gnn in ('gcn', 'sage', 'gat', 'gin'), 'Invalid gnn backbone'
        
        self.in_dim = in_dim
        self.hid_dim = hid_dim
        self.num_classes = num_classes
        self.num_layers = num_layers
        self.dropout = dropout
        self.gnn = gnn
        self.act = act
        self.mode = mode

        self.convs = nn.ModuleList()

        if self.gnn == 'gcn':
            self.convs.append(GCNConv(self.in_dim, self.hid_dim))
            
            for _ in range(self.num_layers - 1):
                self.convs.append(GCNConv(self.hid_dim, self.hid_dim))
            
            if self.mode == 'node':
                self.cls = GCNConv(self.hid_dim, self.num_classes)
        elif self.gnn == 'sage':
            self.convs.append(SAGEConv(self.in_dim, self.hid_dim))
            
            for _ in range(self.num_layers - 1):
                self.convs.append(SAGEConv(self.hid_dim, self.hid_dim))

            if self.mode == 'node':
                self.cls = SAGEConv(self.hid_dim, self.num_classes)
        elif self.gnn == 'gat':
            self.convs.append(GATConv(self.in_dim, self.hid_dim, heads=1, concat=False))
            
            for _ in range(self.num_layers - 1):
                self.convs.append(GATConv(self.hid_dim, self.hid_dim, heads=1, concat=False))

            if self.mode == 'node':
                self.cls = GATConv(self.hid_dim, self.num_classes, heads=1, concat=False)
        elif self.gnn == 'gin':
            self.convs.append(GINConv(Sequential(Linear(self.in_dim, self.hid_dim)), train_eps=True))

            for _ in range(self.num_layers - 1):
                self.convs.append(GINConv(Sequential(Linear(self.hid_dim, self.hid_dim)), train_eps=True))

            if self.mode == 'node':
                self.cls = GINConv(Sequential(Linear(self.hid_dim, self.num_classes)), train_eps=True)
        
        if self.mode == 'graph':
            self.cls = Linear(self.hid_dim, self.num_classes)

            
    def forward(self, x, edge_index, edge_weight=None, batch=None):
        """
        Forward pass of the GNN model.

        Parameters
        ----------
        x : torch.Tensor
            Node feature matrix, shape (num_nodes, in_dim).
        edge_index : torch.Tensor
            Edge indices, shape (2, num_edges).
        edge_weight : torch.Tensor, optional
            Edge weights. Default: None.
        batch : torch.Tensor, optional
            Batch vector for graph-level tasks. Default: None.

        Returns
        -------
        torch.Tensor
            Log-softmax probabilities:
            - For node mode: shape (num_nodes, num_classes)
            - For graph mode: shape (num_graphs, num_classes)

        Notes
        -----
        Process:
        
        1. Feature transformation through GNN layers
        2. Graph pooling (if graph-level task)
        3. Classification
        4. Log-softmax normalization
        """
        x = self.feat_bottleneck(x, edge_index, edge_weight)
        if self.mode == 'graph':
            x = global_mean_pool(x, batch)
        x = self.feat_classifier(x, edge_index, edge_weight) 

        x = F.log_softmax(x, dim=1)

        return x
    
    def feat_bottleneck(self, x, edge_index, edge_weight=None):
        """
        Feature extraction through GNN layers.

        Parameters
        ----------
        x : torch.Tensor
            Node feature matrix.
        edge_index : torch.Tensor
            Edge indices.
        edge_weight : torch.Tensor, optional
            Edge weights. Default: None.

        Returns
        -------
        torch.Tensor
            Transformed node features.

        Notes
        -----
        Process:

        1. Sequential GNN layer application
        2. Activation (except last layer)
        3. Dropout regularization
        """
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index, edge_weight)
            if i < len(self.convs) - 1:
                x = self.act(x)
                x = F.dropout(x, p=self.dropout, training=self.training)

        return x
    
    def feat_classifier(self, x, edge_index, edge_weight=None):
        """
        Final classification layer.

        Parameters
        ----------
        x : torch.Tensor
            Node features from bottleneck.
        edge_index : torch.Tensor
            Edge indices.
        edge_weight : torch.Tensor, optional
            Edge weights. Default: None.

        Returns
        -------
        torch.Tensor
            Classification logits.

        Notes
        -----
        Two modes:

        - Node mode: Uses GNN classifier
        - Graph mode: Uses linear classifier
        """
        if self.mode == 'node':
            x = self.cls(x, edge_index, edge_weight)
        else:
            x = self.cls(x)
        
        return x
