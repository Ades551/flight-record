from multiprocessing import Pool, cpu_count
from typing import Any, Optional

import numpy as np
from profiling_decorators import time_profile
from sklearn.cluster import DBSCAN
from sklearn.neighbors import BallTree

ZOOM_LEVELS = [i for i in range(1, 8)]


class Cluster:
    def __init__(
        self, cluster: int, position: Optional[tuple[float, float]], data: Any
    ) -> None:
        self.cluster = cluster
        self.position = position
        self.data = data

    def json(self) -> dict[str, Any]:
        return {"cluster": self.cluster, "position": self.position, "data": self.data}


# TODO: in future change whole implementation
# since in the FE of the application planes are jumping all over the place
def get_cluster(data: list[dict[str, Any]], zoom: int) -> list[Cluster]:
    if not data:
        return []

    # positions to np.array
    X = np.array([i["position"] for i in data])
    # to use radians
    points_rad = np.radians(X)

    # eps was evaluated based on the graph using geogebra
    # so that there will be no big differences between zooms
    eps_0 = 0.1
    eps = eps_0 * 2 ** (-0.7 * zoom)
    clustering = DBSCAN(
        eps=eps, min_samples=2, algorithm="ball_tree", metric="haversine"
    ).fit(points_rad)

    # get lables (clusters)
    labels = clustering.labels_

    # find lables that are considered as noise
    label_clusters = np.where(labels != -1)[0]
    # assign noise to the closes cluster
    if len(label_clusters):
        tree = BallTree(points_rad[label_clusters])

        for noise in np.where(labels == -1)[0]:
            _, indices = tree.query([points_rad[noise]], k=2)
            nearest_cluster = labels[label_clusters[indices[0][1]]]
            labels[noise] = nearest_cluster

    clusters: list[Cluster] = []

    for label in set(labels):
        # find all coordinates that belong to this cluster
        indices = np.where(labels == label)[0]
        # calculate mean from lats and longs
        lat = np.mean([data[j]["position"][0] for j in indices])
        long = np.mean([data[j]["position"][1] for j in indices])
        clusters.append(
            Cluster(
                cluster=int(label),
                position=(lat, long),
                data=[{**data[j]} for j in indices],
            )
        )

    return clusters


@time_profile
def get_clusters(data: list[dict[str, Any]]) -> dict[int, list[Cluster]]:
    """Get cluster for each zoom."""

    # number of processes to be used
    p_count = x if (x := max(ZOOM_LEVELS)) < (y := cpu_count()) else y

    with Pool(processes=p_count) as p:
        result = p.starmap(get_cluster, [(data, zoom) for zoom in ZOOM_LEVELS])
        return {ZOOM_LEVELS[i]: value for i, value in enumerate(result)} | {
            -1: [Cluster(cluster=-1, position=None, data=data)]
        }
