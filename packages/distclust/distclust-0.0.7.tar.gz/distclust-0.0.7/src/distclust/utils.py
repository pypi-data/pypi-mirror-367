import numpy as np
from scipy.spatial import distance
import pandas as pd
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import json


def denormalize(matrix, min_values, max_values):
    """
    Reverse the normalization process to recover original scale values.

    Parameters
    ----------
    matrix : numpy.ndarray
        Normalized data.
    min_values : numpy.ndarray
        Minimum values per dimension from the original data.
    max_values : numpy.ndarray
        Maximum values per dimension from the original data.

    Returns
    -------
    numpy.ndarray
        Data rescaled back to the original units using the provided min and max values.
    """
    # Scale the normalized values by the original range
    # and then shift them back using the original minimum
    return matrix * (max_values - min_values) + min_values


def dataframe_to_json(df, columns=None):
    """
    Convert a pandas DataFrame to a JSON format.

    Parameters:
    df (pandas.DataFrame): The DataFrame to convert.

    Returns:
    str: JSON string representing the DataFrame.
    """
    # Convert DataFrame to dictionary format
    if columns is None:
        df_dict = df.to_dict(orient='index')
    else:
        df_dict = df[columns].to_dict(orient='index')
    for row in df_dict.values():
        for key, value in row.items():
            if isinstance(value, np.ndarray):
                row[key] = value.tolist()
    # Convert dictionary to JSON
    json_result = json.dumps(df_dict, indent=4)

    return json_result


def list_of_lists_to_json(list_of_lists):
    """
    Convert a list of lists into a JSON-formatted string with IDs.

    Parameters
    ----------
    list_of_lists : list of list
        A list where each element is itself a list of data points.

    Returns
    -------
    str
        JSON string containing the data with assigned IDs and indentation.
    """
    json_data = {}
    for idx, lst in enumerate(list_of_lists):
        json_data[idx + 1] = {
            'id': idx + 1,
            'data points': lst
        }

    json_output = json.dumps(json_data, indent=4)
    return json_output


def json_content_to_list_of_lists(json_content):
    """
    Convert JSON-formatted data into a list of lists of tuples.

    Parameters
    ----------
    json_content : str
        JSON string containing data with an 'id' and 'data points' for each entry.

    Returns
    -------
    list of list of tuple
        A list where each element is a list of tuples representing data points.
    """
    json_data = json.loads(json_content)

    list_of_lists = []
    for key in sorted(json_data.keys(), key=int):
        list_of_lists.append(
            [tuple(item) for item in json_data[key]['data points']]
        )

    return list_of_lists


def merge_list(list_of_lists):
    """
    Merge a list of lists into a single list of unique elements.

    Parameters
    ----------
    list_of_lists : list of list
        A list containing multiple sublists to be merged.

    Returns
    -------
    list
        A list containing the unique elements from all sublists.
    """
    merged = []
    for sublist in list_of_lists:
        merged.extend(sublist)  # more efficient than += for lists
    return list(set(merged))


def density_calc(list_base, list_point):
    """
    Calculate the relative frequency of each element in list_base
    with respect to list_point.

    Parameters
    ----------
    list_base : list
        Base list of reference elements.
    list_point : list
        List of elements whose frequencies will be calculated.

    Returns
    -------
    tuple
        list_point_final : list
            Elements from list_base that appear in list_point.
        list_density : list
            Relative frequencies of elements from list_base in list_point.
    """
    n = len(list_point)
    list_base = list(set(list_base))
    list_density = []
    list_point_final = []
    for i in list_base:
        if i in list_point:
            list_density.append(list_point.count(i) / n)
            list_point_final.append(i)
        else:
            list_density.append(0)  # changed
    return list_point_final, list_density


def density_calc_list(list_of_list, list_base):
    """
    Calculate density values for each list in a collection of lists.

    Parameters
    ----------
    list_of_list : list of list
        A collection of lists for which densities will be calculated.
    list_base : list
        Base list of reference elements used in density calculation.

    Returns
    -------
    list
        A list of NumPy arrays containing density values for each input list.
    """
    list_density = []
    for i in list_of_list:
        list_density.append(
            np.array([density_calc(list_base, i)[1]]).transpose()
        )
    return list_density


def calculate_euclidean_distance_matrix(list1, list2):
    """
    Calculate the pairwise Euclidean distance matrix between two lists of points.

    Parameters
    ----------
    list1 : list of list or array-like
        First set of points.
    list2 : list of list or array-like
        Second set of points.

    Returns
    -------
    numpy.ndarray
        A 2D array where element (i, j) is the Euclidean distance
        between list1[i] and list2[j].

    Raises
    ------
    ValueError
        If the two input lists do not have the same number of dimensions.
    """
    array1 = np.array(list1)
    array2 = np.array(list2)

    if array1.shape[1] != array2.shape[1]:
        raise ValueError("Input arrays must have the same number of dimensions")

    distance_matrix = distance.cdist(array1, array2)

    return distance_matrix


def calculate_exponential_matrix(distance_matrix, lamb):
    """
    Calculate the element-wise exponential transformation of a distance matrix.

    Parameters
    ----------
    distance_matrix : numpy.ndarray
        Matrix of distances.
    lamb : float
        Scaling parameter for the exponential transformation.

    Returns
    -------
    numpy.ndarray
        Exponentially transformed distance matrix, where each element is
        exp(-distance / lamb).
    """
    exponential_matrix = np.exp(-distance_matrix / lamb)
    return exponential_matrix


def create_blank_dataset_with_metadata(m):
    """
    Create a blank Pandas DataFrame with predefined metadata columns.

    Parameters
    ----------
    m : int
        Number of additional numbered columns to create.

    Returns
    -------
    pandas.DataFrame
        An empty DataFrame with columns for system number, data points,
        numbered columns from 0 to m-1, and a label column.
    """
    data = {
        'system num': [],
        'data points': [],
    }

    for i in range(1, m + 1):
        data[f'{i - 1}'] = []

    data['label'] = []
    blank_dataset = pd.DataFrame(data)

    return blank_dataset


def fill_dataset_with_records(dataset, records):
    """
    Append multiple records to a Pandas DataFrame.

    Parameters
    ----------
    dataset : pandas.DataFrame
        The DataFrame to which the records will be appended.
    records : list of dict
        A list of records, where each record is represented as a dictionary.

    Returns
    -------
    pandas.DataFrame
        The updated DataFrame containing the appended records.
    """
    for record in records:
        dataset = pd.concat([dataset, pd.DataFrame([record])], ignore_index=True)
    return dataset


def make_record(list_of_list, list_p):
    """
    Create a list of record dictionaries from data points and probability values.

    Parameters
    ----------
    list_of_list : list of list
        A list where each element is a list of data points for a system.
    list_p : list
        A list of probability values corresponding to each system.

    Returns
    -------
    list of dict
        A list of dictionaries, each containing:
        - 'system num': index of the system
        - 'data points': list of data points
        - 'p': probability value
    """
    records_to_be_added = []
    for i in range(len(list_of_list)):
        records_to_be_added.append({
            'system num': i,
            'data points': list_of_list[i],
            'p': list_p[i]
        })

    return records_to_be_added


def condensed_creator(arr):
    """
    Convert a square matrix into its condensed upper-triangle form.

    Parameters
    ----------
    arr : numpy.ndarray
        A square matrix.

    Returns
    -------
    list
        A list containing the upper-triangle elements of the matrix,
        excluding the diagonal.
    """
    m = arr.shape[0]

    # Extract upper triangle indices (excluding the diagonal)
    upper_triangle_indices = np.triu_indices(m, k=1)

    # Use the indices to get the upper triangle elements
    upper_triangle_elements = arr[upper_triangle_indices]

    # Convert the elements to a list
    upper_triangle_list = upper_triangle_elements.tolist()

    return upper_triangle_list


def plot_dendrogram(df, save_file=False, file_path=None):
    """
    Plot a dendrogram from a distance matrix stored in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing pairwise distances between systems.
    save_file : bool, optional
        If True, saves the dendrogram as a PNG file. Default is False.

    Returns
    -------
    None
    """
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()

    scaled_matrix = matrix_final
    np.fill_diagonal(scaled_matrix, 0)

    matrix_final = condensed_creator(scaled_matrix)
    linkage_matrix = linkage(matrix_final, method='complete')

    plt.figure(figsize=(10, 7))
    dendrogram(
        linkage_matrix,
        color_threshold=-np.inf,
        above_threshold_color='gray'
    )
    plt.xlabel('Distributions', fontsize=18, labelpad=20)  # X-axis label
    plt.xticks([])  # Remove x-axis tick labels
    plt.ylabel('Distance', fontsize=18)

    if save_file:
        plt.savefig(f'{file_path}.png', format='png', dpi=1000)
    plt.show()


def silhouette_score_agglomerative(df):
    """
    Compute silhouette scores for agglomerative clustering.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing pairwise distances between systems (as columns
        named '0', '1', ..., len(df)-1).

    Returns
    -------
    list of float
        Silhouette scores for cluster counts from 2 up to len(df) - 1,
        computed with metric='precomputed'.
    """
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()
    min_val = np.min(matrix)
    scaled_matrix = (matrix_final - min_val)
    np.fill_diagonal(scaled_matrix, 0)
    silhouette_score_list = []
    for i in range(2, len(df)):
        index_list = cluster_list_creator(df, i)
        silhouette_score_list.append(
            silhouette_score(scaled_matrix, index_list, metric='precomputed')
        )
    return silhouette_score_list


def entropy(matrix):
    """
    Calculate the entropy of a matrix, considering only positive entries.

    Parameters
    ----------
    matrix : array-like
        Input matrix or array.

    Returns
    -------
    float
        The entropy value computed as:
        -sum(p * log(p)) for all p > 0 in the matrix.
    """
    matrix = np.array(matrix)
    non_zero_entries = matrix[matrix > 0]
    entropy_value = -np.sum(non_zero_entries * np.log(non_zero_entries))

    return entropy_value


def cluster_list_creator(df, num_of_clusters):
    """
    Create a list of cluster labels for each item based on complete-linkage
    agglomerative clustering.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame whose columns '0', '1', ..., len(df)-1 contain a (possibly
        asymmetric) pairwise distance representation.
    num_of_clusters : int
        Desired number of clusters.

    Returns
    -------
    list
        A list of integer cluster labels (0-based) of length len(df),
        indicating the assigned cluster for each item.
    """
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()

    min_val = np.min(matrix)
    max_val = np.max(matrix)
    scaled_matrix = (matrix_final - min_val) / (max_val - min_val)
    np.fill_diagonal(scaled_matrix, 0)
    matrix_final = condensed_creator(scaled_matrix)

    linkage_matrix = linkage(matrix_final, method='complete')

    height = np.shape(linkage_matrix)[0]
    list_linkage = [[i] for i in range(len(df))]
    for i in range(height):
        list_linkage.append(
            list_linkage[int(linkage_matrix[i][0])] +
            list_linkage[int(linkage_matrix[i][1])]
        )

    list_linkage_inverse = list_linkage[::-1]
    list_final = list_linkage_inverse[num_of_clusters - 1:]
    list_index = []
    for i in range(len(df)):
        for j in list_final:
            if i in j:
                list_index.append(list_final.index(j))
                break

    return list_index


def calculate_OT_cost(p, q, reg, cost_matrix, num_iterations=100, stop_threshold=1e-9):
    """
    Compute the entropically-regularized optimal transport plan via Sinkhorn updates.

    Parameters
    ----------
    p : array-like
        Source probability vector (will be flattened to 1D).
    q : array-like
        Target probability vector (will be flattened to 1D).
    reg : float
        Entropic regularization parameter (lambda).
    cost_matrix : array-like
        Pairwise cost matrix between source and target supports.
    num_iterations : int, optional
        Maximum number of Sinkhorn iterations. Default is 100.
    stop_threshold : float, optional
        Convergence threshold on consecutive v-updates (L2 norm). Default is 1e-9.

    Returns
    -------
    numpy.ndarray
        The optimal transport plan (matrix) computed from the final scaling factors.

    Notes
    -----
    This function performs classic Sinkhorn scaling:
    u <- p / (K v), v <- q / (K^T u), where K = exp(-C / reg).
    """
    # Ensure 1D arrays
    p = np.asarray(p).flatten()
    q = np.asarray(q).flatten()

    # Kernel
    Xi = np.exp(-cost_matrix / reg)

    # Initialize v
    v = np.ones_like(q)

    for _ in range(num_iterations):
        v_old = v.copy()
        u = p / (Xi @ v)
        v = q / (Xi.T @ u)
        if np.linalg.norm(v - v_old) < stop_threshold:
            break

    OT_plan = np.outer(u, v) * Xi

    return OT_plan


def fill_ot_distance(df, num_of_iterations, lambda_pen, stop_threshold):
    """
    Fill a DataFrame with pairwise entropic OT distances between systems.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame whose rows contain 'data points' (support) and 'p' (probability masses)
        for each system. Distances will be written into string-named columns ('0', '1', ...).
    num_of_iterations : int
        Maximum number of iterations for the Sinkhorn solver.
    lambda_pen : float
        Entropic regularization parameter (same as 'reg' in OT computation).
    stop_threshold : float
        Convergence threshold for the Sinkhorn updates.
    """
    for i in range(len(df)):  # Here we iterate among rows, and below we shall calculate the densities
        for j in range(i + 1):
            cost_matrix = distance.cdist(df['data points'][i], df['data points'][j])
            OT_plan_test = calculate_OT_cost(
                df['p'][i],
                df['p'][j],
                lambda_pen,
                cost_matrix,
                num_of_iterations,
                stop_threshold
            )
            OT_cost_test = np.multiply(OT_plan_test, cost_matrix).sum()  # yakhoda
            df.at[j, str(i)] = OT_cost_test


def normalize_tuples(list_of_lists):
    """
    Normalize each dimension of tuples in a list of lists to the [0, 1] range.

    Parameters
    ----------
    list_of_lists : list of list of tuple
        Nested list where each inner list contains tuples of equal length
        (same dimensionality).

    Returns
    -------
    tuple
        normalized_list_of_lists : list of list of tuple
            Same structure as input, with each dimension scaled to [0, 1].
        min_values : numpy.ndarray
            Minimum value per dimension (before normalization).
        max_values : numpy.ndarray
            Maximum value per dimension (before normalization).
    """
    num_dimensions = len(list_of_lists[0][0])  # Get the number of dimensions from the first tuple

    # Extract all values for each dimension
    all_values = [[] for _ in range(num_dimensions)]
    for sublist in list_of_lists:
        for i, t in enumerate(sublist):
            for j in range(num_dimensions):
                all_values[j].append(t[j])

    # Compute the minimum and maximum values for each dimension
    min_values = [min(dim_values) for dim_values in all_values]
    max_values = [max(dim_values) for dim_values in all_values]

    # Normalize each dimension of each tuple
    normalized_list_of_lists = []
    for sublist in list_of_lists:
        normalized_sublist = []
        for t in sublist:
            normalized_t = tuple(
                (t[j] - min_values[j]) / (max_values[j] - min_values[j]) for j in range(num_dimensions)
            )
            normalized_sublist.append(normalized_t)
        normalized_list_of_lists.append(normalized_sublist)

    return normalized_list_of_lists, np.array(min_values), np.array(max_values)


def proximal_mapping(a, gradient, t0_beta):
    """
    Perform a proximal mapping step under KL (entropy) Bregman divergence.

    Parameters
    ----------
    a : array-like
        Current iterate (e.g., a probability vector).
    gradient : array-like
        Gradient/subgradient at the current iterate.
    t0_beta : float
        Step size parameter for the proximal update.

    Returns
    -------
    numpy.ndarray
        The updated vector a_tilde, re-normalized to sum to 1.
    """
    # Proximal mapping using Kullback–Leibler divergence as the Bregman divergence
    a_tilde = a * np.exp(-t0_beta * gradient)
    a_tilde /= np.sum(a_tilde)
    return a_tilde


def opt_a(X, Y_list, b_list, t0, tol=1e-9, max_iter=1000):
    """
    Optimize the mass vector 'a' for Wasserstein barycenter computation.

    Parameters
    ----------
    X : numpy.ndarray
        Current support locations for the barycenter (shape: n x d).
    Y_list : list of numpy.ndarray
        List of support locations for each input distribution.
    b_list : list of numpy.ndarray
        List of probability vectors (column vectors) corresponding to Y_list.
    t0 : float
        Base step size parameter.
    tol : float, optional
        Convergence tolerance on ||a_tilde - a_hat||. Default is 1e-9.
    max_iter : int, optional
        Maximum number of iterations. Default is 1000.

    Returns
    -------
    numpy.ndarray
        Final estimate of the probability vector a_hat (as a column vector).
    """
    n = X.shape[0]

    M_list = [np.linalg.norm(X[:, np.newaxis] - Y, axis=2) for Y in Y_list]
    a_hat = (np.ones(n) / n).reshape((n, 1))
    a_tilde = a_hat
    t = 3
    converged = False
    while not converged and t < max_iter:
        beta = (t + 1) / 2
        a = (1 - beta ** -1) * a_hat + beta ** -1 * a_tilde

        # Form subgradient alpha
        alpha_list = [
            calculate_OT_cost_bary(a, b_list[i], 0.5, M_list[i], num_iterations=100, stop_theshold=10 ** -9)[1] for i in
            range(len(b_list))]
        alpha = np.mean(alpha_list, axis=0)
        # Update a_tilde using the proximal mapping
        t0_beta = t0 * beta
        a_tilde = proximal_mapping(a, alpha, t0_beta)
        #         # Update a_hat
        a_hat = (1 - beta ** -1) * a_hat + (beta ** -1) * a_tilde

        #         # Check convergence
        if np.linalg.norm(a_tilde - a_hat) < tol:
            converged = True

        t += 1
    return a_hat


def find_barycenter(X, Y_list, b_list, reg, t0, theta, tol=1e-9, max_iter=1000):
    """
    Compute a Wasserstein barycenter by alternating updates of support locations (X)
    and masses (a), using entropic OT subproblems.

    Parameters
    ----------
    X : numpy.ndarray
        Initial barycenter support locations (shape: n x d).
    Y_list : list of numpy.ndarray
        List of support locations for each input distribution.
    b_list : list of numpy.ndarray
        List of probability vectors (column vectors) corresponding to Y_list.
    t0 : float
        Base step size parameter for the a-update routine.
    theta : float
        Relaxation parameter for updating X.
    tol : float, optional
        Convergence tolerance on ||X - X_old||_2. Default is 1e-9.
    max_iter : int, optional
        Maximum number of outer iterations. Default is 1000.

    Returns
    -------
    tuple
        X : numpy.ndarray
            Final barycenter support locations.
        a_update : numpy.ndarray
            Final barycenter probability vector (column vector).
    """
    iter_num = 1
    while iter_num < max_iter:
        M_list = [np.linalg.norm(X[:, np.newaxis] - Y, axis=2) for Y in Y_list]

        a_update = opt_a(X, Y_list, b_list, t0, tol=1e-2, max_iter=30)

        T_list = [
            calculate_OT_cost_bary(a_update, b_list[i], reg, M_list[i], num_iterations=50, stop_theshold=10 ** -2)[0]
            for i in range(len(b_list))
        ]
        YT_list = [T_list[i] @ Y_list[i] for i in range(len(Y_list))]
        YT_ave = np.mean(YT_list, axis=0)
        X_old = X
        X = (1 - theta) * X + theta * (np.diag((a_update ** -1).T[0]) @ YT_ave)

        if np.linalg.norm(X - X_old) < tol:
            return X, a_update
        iter_num += 1

    return X, a_update


def calculate_OT_cost_bary(p, q, reg, cost_matrix, num_iterations, stop_theshold):
    """
    Solve an entropically regularized OT subproblem (barycenter variant) and
    return the transport plan and scaling vectors.

    Parameters
    ----------
    p : numpy.ndarray
        Source probability vector (column vector).
    q : numpy.ndarray
        Target probability vector (column vector).
    reg : float
        Entropic regularization parameter.
    cost_matrix : numpy.ndarray
        Pairwise cost matrix between source and target supports.
    num_iterations : int
        Maximum number of Sinkhorn iterations.
    stop_theshold : float
        Convergence threshold on successive v-updates (L2 norm).

    Returns
    -------
    tuple
        OT_plan : numpy.ndarray
            Optimal transport plan matrix.
        u_vec : numpy.ndarray
            Left scaling vector (p / (Xi @ v)).
        v_vec : numpy.ndarray
            Right scaling vector (v).
    """
    Xi = np.exp(-cost_matrix / reg)
    v_n = np.ones((Xi.shape[1], 1))
    v_old = v_n
    for _ in range(num_iterations):
        v_n = q / (Xi.T @ (p / (Xi @ v_n)))
        if np.linalg.norm(v_n - v_old) < stop_theshold:
            break
        v_old = v_n
    diag_u = np.diagflat((p / (Xi @ v_n)))
    diag_v = np.diagflat(v_n)
    OT_plan = diag_u @ Xi @ diag_v
    return OT_plan, p / (Xi @ v_n), v_n


def cluster_distributions(
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
    """
    Cluster simulation output distributions using entropically regularized optimal transport (OT)
    distances with agglomerative hierarchical clustering, and optionally compute cluster barycenters.

    Parameters
    ----------
    dist_dict : dict
        A dictionary containing the empirical distributions to be clustered.
        Each key is a unique identifier for a distribution (as a string), and each value is a
        dictionary containing:
            - "id": Unique distribution ID (string)
            - "data_points": List of support points (tuples or lists of coordinates)

    reg : float, optional (default=0.5)
        Entropic regularization parameter for regularized Wasserstein distance. Must be positive.

    n_clusters : int or None, optional (default=None)
        Number of clusters. If None, the optimal number is chosen using the silhouette score.

    calculate_barycenter : bool, optional (default=False)
        If True, computes the regularized Wasserstein barycenter for each cluster.

    stop_threshold : float, optional (default=1e-9)
        Convergence tolerance for iterative regularized Wasserstein distance computation.

    num_of_iterations : int, optional (default=1000)
        Maximum number of Sinkhorn iterations for each pairwise OT distance computation.

    plt_dendrogram : bool, optional (default=True)
        If True, displays a dendrogram of the hierarchical clustering.
        If `path_dendrogram` is provided, the plot is also saved.

    path_dendrogram : str or None, optional (default=None)
        Path to save the dendrogram image (e.g., "dendrogram.png").
        Only used if `plt_dendrogram=True`.

    sup_barycenter : int, optional (default=100)
        Number of support points to use when computing barycenters.

    t0 : float, optional (default=0.005)
        Base step size for updating the barycenter's mass vector (`a`) in the optimization routine.

    theta : float, optional (default=0.005)
        Relaxation parameter for updating the barycenter support locations (`X`).

    Returns
    -------
    clusters_dict : dict

    barycenters_dict : dict, optional
        Returned only if `calculate_barycenter=True`.
        A dictionary where each key is a cluster ID (int or str), and each value contains:
            - "support": List of barycenter support points
            - "p": Corresponding probability mass vector

    - If `plt_dendrogram=True`, displays a dendrogram of the clustering.
    - If `path_dendrogram` is provided, saves the dendrogram plot as a PNG file.
    """

    # Parse JSON into list-of-lists format and determine dimensionality
    dist_file = json.dumps(dist_file)
    list_sim_outputs_raw = json_content_to_list_of_lists(dist_file)
    dim = len(list_sim_outputs_raw[0][0])

    # Compute supports and probability masses for each system
    list_sim_outputs = []
    p_list = []
    for i in list_sim_outputs_raw:
        list_sim_outputs.append(density_calc(i, i)[0])
        p_list.append(density_calc(i, i)[1])

    # Normalize supports to [0, 1] range
    normalized_list_sim_outputs = normalize_tuples(list_sim_outputs)[0]

    # Create a blank dataset and fill it with system supports and probabilities
    m = len(normalized_list_sim_outputs)
    blank_df = create_blank_dataset_with_metadata(m)
    df = fill_dataset_with_records(
        blank_df,
        make_record(normalized_list_sim_outputs, p_list)
    )
    df['data points real'] = list_sim_outputs  # Keep unnormalized supports

    # Compute pairwise OT distances between all systems
    fill_ot_distance(
        df,
        num_of_iterations,
        reg,
        stop_threshold=stop_threshold
    )

    # Optionally plot dendrogram from OT distance matrix
    if plt_dendrogram is True and path_dendrogram is None:
        plot_dendrogram(df, save_file=False)
    elif plt_dendrogram is True and path_dendrogram is not None:
        plot_dendrogram(df, save_file=True, file_path=path_dendrogram)

    # Choose number of clusters by silhouette score if not provided
    sil_values = silhouette_score_agglomerative(df)
    if n_clusters is None:
        n_clusters = sil_values.index(max(sil_values)) + 2

    # Prepare symmetric OT distance matrix for agglomerative clustering
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()
    np.fill_diagonal(matrix_final, 0)

    # Perform hierarchical clustering and assign cluster labels
    upper_triangle_flat = matrix_final[np.triu_indices_from(matrix_final, k=1)]
    Z = linkage(upper_triangle_flat, method='complete')
    clusters = fcluster(Z, n_clusters, criterion='maxclust')
    df['cluster'] = clusters
    if calculate_barycenter is False:
        json_clusters = dataframe_to_json(df, ['system num', 'data points real', 'cluster'])
        dict_clusters = json.loads(json_clusters)
        return json_inputs

    # Initialize DataFrame for storing cluster-level data
    blank_df_clusters = create_blank_dataset_with_metadata(n_clusters)
    records_to_be_added = [{'cluster num': i, 'p': 0} for i in range(1, n_clusters + 1)]
    df_clusters = fill_dataset_with_records(blank_df_clusters, records_to_be_added)

    # Compute barycenters for each cluster
    min_values_all = []
    max_values_all = []
    list_bary_X = []
    list_bary_prob = []
    list_sup_cluster_new = []
    list_sup_cluster_real_new = []
    for i in range(1, len(df_clusters) + 1):
        df_test = df[df['cluster'] == i]

        # Extract cluster data points (real and normalized)
        list_column = df_test['data points real']
        list_sim_outputs_cluster = list_column.tolist()
        min_values_all.append(normalize_tuples(list_sim_outputs_cluster)[1])
        max_values_all.append(normalize_tuples(list_sim_outputs_cluster)[2])
        list_sim_outputs_cluster = normalize_tuples(list_sim_outputs_cluster)[0]

        # Merge supports and prepare for OT barycenter computation
        list_base_cluster = merge_list(list_sim_outputs_cluster)
        list_of_arrays = [np.array(inner_list) for inner_list in list_sim_outputs_cluster]
        X = np.random.rand(sup_barycenter, dim)
        b_list = [
            (np.ones(len(list_sim_outputs_cluster[i])) /
             len(list_sim_outputs_cluster[i])).reshape((len(list_sim_outputs_cluster[i]), 1))
            for i in range(len(list_sim_outputs_cluster))
        ]

        # Compute barycenter using entropic OT iterations
        bary_X, bary_a = find_barycenter(
            X, list_of_arrays, b_list, reg, t0, theta, tol=1e-5 * 0.9, max_iter=400
        )
        list_bary_X.append(bary_X)
        list_bary_prob.append(bary_a)

        # Store original (unnormalized) supports for the cluster
        list_column_real = df_test['data points real']
        list_sim_outputs_cluster_real = list_column_real.tolist()
        list_base_cluster_real = merge_list(list_sim_outputs_cluster_real)
        list_sup_cluster_new.append(list_base_cluster)
        list_sup_cluster_real_new.append(list_base_cluster_real)

    # Denormalize barycenter supports back to original scale
    matrices = [
        denormalize(list_bary_X[i], min_values_all[i], max_values_all[i])
        for i in range(len(list_bary_X))
    ]

    # Store barycenter probability masses and supports in df_clusters
    df_clusters['p'] = list_bary_prob
    df_clusters['data points'] = list_sup_cluster_new
    df_clusters['data points real'] = list_sup_cluster_real_new

    # Serialize results into JSON
    json_clusters = dataframe_to_json(df, ['system num', 'data points real', 'cluster'])
    json_barycenters = dataframe_to_json(df_clusters, ['data points real', 'p'])
    dict_clusters = json.loads(json_clusters)
    dict_barycenters = json.loads(json_barycenters)
    return dict_clusters, dict_barycenters
