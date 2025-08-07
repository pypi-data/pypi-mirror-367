import copy
import os
from typing import Callable, Literal, Optional, Sequence, Union

import mlx.core as mx
import numpy as np

from mlx_graphs.data import GraphData
from mlx_graphs.datasets.base_dataset import DEFAULT_BASE_DIR, BaseDataset


class Dataset(BaseDataset):
    """
    A dataset class for graph data. ``download`` and ``process`` methods must be
    implemented by children classes. The ``save`` and ``load`` methods save and load
    only the processed ``self.graphs`` attribute by default. You may want to
    override them to store/load additional processed attributes.

    Graph data within the dataset should be stored in ``self.graphs`` as
    a `list[GraphData]`. The creation and preprocessing of this list of graphs
    is typically done within the overridden ``process`` method.

    Args:
        name: name of the dataset
        base_dir: Directory where to store dataset files. Default is
            in the local directory ``.mlx_graphs_data/``.
        pre_transform: A function/transform that takes in a ``GraphData`` object and
            returns a transformed version. The transformation is applied before
            the first access.
        transform: A function/transform that takes in a ``GraphData`` object and returns
            a transformed version. The transformation is applied before every access,
            i.e., during the ``__getitem__`` call.
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
        self.graphs: list[GraphData] = []
        self._load()

    @property
    def processed_path(self) -> str:
        """
        The path where raw files are stored. Defaults at `<base_dir>/<name>/processed`
        """
        return os.path.expanduser(os.path.join(self._base_dir, self.name, "processed"))

    @property
    def num_graphs(self) -> int:
        """Returns the number of graphs in the dataset."""
        return len(self)

    @property
    def num_node_classes(self) -> Union[int, dict[str, int]]:
        """Returns the number of node classes to predict."""
        return self._num_classes("node")

    @property
    def num_edge_classes(self) -> Union[int, dict[str, int]]:
        """Returns the number of edge classes to predict."""
        return self._num_classes("edge")

    @property
    def num_graph_classes(self) -> Union[int, dict[str, int]]:
        """Returns the number of graph classes to predict."""
        return self._num_classes("graph")

    @property
    def num_node_features(self) -> int:
        """Returns the number of node features."""
        return self.graphs[0].num_node_features

    @property
    def num_edge_features(self) -> int:
        """Returns the number of edge features."""
        return self.graphs[0].num_edge_features

    @property
    def num_graph_features(self) -> int:
        """Returns the number of graph features."""
        return self.graphs[0].num_graph_features

    def _num_classes(
        self, task: Literal["node", "edge", "graph"]
    ) -> Union[int, dict[str, int]]:
        flattened_labels = []
        num_classes_dict = {}
        for g in self.graphs:
            labels = getattr(g, f"{task}_labels")
            if labels is not None:
                flattened_labels.append(labels)

        if len(flattened_labels) == 0 and len(num_classes_dict) == 0:
            return 0
        else:
            if len(flattened_labels) > 0:
                flattened_labels = np.concatenate(flattened_labels)
                return np.unique(flattened_labels).size
            else:
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

    def __len__(self):
        """Number of examples in the dataset"""
        return len(self.graphs)

    def __getitem__(
        self,
        idx: Union[int, np.integer, slice, mx.array, np.ndarray, Sequence],
    ) -> Union["Dataset", GraphData]:
        """
        Returns graphs from the ``Dataset`` at given indices.

        If ``idx`` contains multiple indices (e.g. list or slice), then
        another ``Dataset`` object containing the corresponding indexed graphs
        is returned.
        If ``idx`` is a single index (e.g. int), then a single ``GraphData``
        is returned.

        Args:
            idx: Indices or index of the graphs to gather from the dataset.

        Returns:
            A ``Dataset`` if ``idx`` contains multiple elements, or a
                ``GraphData`` otherwise.
        """
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
                f"Dataset indexing failed. Accepted indices are: int, mx.array, "
                f"list, tuple, np.ndarray (got '{type(idx).__name__}')"
            )

        dataset = copy.copy(self)
        graphs = [self.graphs[i] for i in indices]
        if self.transform is not None:
            graphs = [self.transform(g) for g in graphs]
        dataset.graphs = graphs
        return dataset

    def __repr__(self):
        return (
            self.name if len(self) is None else f"{self.name}(num_graphs={len(self)})"
        )
