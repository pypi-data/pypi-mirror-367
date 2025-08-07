import copy
from typing import Any, Callable, Literal, Optional, Sequence, Union

import mlx.core as mx
import numpy as np

from mlx_graphs.data import HeteroGraphData
from mlx_graphs.datasets.base_dataset import DEFAULT_BASE_DIR, BaseDataset


class HeteroDataset(BaseDataset):
    """
    A dataset class for handling heterogeneous graph data.

    Args:
        name: name of the dataset
        base_dir: Directory where to store dataset files. Default is
            in the local directory ``.mlx_graphs_data/``.
        pre_transform: A function/transform that takes in a ``HeteroGraphData`` object
            and returns a transformed version. The transformation is applied before
            the first access.
        transform: A function/transform that takes in a ``HeteroGraphData`` object and
            returns a transformed version. The transformation is applied before every
            access, i.e., during the ``__getitem__`` call.
            By default, no transformation is applied.
    """

    def __init__(
        self,
        name: str,
        base_dir: Optional[str] = None,
        pre_transform: Optional[Callable] = None,
        transform: Optional[Callable] = None,
    ):
        self._name = name
        self._base_dir = base_dir if base_dir else DEFAULT_BASE_DIR
        self.transform = transform
        self.pre_transform = pre_transform
        self.graphs: list[HeteroGraphData] = []
        self._load()

    @property
    def num_node_features(self) -> dict[str, int]:
        """Returns a dictionary of the number of node features for each node type."""
        return self.graphs[0].num_node_features

    @property
    def num_edge_features(self) -> dict[str, int]:
        """Returns a dictionary of the number of edge features for each edge type."""
        return self.graphs[0].num_edge_features

    @property
    def num_graph_features(self) -> int:
        """Returns the number of graph features."""
        return self.graphs[0].num_graph_features

    @property
    def num_node_classes(self) -> Union[dict[str, int], None]:
        """Returns a dictionary of the number of node classes for each node type."""
        return self.graphs[0].num_node_classes

    @property
    def num_edge_classes(self) -> dict[Any, int]:
        """Returns a dictionary of the number of edge classes for each edge type."""
        return self.graphs[0].num_edge_classes

    @property
    def num_nodes(self) -> dict[str, int]:
        """Returns a dictionary of the number of nodes for each node type."""
        return self.graphs[0].num_nodes

    @property
    def num_edges(self) -> dict[Any, int]:
        """Returns a dictionary of the number of edges for each edge type."""
        return self.graphs[0].num_edges

    def _num_classes(
        self, task: Literal["node", "edge", "graph"]
    ) -> Union[dict[str, int], int]:
        num_classes_dict = {}
        for g in self.graphs:
            if task == "node":
                labels_dict = g.node_labels_dict
                if labels_dict is not None:
                    for node_type, labels in labels_dict.items():
                        if node_type not in num_classes_dict:
                            num_classes_dict[node_type] = []
                        num_classes_dict[node_type].append(labels)
            elif task == "edge":
                labels_dict = g.edge_labels_dict
                if labels_dict is not None:
                    for edge_type, labels in labels_dict.items():
                        if edge_type not in num_classes_dict:
                            num_classes_dict[edge_type] = []
                        num_classes_dict[edge_type].append(labels)
            else:  # task == "graph"
                labels = g.graph_labels
                if labels is not None:
                    if None not in num_classes_dict:
                        num_classes_dict[None] = []
                    num_classes_dict[None].append(labels)
        if task == "node" or task == "edge":
            return {
                key: np.unique(np.concatenate(labels)).size
                for key, labels in num_classes_dict.items()
            }
        else:  # task == "graph"
            graph_labels = num_classes_dict.get(None)
            if graph_labels is not None:
                return np.unique(np.concatenate(graph_labels)).size
            else:
                return 0

    def __getitem__(
        self,
        idx: Union[int, np.integer, slice, mx.array, np.ndarray, Sequence],
    ) -> Union["HeteroDataset", HeteroGraphData]:
        indices = range(len(self))

        if isinstance(idx, (int, np.integer)) or (
            isinstance(idx, mx.array) and idx.ndim == 0  # type: ignore
        ):
            index = indices[idx]  # type:ignore - idx here is a singleton
            data = self.graphs[index]

            if self.transform is not None:
                data = self.transform(data)

            return data

        if isinstance(idx, slice):
            indices = indices[idx]

        elif isinstance(idx, mx.array) and idx.dtype in [  # type: ignore
            mx.int64,
            mx.int32,
            mx.int16,
        ]:
            return self[idx.flatten().tolist()]  # type: ignore - idx is a mx.array

        elif isinstance(idx, np.ndarray) and idx.dtype == np.int64:
            return self[idx.flatten().tolist()]

        elif isinstance(idx, Sequence) and not isinstance(idx, str):
            indices = [indices[i] for i in idx]

        else:
            raise IndexError(
                f"HeteroGraphDataset indexing failed."
                f"Accepted indices are: int, mx.array,"
                f"list, tuple, np.ndarray (got '{type(idx).__name__}')"
            )

        dataset = copy.copy(self)
        graphs = [self.graphs[i] for i in indices]
        if self.transform is not None:
            graphs = [self.transform(g) for g in graphs]
        dataset.graphs = graphs
        return dataset
