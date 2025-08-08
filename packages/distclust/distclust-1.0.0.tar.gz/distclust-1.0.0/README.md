A Python package implementing the clustering algorithm proposed in the paper  
**"An Agglomerative Clustering Algorithm for Simulation Output Distributions Using Regularized Wasserstein Distance"**, accepted to the *INFORMS Journal on Data Science*.
The preprint is available on [arXiv:2407.12100](https://arxiv.org/abs/2407.12100).  
This link will be updated once the final published version becomes available.



The package can be installed using 

```python
pip install --index-url https://pypi.org/simple/ --no-deps distclust==1.0.0
```

## Main function
```python
dict_clusters, dict_barycenters = cluster_distributions(
    dist_file,
    reg=0.5,
    n_clusters=None,
    calculate_barycenter=False,
    stop_threshold=10 ** -9,
    num_of_iterations=1000,
    plt_dendrogram=True,
    path_dendrogram=None,
    sup_barycenter=100,
    t0=0.005,
    theta=0.005,
):
```

## Description
This function performs hierarchical (agglomerative) clustering of empirical probability distributions using the regularized (entropic) Wasserstein distance.  
It takes a JSON-formatted string that encodes a list of distributions, computes all pairwise regularized Wasserstein distances, and then performs agglomerative clustering.

- Returns one dictionary with each distribution and its assigned cluster.
- If `calculate_barycenter=True`, it also computes barycenters of each cluster and returns a second dictionary with the barycenters.

---

### Function Parameters

- **`dist_file`** *(dict)*:  
  A dictionary containing a dictionary of distributions.  
  Each key in the dictionary is a **distribution number**, mapped to another dictionary with:
  - `"id"`: The identifier of the distribution.  
  - `"data_points"`: A list of tuples representing the data points.  

  Example format: [`An example in Github`](https://github.com/mohammadmgh78/Agglomerative_Clustering_Distribution/blob/main/distclust/dict_test.txt)
- **`reg`** *(float)*:  
  Entropic regularization parameter for the Wasserstein distance. Must be positive.

- **`n_clusters`** *(int or None)*:  
  Number of clusters to form. If `None`, the optimal number is chosen using the silhouette index.

- **`calculate_barycenter`** *(bool)*:  
  If `True`, compute a regularized Wasserstein barycenter for each cluster.  
  If `False`, only clustering results are returned.

- **`stop_threshold`** *(float)*:  
  Convergence threshold for the Sinkhorn iterations.

- **`num_of_iterations`** *(int)*:  
  Maximum number of iterations for each regularized Wasserstein distance computation.
  
- **`plt_dendrogram`** : bool, optional (default=True)
        If True, display a dendrogram of the hierarchical clustering.
        If `path_dendrogram` is provided, the plot is also saved to the specified path.
  
- **`path_dendrogram`** : str or None, optional (default=None)
        If provided, path to save the dendrogram plot. Ignored if `plt_dendrogram=False`.
  
- **`sup_barycenter`** *(int)*:  
  Number of support points to initialize for barycenter computation.

- **`t0`** *(float)*:  
  Base step size for the barycenter probability vector (`a`) update.

- **`theta`** *(float)*:  
  Relaxation parameter for the barycenter support (`X`) update.

---

### Returns

If `calculate_barycenter=False`:
- **`dict_clusters`** *(dict)*: A dictionary with each distribution's ID, real data points, and assigned cluster label.

If `calculate_barycenter=True`:
- **`dict_clusters`** *(dict)*: A dictionary with each distribution's ID, real data points, and assigned cluster label.
- **`dict_barycenters`** *(dict)*: A dictionary with each cluster's barycenter, including unnormalized supports and probability masses.

If `plt_dendrogram=True`:
- Displays the dendrogram plot.  
- If `path_dendrogram` is provided, saves the dendrogram as a PNG file to that path.

## Other Functions in `distclust`

We also provide the following functions that might be useful to some users:

1. **`density_calc`** – Compute empirical probability masses.  
2. **`density_calc_list`** – Batch probability mass computation.  
3. **`fill_ot_distance`** – Compute and store regularized Wasserstein distances between all systems.  (Cuturi and Doucet (2014) [1])
4. **`plot_dendrogram`** – Dendrogram visualization.  
5. **`silhouette_score_agglomerative`** – Choose number of clusters.  
6. **`find_barycenter`** – Compute Wasserstein barycenter.  (Cuturi and Doucet (2014) [1])


## References

[1] Marco Cuturi and Arnaud Doucet. [**Fast computation of Wasserstein barycenters.**](https://proceedings.mlr.press/v32/cuturi14.html) In *Proceedings of the 31st International Conference on Machine Learning (ICML)*, pp. 685–693, 2014.  





