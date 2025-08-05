import torch
from torch import nn
import torch.nn.functional as F

from torch_geometric.nn import GCNConv, SAGEConv, GATConv, GINConv
from torch.nn import Sequential, Linear

from torch_geometric.nn import global_mean_pool


class CWGCNBase(nn.Module):
    """
    Base class for CWGCN.

    Parameters
    ----------
    in_dim : int
        Input dimension of model.
    hid_dim : int
        Hidden dimension of model.
    num_classes : int
        Number of classes.
    num_layers : int, optional
        Total number of layers in model. Default: 2.
    dropout : float, optional
        Dropout rate. Default: 0.1.
    act : callable, optional
        Activation function. Default: torch.nn.functional.relu.
    gnn : str, optional
        The backbone GNN model type ('gcn', 'sage', 'gat', 'gin'). Default: 'gcn'.
    mode : str, optional
        Task mode ('node' or 'graph'). Default: 'node'.
    **kwargs : dict, optional
        Additional parameters for the backbone.

    Notes
    -----
    Currently supports only 2-layer architectures with various GNN backbones.
    """

    def __init__(self,
                 in_dim,
                 hid_dim,
                 num_classes,
                 num_layers=2,
                 dropout=0.1,
                 act=F.relu,
                 gnn='gcn',
                 mode='node',
                 **kwargs):
        super(CWGCNBase, self).__init__()

        assert gnn in ('gcn', 'sage', 'gat', 'gin'), 'Invalid gnn backbone'
        assert num_layers==2, 'unsupport number of layers'
        
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
        Forward pass of the model.

        Parameters
        ----------
        x : torch.Tensor
            Node feature matrix.
        edge_index : torch.Tensor
            Edge indices.
        edge_weight : torch.Tensor, optional
            Edge weights. Default: None.
        batch : torch.Tensor, optional
            Batch vector for graph-level tasks. Default: None.

        Returns
        -------
        tuple
            Contains:
            - torch.Tensor: Final node/graph representations
            - list: Intermediate representations from each layer
        """
        x, x_list = self.feat_bottleneck(x, edge_index, edge_weight, batch)
        x = self.feat_classifier(x, edge_index, edge_weight)

        return x, x_list
    
    def feat_bottleneck(self, x, edge_index, edge_weight=None, batch=None):
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
        batch : torch.Tensor, optional
            Batch vector for graph-level tasks. Default: None.

        Returns
        -------
        tuple
            Contains:
            - torch.Tensor: Final bottleneck features
            - list: Layer-wise features for domain adaptation
        """
        x_list = []
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index, edge_weight)
            if i < len(self.convs) - 1:
                x = self.act(x)
                x = F.dropout(x, p=self.dropout, training=self.training)
            if self.mode == 'node':
                x_list.append(x)
            else:
                x_list.append(global_mean_pool(x, batch))
        
        if self.mode == 'graph':
            x = global_mean_pool(x, batch)

        return x, x_list
    
    def feat_classifier(self, x, edge_index, edge_weight=None):
        """
        Classification layer after feature extraction.

        Parameters
        ----------
        x : torch.Tensor
            Input features.
        edge_index : torch.Tensor
            Edge indices.
        edge_weight : torch.Tensor, optional
            Edge weights. Default: None.

        Returns
        -------
        torch.Tensor
            Classification logits.
        """
        if self.mode == 'graph':
            x = self.cls(x)
        else:
            x = self.cls(x, edge_index, edge_weight)
        
        return x
    
    def c_loss(self, preds, labels):
        """
        Compute correntropy-induced loss.

        Parameters
        ----------
        preds : torch.Tensor
            Model predictions.
        labels : torch.Tensor
            Ground truth labels.

        Returns
        -------
        tuple
            Contains:
            - torch.Tensor: Correntropy loss value
            - torch.Tensor: Sample weights based on prediction-label distance
        """
        p = torch.sigmoid(preds)
        labels = F.one_hot(labels).to(preds.device)
        distance = torch.sum(torch.square(preds - labels), dim=1)

        loss = torch.mean(1 - torch.exp(torch.div(-distance, 100)))

        self.weight = torch.exp(torch.div(-distance, 10))

        return loss, self.weight
