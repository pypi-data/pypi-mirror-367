from cProfile import label
import os
from typing import List, Tuple, Union
import numpy as np
from matplotlib.lines import Line2D
from matplotlib import colors, pyplot as plt
from matplotlib.colors import LogNorm
from scipy.stats import gaussian_kde
from sklearn.cluster import KMeans
import mdtraj
from idpet.featurization.distances import *
from idpet.ensemble_analysis import EnsembleAnalysis
from idpet.featurization.angles import featurize_a_angle
from idpet.coord import *
from idpet.featurization.glob import compute_asphericity, compute_prolateness
from idpet.comparison import scores_data, process_all_vs_all_output
from idpet.utils import logger
import plotly.express as px
import pandas as pd

PLOT_DIR = "plots"

def plot_histogram(
        ax: plt.Axes,
        data: List[np.ndarray],
        labels: List[str],
        bins: Union[int, List] = 50,
        range: Tuple = None,
        title: str = "Histogram",
        xlabel: str = "x",
        ylabel: str = "Density",
        location: str = None
    ):
    """
    Plot an histogram for different features.

    Parameters
    ----------
    ax: plt.Axes
        Matplotlib axis object where the histograms will be for plotted.
    data: List[np.array]
        List of NumPy array storing the data to be plotted.
    labels: List[str]
        List of strings with the labels of the arrays.
    bins:
        Number of bins.
    range: Tuple, optional
        A tuple with a min and max value for the histogram. Default is None,
        which corresponds to using the min a max value across all data.
    title: str, optional
        Title of the axis object.
    xlabel: str, optional
        Label of the horizontal axis.
    ylabel: str, optional
        Label of the vertical axis.

    Returns
    -------
    plt.Axes
        Axis objects for the histogram plot of original labels.
    """
    
    _bins = _get_hist_bins(data=data, bins=bins, range=range)
    legend_handles = []

    for i, data_i in enumerate(data):
        ax.hist(
            data_i,
            label=labels[i],
            bins=_bins,
            density=True,
            histtype='step'
        )

        # Add mean and/or median lines
        if location in ['mean', 'both']:
            mean_val = np.mean(data_i)
            ax.axvline(mean_val, color='k', linestyle='--', linewidth=1)
            if i == 0:
                legend_handles.append(Line2D([0], [0], color='k', linestyle='--', label='Mean'))

        if location in ['median', 'both']:
            median_val = np.median(data_i)
            ax.axvline(median_val, color='r', linestyle='--', linewidth=1)
            if i == 0:
                legend_handles.append(Line2D([0], [0], color='r', linestyle='--', label='Median'))

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Merge histogram and stat lines into legend
    ax.legend(handles=ax.get_legend_handles_labels()[0] + legend_handles)

    return ax

def _get_hist_bins(data: List[np.ndarray], bins: int, range: Tuple = None):
    if isinstance(bins, int):  # Make a range.
        if range is None:
            _min = min([min(x_i) for x_i in data])
            _max = max([max(x_i) for x_i in data])
        else:
            _min = range[0]
            _max = range[1]
        _bins = np.linspace(_min, _max, bins+1)
    else:  # The bins are already provided as a range.
        _bins = bins
    return _bins

def plot_violins(
        ax: plt.Axes,
        data: List[np.ndarray],
        labels: List[str],
        summary_stat: str = 'mean',
        title: str = "Histogram",
        xlabel: str = "x",
        color: str = 'blue',
        x_ticks_rotation: int = 45
      

    ):
    """
    Make a violin plot.

    Parameters
    ----------
    ax: plt.Axes
        Matplotlib axis object where the histograms will be for plotted.
    data: List[np.array]
        List of NumPy array storing the data to be plotted.
    labels: List[str]
        List of strings with the labels of the arrays.
    summary_stat: str, optional
        Select between "median" or "mean" to show in violin plot. Default value is "mean"
    title: str, optional
        Title of the axis object.
    xlabel: str, optional
        Label of the horizontal axis.

    Returns
    -------
    plt.Axes
        Axis objects for the histogram plot of original labels.
    """
    from matplotlib.lines import Line2D

    # Define the list of colors you want to provide
    mycolors = ['purple', 'green', 'blue']  # You can customize this list

    # Plot the violin plots and customize the colors for medians and means
    if summary_stat == 'mean':
        vp = ax.violinplot(data, showmeans=True, showmedians=False)
        vp['cmeans'].set_color(mycolors[0])  # Set the mean color
        mean_line = Line2D([0], [0], color=mycolors[0], linestyle='-', label='Mean')
        ax.legend(handles=[mean_line], loc='upper right')

    elif summary_stat == 'median':
        vp = ax.violinplot(data, showmeans=False, showmedians=True)
        vp['cmedians'].set_color(mycolors[1])  # Set the median color
        median_line = Line2D([0], [0], color=mycolors[1], linestyle='-', label='Median')
        ax.legend(handles=[median_line], loc='upper right')

    elif summary_stat == 'both':
        vp = ax.violinplot(data, showmeans=True, showmedians=True)
        vp['cmeans'].set_color(mycolors[0])    # Set the mean color
        vp['cmedians'].set_color(mycolors[1])  # Set the median color
        mean_line = Line2D([0], [0], color=mycolors[0], linestyle='-', label='Mean')
        median_line = Line2D([0], [0], color=mycolors[1], linestyle='-', label='Median')
        ax.legend(handles=[mean_line, median_line], loc='upper right')

    
    for pc in vp['bodies']:
        pc.set_facecolor(color)
        pc.set_edgecolor('black')  # Set edge color to black for better visibility
        pc.set_alpha(0.7)  # Set transparency level

    ax.set_xticks(ticks=[y + 1 for y in range(len(labels))])
    ax.set_xticklabels(labels=labels, rotation=x_ticks_rotation, ha="center")
    ax.set_ylabel(xlabel)
    ax.set_title(title)
    return ax

def plot_comparison_matrix(
        ax: plt.Axes,
        comparison_out: np.ndarray,
        codes: List[str],
        confidence_level: float = 0.95,
        significance_level: float = 0.05,
        cmap: str = "viridis_r",
        title: str = "New Comparison",
        cbar_label: str = "score",
        textcolors: Union[str, tuple] = ("black", "white")
    ):
    """
    Plot a matrix with all-vs-all comparison scores of M ensembles as a heatmap.
    If plotting the results of a regular all-vs-all analysis (no bootstraping
    involved), it will just plot the M x M comparison scores, with empty values
    on the diagonal. If plotting the results of an all-vs-all analysis with
    bootstrapping it will plot the M x M confidence intervals for the scores.
    The intervals are obtained by using the 'percentile' method. Additionally,
    it will plot an asterisk for those non-diagonal entries in for which the
    inter-ensemble scores are significantly higher than the intra-ensemble
    scores according to a Mann–Whitney U test.

    Parameters
    ----------
    ax: plt.Axes
        Axes object where the heatmap should be created.
    comparison_out: dict
        A dictionary containing the output of the `comparison_scores` method of
        the `dpet.ensemble_analysis.EnsembleAnalysis` class. It must contain the
        following key-value pairs:
        `scores`: NumPy array with shape (M, M, B) containing the comparison
        scores for M ensembles and B bootstrap iterations. If no bootstrap
        analysis was performed, `B = 1`, otherwise it will be `B > 1`.
        `p_values` (optional): used only when a bootstrap analysis was
        performed. A (M, M) NumPy array storiging the p-values obtained
        by comparing with a statistical test the inter-ensemble and
        intra-ensemble comparison scores.
    codes: List[str]
        List of strings with the codes of the ensembles.
    confidence_level: float, optional
        Condifence level for the bootstrap intervals of the comparison scores.
    significance_level: float, optional
        Significance level for the statistical test used to compare inter and
        intra-ensemble comparison scores.
    cmap: str, optional
        Matplotlib colormap name to use in the heatmap.
    title: str, optional
        Title of the heatmap.
    cbar_label: str, optional
        Label of the colorbar.
    textcolors: Union[str, tuple], optional
        Color of the text for each cell of the heatmap, specified as a string.
        By providing a tuple with two elements, the two colors will be applied
        to cells with color intensity above/below a certain threshold, so that
        ligher text can be plotted in darker cells and darker text can be
        plotted in lighter cells.

    Returns
    -------
    ax: plt.Axes
        The same updated Axes object from the input. The `comparison_out` will
        be updated to store confidence intervals if performing a bootstrap
        analysis.
    
    Notes
    -----
    The comparison matrix is annotated with the scores, and the axes are labeled
    with the ensemble labels.

    """
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    
    comparison_out = process_all_vs_all_output(
        comparison_out=comparison_out, confidence_level=confidence_level
    )
    scores_mean = comparison_out['scores_mean']
    im = ax.imshow(scores_mean, cmap=cmap)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)  # size and padding can be adjusted
    cbar = ax.figure.colorbar(im, cax=cax)
    cbar.set_label(cbar_label, fontsize=10)  # adjust font size here
    cbar.ax.tick_params(labelsize=8) 
    ax.set_title(title)
    ax.set_xticks(np.arange(len(codes)))
    ax.set_yticks(np.arange(len(codes)))
    ax.set_xticklabels(codes, rotation=45, ha='right', rotation_mode='anchor')
    ax.set_yticklabels(codes)

    threshold = 0.75
    for i in range(len(codes)):
        for j in range(len(codes)):
            if isinstance(textcolors, str):
                color_ij = textcolors
            else:
                text_idx = int(im.norm(scores_mean[i, j]) > threshold)
                color_ij = textcolors[text_idx]
            kw = {"color": color_ij}
            if comparison_out["mode"] == "single":
                label_ij = f"{scores_mean[i, j]:.2f}"
                if i == j:
                    label_ij = "-"
                size = 10
            elif comparison_out["mode"] == "bootstrap":
                _low_ij = comparison_out['confidence_intervals'][i, j][0]
                _high_ij = comparison_out['confidence_intervals'][i, j][1]
                label_ij = f"[{_low_ij:.3f}, \n {_high_ij:.3f}]"
                if i != j and comparison_out['p_values'][i, j] < significance_level:
                    label_ij += "*"
                size = 8
            else:
                raise NotImplementedError()
            text = im.axes.text(j, i, label_ij, size=size, ha="center", va="center", **kw)

    return ax

def _get_random_a_angle_ids(n: int, prot_len: int) -> np.ndarray:
    rand_ids = np.random.choice(prot_len-3, n, replace=False)
    torsion_ids = _get_a_angle_ids(rand_ids)
    return torsion_ids

def _get_a_angle_ids(ids):
    torsion_ids = []
    for i in ids:
        torsion_ids.append([i, i+1, i+2, i+3])
    return np.array(torsion_ids)

def _get_random_pairs(
        n: int,
        prot_len: int,
        min_sep: int = 1
    ) -> np.ndarray:
    pairs = np.triu_indices(prot_len, k=min_sep)
    pairs = np.vstack(pairs).T
    rand_ids = np.random.choice(pairs.shape[0], n, replace=False)
    return pairs[rand_ids]

def _to_array(x):
    return np.asarray(x)

_phi_psi_offsets = {"phi": 1, "psi": 0}

def _get_max_plots_in_grid(min_len, feature):
    if feature == "ca_dist":
        return min_len*(min_len-1)/2
    elif feature == "a_angle":
        return min_len-3
    elif feature in ("phi", "psi"):
        return min_len-1
    elif feature in ("rama"):
        return min_len-2
    else:
        raise KeyError(feature)


legend_kwargs = {
    # "loc": 'upper right', "bbox_to_anchor": (1.1, 1.1),
    "fontsize": 8
}

class Visualization:
    """
    Visualization class for ensemble analysis.

    Parameters:
        analysis (EnsembleAnalysis): An instance of EnsembleAnalysis providing data for visualization.
    """

    def __init__(self, analysis: EnsembleAnalysis):
        self.analysis = analysis
        self.plot_dir = os.path.join(self.analysis.output_dir, PLOT_DIR)
        os.makedirs(self.plot_dir, exist_ok=True)

    def _index_models(self):
        analysis = self.analysis
        model_indexes = []
        for ensemble in analysis.trajectories:
            for frame in range(analysis.trajectories[ensemble].n_frames):
                model_indexes.append(f'model{frame+1}_{ensemble}')
        return model_indexes

    def _tsne_scatter(
            self,
            color_by: str = "rg",
            kde_by_ensemble: bool = True,
            ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None,
            size: int = 10,
            plotly = False,
            cmap_label: str = 'viridis',
            dpi: int = 96,
            save: bool = False
    ) -> List[plt.Axes]:
        """
        Plot the results of t-SNE analysis. 

        Three scatter plots will be generated based on original, clustering, and feature-colored points. 
        One KDE density plot will also be generated to show the most populated areas in the reduced dimension.   

        Parameters
        ----------
        color_by: str, optional
            The feature extraction method used for coloring points in the scatter plot.
            Options are "rg", "prolateness", "asphericity", "sasa", and "end_to_end". Default is "rg".
        kde_by_ensemble: bool, optional
            If True, the KDE plot will be generated for each ensemble separately. 
            If False, a single KDE plot will be generated for the concatenated ensembles. Default is True.
        save: bool, optional
            If True, the plot will be saved in the data directory. Default is False.
        ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The axes on which to plot. If None, new axes will be created. Default is None.
        size: int, optional 
            The size of the points in the scatter plots. Default is 10.
        plotly: bool, optional 
            If True, the plot will be generated using Plotly. Default is False.
        cmap_label: str, optional 
            The colormap to use for the feature-colored labels. Default is 'viridis'.

        Returns
        -------
        List[plt.Axes]
            List containing Axes objects for the scatter plot of original labels, clustering labels, feature-colored labels, and the KDE density plot, respectively.

        Notes
        ------
        This analysis is only valid for t-SNE dimensionality reduction.
        """

        analysis = self.analysis

        if analysis.reduce_dim_method != "tsne":
            raise ValueError("Analysis is only valid for t-SNE dimensionality reduction.")
        
        if color_by not in ("rg", "prolateness", "asphericity", "sasa", "end_to_end"):
            raise ValueError(f"Method {color_by} not supported.")

        bestclust = analysis.reducer.best_kmeans.labels_
        
        if ax is None:
            custom_axes = False
            fig, ax = plt.subplots(1, 4, figsize=(20, 5), dpi=dpi)
          
        else:
            custom_axes = True
            if not isinstance(ax, (list, np.ndarray)):
                ax = [ax]
            ax = np.array(ax).flatten()
            fig = ax[0].figure
            
        # Create a consistent colormap for the original labels
        unique_labels = np.unique(analysis.all_labels)
        cmap = plt.get_cmap('Set1')
        colors = cmap(np.linspace(0, 1, len(unique_labels)))
        label_colors = {label: color for label, color in zip(unique_labels, colors)}
        point_colors = [label_colors[label] for label in analysis.all_labels]

        # Scatter plot with original labels
        scatter_labeled = ax[0].scatter(analysis.reducer.best_tsne[:, 0], analysis.reducer.best_tsne[:, 1], c=point_colors, s=size, alpha=0.5)
        ax[0].set_title('Scatter Plot (Ensemble labels)', fontsize=15)
        ax[0].set_xlabel('t-SNE 1', fontsize=15)
        ax[0].set_ylabel('t-SNE 2', fontsize=15)
        ax[0].tick_params(axis='both', which='major', labelsize=14)

        # Scatter plot with clustering labels
        cmap = plt.get_cmap('jet', analysis.reducer.bestK)
        scatter_cluster = ax[1].scatter(analysis.reducer.best_tsne[:, 0], analysis.reducer.best_tsne[:, 1], s=size, c=bestclust.astype(float), cmap=cmap, alpha=0.5)
        ax[1].set_title('Scatter Plot (Clustering labels)', fontsize=15)
        ax[1].set_xlabel('t-SNE 1', fontsize=15)
        ax[1].set_ylabel('t-SNE 2', fontsize=15)
        ax[1].tick_params(axis='both', which='major', labelsize=14)

        feature_values = []
        for values in analysis.get_features(color_by).values():
            feature_values.extend(values)
        colors = np.array(feature_values)
        # Scatter plot with different labels
        
        feature_labeled = ax[2].scatter(analysis.reducer.best_tsne[:, 0], analysis.reducer.best_tsne[:, 1], cmap=cmap_label, c=colors, s=size, alpha=0.5)
        cbar = plt.colorbar(feature_labeled, ax=ax[2])
        if color_by in ('rg', 'end_to_end'):
            cbar.set_label(f'{color_by} [nm]', fontsize=15)
        elif color_by in ('prolateness', 'asphericity'):
            cbar.set_label(f'{color_by}', fontsize=15)
        elif color_by == 'sasa':
            cbar.set_label('SASA [nm^2]', fontsize=15)
        ax[2].set_title(f'Scatter Plot ({color_by} labels)', fontsize=15)
        ax[2].set_xlabel('t-SNE 1', fontsize=15)
        ax[2].set_ylabel('t-SNE 2', fontsize=15)
        ax[2].tick_params(axis='both', which='major', labelsize=14)

        if kde_by_ensemble:
            # KDE plot for each ensemble
            for label in unique_labels:
                ensemble_data = analysis.reducer.best_tsne[np.array(analysis.all_labels) == label]
                kde = gaussian_kde([ensemble_data[:, 0], ensemble_data[:, 1]])
                xi, yi = np.mgrid[min(ensemble_data[:, 0]):max(ensemble_data[:, 0]):100j,
                                min(ensemble_data[:, 1]):max(ensemble_data[:, 1]):100j]
                zi = kde(np.vstack([xi.flatten(), yi.flatten()]))
                ax[3].contour(xi, yi, zi.reshape(xi.shape), levels=5, alpha=0.5, colors=[label_colors[label]], linewidths=3)
            ax[3].set_title('Density Plot (Ensemble-wise)', fontsize=15)
            ax[3].set_xlabel('t-SNE 1', fontsize=15)
            ax[3].set_ylabel('t-SNE 2', fontsize=15)
            ax[3].tick_params(axis='both', which='major', labelsize=14)
            # ax[3].legend(title='Ensemble', loc='upper right')
        else:
            # Single KDE plot for concatenated ensembles
            kde = gaussian_kde([analysis.reducer.best_tsne[:, 0], analysis.reducer.best_tsne[:, 1]])
            xi, yi = np.mgrid[min(analysis.reducer.best_tsne[:, 0]):max(analysis.reducer.best_tsne[:, 0]):100j,
                            min(analysis.reducer.best_tsne[:, 1]):max(analysis.reducer.best_tsne[:, 1]):100j]
            zi = kde(np.vstack([xi.flatten(), yi.flatten()]))
            ax[3].contour(xi, yi, zi.reshape(xi.shape), levels=5, cmap='Blues')
            ax[3].set_title('Density Plot', fontsize=15)
            ax[3].set_xlabel('t-SNE 1', fontsize=15)
            ax[3].set_ylabel('t-SNE 2', fontsize=15)
            ax[3].tick_params(axis='both', which='major', labelsize=14)

        # Manage legend for the original labels
        legend_labels = list(label_colors.keys())
        legend_handles = [plt.Line2D([0], [0], marker='o', color=label_colors[label], markersize=10) for label in legend_labels]
        fig.legend(legend_handles, legend_labels, title='Ensemble Labels', loc='upper right', bbox_to_anchor=(1.09, 1.00))

        if not custom_axes:
            fig.tight_layout(pad=1.5)

        if plotly:
            # df = pd.DataFrame({'x':analysis.reducer.best_tsne[:, 0], 'y': analysis.reducer.best_tsne[:, 1], 'index': range(len(analysis.reducer.best_tsne[:, 0]))})
            fig_plotly = px.scatter(x=analysis.reducer.best_tsne[:, 0], 
                            y=analysis.reducer.best_tsne[:, 1],
                            color=colors, hover_data={'index':self._index_models()},
                            labels={'x': 't-SNE 1', 'y': 't-SNE 2'})
            if color_by in ('rg', 'end_to_end'):
                fig_plotly.update_coloraxes(colorbar_title=f'{color_by} [nm]')
            elif color_by in ('prolateness', 'asphericity'):
                fig_plotly.update_coloraxes(colorbar_title=f'{color_by}')
            elif color_by == 'sasa':
                fig_plotly.update_coloraxes(colorbar_title='SASA [nm^2]')
            fig_plotly.show()

        if save:
            fig.savefig(os.path.join(self.plot_dir, f'tsne_scatter_{color_by}.png'), dpi=dpi, bbox_inches='tight')
            msg = f"t-SNE scatter plot saved to {os.path.join(self.plot_dir, f'tsne_scatter_{color_by}.png')}"
            logger.info(msg)

        return ax
    
    def dimensionality_reduction_scatter(self,
                                         color_by: str = "rg", 
                                         save: bool = False, 
                                         ax: Union[None, List[plt.Axes]] = None,
                                         kde_by_ensemble: bool = False,
                                         dpi: int = 96,
                                         size: int = 10,
                                         plotly = False,
                                         cmap_label: str = 'viridis',
                                         n_components: int = 2) -> List[plt.Axes]:
        """
        Plot the results of dimensionality reduction using the method specified in the analysis.

        Parameters
        ----------
        color_by : str, optional
            The feature extraction method used for coloring points in the scatter plot. Options are "rg", "prolateness", "asphericity", "sasa", and "end_to_end". Default is "rg".
        save : bool, optional
            If True, the plot will be saved in the data directory. Default is False.
        ax : Union[None, List[plt.Axes]], optional
            A list of Axes objects to plot on. Default is None, which creates new axes.
        kde_by_ensemble : bool, optional
            If True, the KDE plot will be generated for each ensemble separately. 
            If False, a single KDE plot will be generated for the concatenated ensembles. Default is False.
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        size : int, optional
            The size of the points in the scatter plot. Default is 10.
        plotly : bool, optional
            If True, the plot will be generated using Plotly. Default is False.
        cmap_label : str, optional
            The colormap to use for the feature-colored labels. Default is 'viridis'.
        n_components : int, optional
            The number of components for dimensionality reduction.
            

        Returns
        -------
        List[plt.Axes]
            List containing Axes objects for the scatter plot of original labels, clustering labels, and feature-colored labels, respectively.

        Raises
        ------
        NotImplementedError
            If the dimensionality reduction method specified in the analysis is not supported.

        """

        method = self.analysis.reduce_dim_method
        if method in ("dimenfix", "umap") and n_components <= 2:
            return self._umap_scatter(color_by=color_by, save=save, ax=ax, kde_by_ensemble=kde_by_ensemble, size=size, plotly=plotly, cmap_label=cmap_label)
        elif method == "tsne" and n_components == 2:
            return self._tsne_scatter(color_by=color_by, kde_by_ensemble=kde_by_ensemble, save=save, ax=ax, size=size, cmap_label=cmap_label,dpi=dpi, plotly=plotly)
        elif n_components == 3 :
            self._scatter_3d(color_by=color_by, kde_by_ensemble=kde_by_ensemble, save=save, ax=ax, size=size, plotly=plotly, cmap_label=cmap_label)
        else:
            raise NotImplementedError(f"Scatter plot for method '{method}' is not implemented. Please select between 'tsne', 'dimenfix', and 'umap'.")

    def _umap_scatter(self, 
                         color_by: str = "rg", 
                         save: bool = False,
                         dpi: int = 96, 
                         ax: Union[None, List[plt.Axes]] = None,
                         kde_by_ensemble: bool = False,
                         size: int = 10,
                         plotly = False, 
                         cmap_label: str = 'viridis' 
                         ) -> List[plt.Axes]:
        """
        Plot the complete results for dimenfix and umap methods. 

        Parameters
        -----------
        color_by: str, optional
            The feature extraction method used for coloring points in the scatter plot. Options are "rg", "prolateness", "asphericity", "sasa", and "end_to_end". Default is "rg".

        save: bool, optional
            If True, the plot will be saved in the data directory. Default is False.

        ax : Union[None, List[plt.Axes]], optional
            A list of Axes objects to plot on. Default is None, which creates new axes.
        
        kde_by_ensemble: bool, optional
            If True, the KDE plot will be generated for each ensemble separately. If False, a single KDE plot will be generated for the concatenated ensembles. Default is False.

        Returns
        --------
        List[plt.Axes]
            List containing Axes objects for the scatter plot of original labels, clustering labels, and feature-colored labels, respectively.

        """

        analysis = self.analysis

        if analysis.reduce_dim_method not in ("dimenfix", "umap"):
            raise ValueError("Analysis is only valid for dimenfix dimensionality reduction.")
        
        if color_by not in ("rg", "prolateness", "asphericity", "sasa", "end_to_end"):
            raise ValueError(f"Method {color_by} not supported.")

        if ax is None:
            custom_axes = False
            fig, ax = plt.subplots(1, 4, figsize=(18, 4), dpi=dpi)
            axes = ax.flatten()  # Ensure axes is a 1D array
        else:
            custom_axes = True
            ax_array = np.array(ax).flatten()
            axes = ax_array  # If ax is provided, flatten it to 1D
            fig = axes[0].figure

        # Create a consistent colormap for the original labels
        unique_labels = np.unique(analysis.all_labels)
        cmap = plt.get_cmap('Set1')
        colors = cmap(np.linspace(0, 1, len(unique_labels)))
        label_colors = {label: color for label, color in zip(unique_labels, colors)}
        point_colors = [label_colors[label] for label in analysis.all_labels]

        # Scatter plot with original labels
        
        scatter_labeled = axes[0].scatter(analysis.transformed_data[:, 0], analysis.transformed_data[:, 1], c=point_colors, s=size, alpha=0.5)
        axes[0].set_title('Scatter Plot (Ensemble labels)', fontsize=15)
        axes[0].set_xlabel('UMAP 1', fontsize=15)
        axes[0].set_ylabel('UMAP 2', fontsize=15)
        axes[0].tick_params(axis='both', which='major', labelsize=14)


        # Scatter plot with different labels
        feature_values = []
        for values in analysis.get_features(color_by).values():
            feature_values.extend(values)
        colors = np.array(feature_values)

        
        rg_labeled = axes[2].scatter(analysis.transformed_data[:, 0], analysis.transformed_data[:, 1], c=colors, s=size, alpha=0.5, cmap=cmap_label)
        cbar = plt.colorbar(rg_labeled, ax=axes[2])
        axes[2].set_title(f'Scatter Plot ({color_by} labels)', fontsize=15)
        if color_by in ('rg', 'end_to_end'):
            cbar.set_label(f'{color_by} [nm]', fontsize=15)
        elif color_by in ('prolateness', 'asphericity'):
            cbar.set_label(f'{color_by}', fontsize=15)
        elif color_by == 'sasa':
            cbar.set_label('SASA [nm^2]', fontsize=15)
        axes[2].set_xlabel('UMAP 1', fontsize=15)
        axes[2].set_ylabel('UMAP 2', fontsize=15)
        axes[2].tick_params(axis='both', which='major', labelsize=14)

        

        # Scatter plot with clustering labels
        best_k = max(analysis.reducer.sil_scores, key=lambda x: x[2])[1]
        print('best_k is ', best_k)
        kmeans = KMeans(n_clusters=best_k,n_init=10 ,random_state=42)
        labels = kmeans.fit_predict(analysis.transformed_data)
        scatter_cluster = axes[1].scatter(analysis.transformed_data[:, 0], analysis.transformed_data[:, 1], s=size, c=labels, cmap='viridis')
        axes[1].set_title('Scatter Plot (clustering labels)', fontsize=15)
        axes[1].set_xlabel('UMAP 1', fontsize=15)
        axes[1].set_ylabel('UMAP 2', fontsize=15)
        axes[1].tick_params(axis='both', which='major', labelsize=14)

        # Manage legend for original labels
        legend_labels = list(label_colors.keys())
        legend_handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=label_colors[label], markersize=10) for label in legend_labels]
        

        if kde_by_ensemble:
            # KDE plot for each ensemble
            for label in unique_labels:
                ensemble_data = analysis.transformed_data[np.array(analysis.all_labels) == label]
                kde = gaussian_kde([ensemble_data[:, 0], ensemble_data[:, 1]])
                xi, yi = np.mgrid[min(ensemble_data[:, 0]):max(ensemble_data[:, 0]):100j,
                                min(ensemble_data[:, 1]):max(ensemble_data[:, 1]):100j]
                zi = kde(np.vstack([xi.flatten(), yi.flatten()]))
                ax[3].contour(xi, yi, zi.reshape(xi.shape), levels=5, alpha=0.5, colors=[label_colors[label]])
            ax[3].set_title('Density Plot (Ensemble-wise)', fontsize=15)
            # ax[3].legend(title='Ensemble', loc='upper right')
        else:
            # Single KDE plot for concatenated ensembles
            kde = gaussian_kde([analysis.transformed_data[:, 0], analysis.transformed_data[:, 1]])
            xi, yi = np.mgrid[min(analysis.transformed_data[:, 0]):max(analysis.transformed_data[:, 0]):100j,
                            min(analysis.transformed_data[:, 1]):max(analysis.transformed_data[:, 1]):100j]
            zi = kde(np.vstack([xi.flatten(), yi.flatten()]))
            ax[3].contour(xi, yi, zi.reshape(xi.shape), levels=5, cmap='Blues')
            ax[3].set_title('Density Plot', fontsize=15)
        ax[3].set_xlabel('UMAP 1', fontsize=15)
        ax[3].set_ylabel('UMAP 2', fontsize=15)
        ax[3].tick_params(axis='both', which='major', labelsize=14)
        fig.legend(legend_handles, legend_labels, title='Ensemble Labels', loc='upper right', bbox_to_anchor=(1.09, 1.0))
        if not custom_axes:
            fig.tight_layout()
        if save:
            fig.savefig(self.plot_dir + f'/{analysis.reduce_dim_method}_scatter.png', dpi=dpi, bbox_inches='tight')
            msg = f"UMAP scatter plot saved to {self.plot_dir + f'/{analysis.reduce_dim_method}_scatter.png'}"
            logger.info(msg)
        
        if plotly:
            # df = pd.DataFrame({'x':analysis.reducer.best_tsne[:, 0], 'y': analysis.reducer.best_tsne[:, 1], 'index': range(len(analysis.reducer.best_tsne[:, 0]))})
            fig_plotly = px.scatter(x=analysis.transformed_data[:, 0],
                            y=analysis.transformed_data[:, 1],
                            color=colors,
                            hover_data={'index':self._index_models()},
                            labels={'x': 'UMAP 1', 'y': 'UMAP 2'})
            if color_by in ('rg', 'end_to_end'):
                fig_plotly.update_coloraxes(colorbar_title=f'{color_by} [nm]')
            elif color_by in ('prolateness', 'asphericity'):
                fig_plotly.update_coloraxes(colorbar_title=f'{color_by}')
            elif color_by == 'sasa':
                fig_plotly.update_coloraxes(colorbar_title='SASA [nm^2]')
            fig_plotly.show()

        return axes
    
    def _scatter_3d(self, 
                    color_by: str = "rg", 
                    save: bool = False, 
                    ax: Union[None, List[plt.Axes]] = None,
                    size: int = 10,
                    kde_by_ensemble: bool = False,
                    plotly=False,
                    cmap_label: str = 'viridis', 
                    dpi: int = 96
                    ) -> List[plt.Axes]:
        if color_by in ('rg', 'end_to_end'):
            colorbar_title = f'{color_by} [nm]'
        elif color_by in ('prolateness', 'asphericity'):
            colorbar_title = f'{color_by}'
        elif color_by == 'sasa':
            colorbar_title = 'SASA [nm^2]'

        import plotly.graph_objects as go
        from mpl_toolkits.mplot3d import Axes3D
        analysis = self.analysis

        if analysis.reduce_dim_method not in ("dimenfix", "umap"):
            ax_label = 't-SNE'
            bestclust = analysis.reducer.best_kmeans.labels_
            cmap = plt.get_cmap('Set1', analysis.reducer.bestK)
            labels_clust = bestclust.astype(float)

        else:
            ax_label = 'UMAP'
            best_k = max(analysis.reducer.sil_scores, key=lambda x: x[2])[1]
            kmeans = KMeans(n_clusters=best_k, random_state=42)
            labels_clust = kmeans.fit_predict(analysis.transformed_data)
            
            
            
        
        if color_by not in ("rg", "prolateness", "asphericity", "sasa", "end_to_end"):
            raise ValueError(f"Method {color_by} not supported.")

        if ax is None:
            fig = plt.figure( figsize=(18, 6), dpi=dpi)
            
            # axes = ax.flatten()  # Ensure axes is a 1D array
        else:
            ax_array = np.array(ax).flatten()
            axes = ax_array  # If ax is provided, flatten it to 1D
            fig = axes[0].figure

        # Create a consistent colormap for the original labels
        unique_labels = np.unique(analysis.all_labels)
        cmap = plt.get_cmap('plasma')
        colors = cmap(np.linspace(0, 1, len(unique_labels)))
        label_colors = {label: color for label, color in zip(unique_labels, colors)}
        point_colors = [label_colors[label] for label in analysis.all_labels]

        # Scatter plot with original labels
        ax1 = fig.add_subplot(131, projection='3d')
        scatter_labeled = ax1.scatter(analysis.transformed_data[:, 0], analysis.transformed_data[:, 1], analysis.transformed_data[:, 2],c=point_colors, s=size, alpha=0.5)
        ax1.set_title('Scatter plot (original labels)')
        ax1.view_init(elev=30, azim=135)
        ax1.set_xlabel(f'{ax_label} 1')
        ax1.set_ylabel(f'{ax_label} 2')
        ax1.set_zlabel(f'{ax_label} 3')

        # Scatter plot with different labels
        feature_values = []
        for values in analysis.get_features(color_by).values():
            feature_values.extend(values)
        colors = np.array(feature_values)


        ax2 = fig.add_subplot(133, projection='3d')
        rg_labeled = ax2.scatter(analysis.transformed_data[:, 0], analysis.transformed_data[:, 1],analysis.transformed_data[:, 2] ,c=colors, s=size, alpha=0.5, cmap=cmap_label)
        cbar = plt.colorbar(rg_labeled, ax=ax2, fraction=0.075, shrink=0.6)
        cbar.set_label(f'{colorbar_title}', fontsize=15)
        ax2.set_title(f'Scatter plot ({color_by} labels)')
        ax2.view_init(elev=30, azim=45)
        ax2.set_xlabel(f'{ax_label} 1')
        ax2.set_ylabel(f'{ax_label} 2')
        ax2.set_zlabel(f'{ax_label} 3')

        # Scatter plot with clustering labels
        ax3 = fig.add_subplot(132, projection='3d')
        n_clusters = len(np.unique(labels_clust))
        cluster_cmap = plt.get_cmap('Set1', n_clusters)
        colors_discrete = cluster_cmap(labels_clust.astype(int))

        scatter_cluster = ax3.scatter(
            analysis.transformed_data[:, 0],
            analysis.transformed_data[:, 1],
            analysis.transformed_data[:, 2],
            s=size,
            c=colors_discrete,
            alpha=0.5
        )

        ax3.set_title('Scatter plot (clustering labels)')
        ax3.view_init(elev=30, azim=135)
        ax3.set_xlabel(f'{ax_label} 1')
        ax3.set_ylabel(f'{ax_label} 2')
        ax3.set_zlabel(f'{ax_label} 3')

        # Manage legend for original labels
        legend_labels = list(label_colors.keys())
        legend_handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=label_colors[label], markersize=10) for label in legend_labels]
        fig.legend(legend_handles, legend_labels, title='Original Labels', loc='upper right')

        if plotly:
            # df = pd.DataFrame({'x':analysis.reducer.best_tsne[:, 0], 'y': analysis.reducer.best_tsne[:, 1], 'index': range(len(analysis.reducer.best_tsne[:, 0]))})
            # fig = px.scatter(x=analysis.transformed_data[:, 0], y=analysis.transformed_data[:, 1], color=colors, hover_data={'index':self._index_models()} )
            import plotly.colors as pc
            from plotly.subplots import make_subplots
            import plotly.graph_objects as go
            n_clusters = len(np.unique(labels_clust))
            color_list = pc.qualitative.Set1  # or Set2, Dark2, Pastel, etc.

            # Extend color list if not enough colors
            if n_clusters > len(color_list):
                color_list = (color_list * ((n_clusters // len(color_list)) + 1))[:n_clusters]

            # Map cluster ID to color
            label_color_map = {i: color_list[i] for i in range(n_clusters)}
            labels_colors_discrete = [label_color_map[i] for i in labels_clust]
         

            fig_plotly = make_subplots(
                rows=1, cols=3,
                specs=[[{'type': 'scene'}, {'type': 'scene'} , {'type': 'scene'}]],
                subplot_titles=('Ensemble Labels', 'Clustering Labels' , f'{color_by} Labels')
            )
            fig_plotly.update_layout(
                scene=dict(domain=dict(x=[0.0, 0.32])),
                scene2=dict(domain=dict(x=[0.34, 0.66])),
                scene3=dict(domain=dict(x=[0.68, 1.0]))
)
            # Plot 1: Ensemble Labels
            fig_plotly.add_trace(
                go.Scatter3d(
                    x=analysis.transformed_data[:, 0],
                    y=analysis.transformed_data[:, 1],
                    z=analysis.transformed_data[:, 2],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=point_colors,
                        opacity=0.5,
                                             
                    ),
                    hovertext=self._index_models(),
                   
                ),
                row=1, col=1
            )

            # Plot 2: Clustering Labels
            fig_plotly.add_trace(
                go.Scatter3d(
                    x=analysis.transformed_data[:, 0],
                    y=analysis.transformed_data[:, 1],
                    z=analysis.transformed_data[:, 2],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=labels_colors_discrete,
                        opacity=0.5,
                
                    ),
                    hovertext=self._index_models(),
                   
                ),
                row=1, col=2
            )

            # Plot 3: Feature Colored Labels
            fig_plotly.add_trace(
                go.Scatter3d(
                    x=analysis.transformed_data[:, 0],
                    y=analysis.transformed_data[:, 1],
                    z=analysis.transformed_data[:, 2],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=colors,
                        colorscale=cmap_label,
                        opacity=0.5,
                        colorbar=dict(
                            title=f'{colorbar_title}',
                            x=1.0,
                            len=0.8,
                            y=0.5)
                    ),
                    hovertext=self._index_models(),
                    
                ),
                row=1, col=3
            ),

            # Axis labels for both 3D plots
            fig_plotly.update_layout(
                scene=dict(
                    xaxis_title=f'{ax_label} 1',
                    yaxis_title=f'{ax_label} 2',
                    zaxis_title=f'{ax_label} 3'
                ),
                scene2=dict(
                    xaxis_title=f'{ax_label} 1',
                    yaxis_title=f'{ax_label} 2',
                    zaxis_title=f'{ax_label} 3'
                ),
                scene3=dict(
                    xaxis_title=f'{ax_label} 1',
                    yaxis_title=f'{ax_label} 2',
                    zaxis_title=f'{ax_label} 3'
                ),
                
                margin=dict(l=0, r=0, t=50, b=0),
                showlegend=False
            )

            fig_plotly.show()


        plt.subplots_adjust(wspace=0.5, hspace=0.2)  # Adjust spacing manually
        fig.show()
        if save:
            fig.savefig(os.path.join(self.plot_dir, 'tSNE_landscape'), dpi=dpi, bbox_inches='tight')
            msg = f"3D scatter plot saved to {os.path.join(self.plot_dir, 'tSNE_landscape.png')}"
            logger.info(msg)

        return [ax1, ax2, ax3]


    def pca_cumulative_explained_variance(
            self,
            save: bool = False,
            dpi: int = 96 ,
            ax: Union[None, plt.Axes] = None
        ) -> plt.Axes:
        """
        Plot the cumulative variance. Only applicable when the
        dimensionality reduction method is "pca".

        Parameters
        ----------
        save: bool, optional
            If True, the plot will be saved in the data directory. Default is False.
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        ax: Union[None, plt.Axes], optional
            An Axes object to plot on. Default is None, which creates a new axes.

        Returns
        -------
        plt.Axes, cumvar
            The Axes object for the cumulative explained variance plot and a
            numpy array with the cumulative variance.
        """ 
        
        analysis = self.analysis

        if analysis.reduce_dim_method != "pca":
            raise ValueError("Analysis is only valid for pca dimensionality reduction.")
        
        if ax is None:
            fig, ax = plt.subplots(dpi=dpi)
        else:
            fig = ax.figure

        pc_vars = analysis.reduce_dim_model.explained_variance_ratio_
        cumvar = np.cumsum(pc_vars) * 100
        ax.plot(cumvar)
        ax.set_xlabel("PCA dimension")
        ax.set_ylabel("Cumulative explained variance %")
        ax.set_title("Cumulative Explained Variance by PCA Dimension")
        ax.grid(True)
        first_three_variance = pc_vars[0:3].sum()*100
        ax.text(0.5, 0.9, f"First three: {first_three_variance:.2f}%", transform=ax.transAxes, ha='center')

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'PCA_variance' + analysis.featurization + analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"PCA cumulative explained variance plot saved to {os.path.join(self.plot_dir, 'PCA_variance' + analysis.featurization + analysis.ens_codes[0] + '.png')}"
            logger.info(msg)
        return ax, cumvar

    def _set_labels(self, ax, reduce_dim_method, dim_x, dim_y):
        ax.set_xlabel(f"{reduce_dim_method} dim {dim_x+1}")
        ax.set_ylabel(f"{reduce_dim_method} dim {dim_y+1}")

    def _check_dimred_method(self, method, allowed=None):
        if method is None:
            raise ValueError("No dimensionality reduction was performed")
        if allowed is not None:
            if not method in allowed:
                raise ValueError(
                    f"Analysis is only valid for the following dimensionality reduction methods: {allowed}."
                )

    def pca_2d_landscapes(self,
            save: bool = False,
            sel_components: List[int] = [0, 1],
            ax: Union[None, List[plt.Axes]] = None,
            dpi: int = 96
        ) -> List[plt.Axes]:
        """
        Plot 2D landscapes when the dimensionality reduction method is "pca" or "kpca".

        Parameters
        ----------
        save: bool, optional
            If True the plot will be saved in the data directory. Default is False.
        sel_components: List[int], optional
            Indices of the selected principal components to analyze, starting from 0.
            The default components are the first and second.
        ax: Union[None, List[plt.Axes]], optional
            A list of Axes objects to plot on. Default is None, which creates new axes.
        dpi : int, optional
            For changing the quality and dimension of the output figure. Default is 96.

        Returns
        -------
        List[plt.Axes]
            A list of plt.Axes objects representing the subplots created.
        """
        
        analysis = self.analysis
        method_name = analysis.reduce_dim_method
        self._check_dimred_method(method_name, allowed=("pca", "kpca"))

        # 2D scatter plot settings
        dim_x = sel_components[0]
        dim_y = sel_components[1]
        marker = "."

        num_ensembles = len(analysis.ens_codes)
        
        if ax is None:
            custom_axes = False
            fig, axes = plt.subplots(
                num_ensembles + 1, figsize=(4, 4 * (num_ensembles + 1)), dpi=dpi
            )
        else:
            custom_axes = True
            if not isinstance(ax, (list, np.ndarray)):
                ax = [ax]
            axes = np.array(ax).flatten()
            fig = axes[0].figure

        # Plot all ensembles at the same time
        axes[0].set_title("all")
        for ensemble in analysis.ensembles:
            axes[0].scatter(ensemble.reduce_dim_data[:, dim_x],
                            ensemble.reduce_dim_data[:, dim_y],
                            label=ensemble.code, marker=marker)
        axes[0].legend(**legend_kwargs)
        self._set_labels(axes[0], method_name, dim_x, dim_y)

        # Concatenate all reduced dimensionality data from the dictionary
        all_data = analysis.transformed_data

        # Plot each ensemble individually
        for i, ensemble in enumerate(analysis.ensembles):
            axes[i + 1].set_title(ensemble.code)
            # Plot all data in gray
            axes[i + 1].scatter(all_data[:, dim_x],
                                all_data[:, dim_y],
                                label="all", color="gray", alpha=0.25,
                                marker=marker)
            # Plot ensemble data in color
            axes[i + 1].scatter(ensemble.reduce_dim_data[:, dim_x],
                                ensemble.reduce_dim_data[:, dim_y],
                                label=ensemble.code, c=f"C{i}",
                                marker=marker)
            axes[i + 1].legend(**legend_kwargs)
            self._set_labels(axes[i + 1], method_name, dim_x, dim_y)

        if not custom_axes:
            fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, f'{method_name.upper()}_2d_landscapes_' + analysis.featurization + 
                        analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"{method_name.upper()} 2D landscapes saved to {os.path.join(self.plot_dir, f'{method_name.upper()}_2d_landscapes_' + analysis.featurization + analysis.ens_codes[0] + '.png')}"
            logger.info(msg)

        return axes

    def pca_1d_histograms(self,
            save: bool = False,
            sel_components: int = 0,
            bins: int = 30,
            ax: Union[None, List[plt.Axes]] = None,
            dpi: int = 96
        ) -> List[plt.Axes]:
        """
        Plot 1D histogram when the dimensionality reduction method is "pca" or "kpca".

        Parameters
        ----------
        save: bool, optional
            If True the plot will be saved in the data directory. Default is False.

        dim: int, optional
            To select the specific component (dimension) for which you want to visualize the histogram distribution.
            Default is 0 (first principal component in PCA). 

        n_bins: int, optional
            Number of bins in the histograms.

        ax: Union[None, List[plt.Axes]], optional
            A list of Axes objects to plot on. Default is None, which creates new axes.
        
        dpi : int, optional
            For changing the quality and dimension of the output figure. Default is 96.

        Returns
        -------
        List[plt.Axes]
            A list of plt.Axes objects representing the subplots created.
        """

        analysis = self.analysis
        method_name = analysis.reduce_dim_method
        self._check_dimred_method(method_name, allowed=("pca", "kpca"))

        k = sel_components
        bins = np.linspace(analysis.transformed_data[:, k].min(),
                           analysis.transformed_data[:, k].max(),
                           bins)

        if ax is None:
            fig, axes = plt.subplots(
                len(analysis.ens_codes), 1, figsize=(4, 2 * len(analysis.ens_codes)), dpi=dpi
            )
            if len(analysis.ens_codes) == 1:
                axes = [axes]

        else:
            if not isinstance(ax, (list, np.ndarray)):
                ax = [ax]
            axes = np.array(ax).flatten()
            fig = axes[0].figure

        # Plot histograms for each ensemble
        for i, ensemble in enumerate(analysis.ensembles):
            axes[i].hist(ensemble.reduce_dim_data[:, k],
                        label=ensemble.code,
                        bins=bins,
                        density=True,
                        color=f"C{i}",
                        histtype="step")
            axes[i].hist(analysis.transformed_data[:, k],
                        label="all",
                        bins=bins,
                        density=True,
                        color="gray",
                        alpha=0.25,
                        histtype="step")
            axes[i].legend(**legend_kwargs)
            axes[i].set_xlabel(f"{method_name} dim {k+1}")
            axes[i].set_ylabel("Density")

        if ax is None:
            fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, f'{method_name.upper()}_hist' + 
                        analysis.featurization + analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"{method_name.upper()} 1D histograms saved to {os.path.join(self.plot_dir, f'{method_name.upper()}_hist' + analysis.featurization + analysis.ens_codes[0] + '.png')}"
            logger.info(msg)

        return axes

    def pca_residue_correlation(self,
            sel_components: List[int] = [0, 1, 2],
            save: bool = False,
            ax: Union[None, List[plt.Axes]] = None,
            dpi: int = 96,
            cmap: str = "RdBu",
            cmap_range: Union[None, Tuple[float]] = None,
            scale_loadings: bool = False
        ) -> List[plt.Axes]:
        """
        Plot the loadings (weights) of each pair of residues for a list of
        principal components (PCs).

        Parameters
        ----------
        sel_components : List[int], optional
            A list of indices specifying the PC to include in the plot.
        save : bool, optional
            If True, the plot will be saved as an image file. Default is False.
        ax : Union[None, List[plt.Axes]], optional
            A list of Axes objects to plot on. Default is None, which creates new axes.
        dpi : int, optional
            For changing the quality and dimension of the output figure. Default is 96.
        cmap: str, optional
            Matplotlib colormap name.
        cmap_range: Union[None, Tuple[float]], optional
            Range of the colormap. Defaults to 'None', the range will be
            identified automatically. If a tuple, the first and second elements
            are the min. and max. of the range.
        scale_loadings: bool, optional
            Scale loadings by explained variance. Some definitions use correlation
            coefficients as loadings, when input features are standardized.

        Returns
        -------
        List[plt.Axes]
            A list of plt.Axes objects representing the subplots created.

        Notes
        -----
        This method generates a correlation plot showing the weights of pairwise residue distances
        for selected PCA dimensions. The plot visualizes the correlation between residues based on
        the PCA weights.

        The analysis is only valid on PCA and kernel PCA dimensionality reduction with 'ca_dist' feature extraction.
        """

        analysis = self.analysis

        if analysis.reduce_dim_method != "pca" or analysis.featurization != "ca_dist":
            raise ValueError("Analysis is only valid for pca dimensionality reduction with ca_dist feature extraction.")
        
        cmap = plt.get_cmap(cmap)

        fig_r = 0.8
        if ax is None:
            fig, axes = plt.subplots(1, len(sel_components), dpi=dpi, figsize=(15*fig_r, 4*fig_r))
        else:
            if not isinstance(ax, (list, np.ndarray)):
                ax = [ax]
            axes = np.array(ax).flatten()
            fig = axes[0].figure

        # Get the number of residues from one of the trajectories
        num_residues = next(iter(analysis.trajectories.values())).topology.n_residues
        pca_model = analysis.reduce_dim_model
        for k, sel_component in enumerate(sel_components):
            matrix = np.zeros((num_residues, num_residues))
            vals = []
            if scale_loadings:
                loadings = pca_model.components_.T * np.sqrt(pca_model.explained_variance_)
                loadings = loadings.T
            else:
                loadings = pca_model.components_
            for i in range(loadings.shape[1]):
                r1, r2 = analysis.feature_names[i].split("-")
                # Note: this should be patched for proteins with resSeq values not starting from 1!
                v_ij = loadings[sel_component,i]
                matrix[int(r1[3:])-1, int(r2[3:])-1] = v_ij
                matrix[int(r2[3:])-1, int(r1[3:])-1] = v_ij
                vals.append(v_ij)
            if cmap_range is None:
                # Automatically find the range.
                _cmap_range = (-np.abs(vals).max(), np.abs(vals).max())
            else:
                _cmap_range = cmap_range
            norm = colors.Normalize(_cmap_range[0], _cmap_range[1])
            im = axes[k].imshow(matrix, cmap=cmap, norm=norm)  # RdBu, PiYG
            axes[k].set_xlabel("Residue j")
            axes[k].set_ylabel("Residue i")
            axes[k].set_title(r"Loading of $d_{ij}$" + f" for PCA dim {sel_component+1}")
            cbar = fig.colorbar(
                im, ax=axes[k],
                label="PCA loading"
            )
        if ax is None:
            fig.tight_layout()
        if save:
            fig.savefig(os.path.join(self.plot_dir, 'PCA_correlation' + analysis.featurization + analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"PCA residue correlation plot saved to {os.path.join(self.plot_dir, 'PCA_correlation' + analysis.featurization + analysis.ens_codes[0] + '.png')}"
            logger.info(msg)

        return axes

    def pca_rg_correlation(self,
            save: bool = False,
            ax: Union[None, List[plt.Axes]] = None,
            dpi: int = 96,
            sel_components: int = 0,
        ) -> List[plt.Axes]:
        """
        Examine and plot the correlation between PC dimension 1 and the amount of Rg.
        Typically high correlation can be detected in case of IDPs/IDRs .

        Parameters
        ----------
        save : bool, optional
            If True, the plot will be saved in the data directory. Default is False.

        ax: Union[None, List[plt.Axes]], optional
            A list of Axes objects to plot on. Default is None, which creates new axes.
        
        dpi : int, optional
            For changing the quality and dimension of the output figure. Default is 96.

        sel_components: int, optional
            Index of the selected principal component to analyze, defaults to 0 (first
            principal component).

        Returns
        -------
        List[plt.Axes], dict
            A list of plt.Axes objects representing the subplots created and a
            dictionary with all the raw data being plotted.
        """

        analysis = self.analysis

        if analysis.reduce_dim_method not in ("pca", "kpca"):
            raise ValueError("Analysis is only valid for pca and kpca dimensionality reduction.")

        if ax is None:
            fig, axes = plt.subplots(len(analysis.ens_codes), 1, figsize=(3, 3 * len(analysis.ens_codes)), dpi=dpi)
            if len(analysis.ens_codes) == 1:
                axes = [axes]
        else:
            if not isinstance(ax, (list, np.ndarray)):
                ax = [ax]
            axes = np.array(ax).flatten()
            fig = axes[0].figure

        # Plot the correlation for each ensemble
        data = {}
        for i, ensemble in enumerate(analysis.ensembles):
            rg_i = mdtraj.compute_rg(ensemble.trajectory)
            axes[i].scatter(ensemble.reduce_dim_data[:, sel_components],
                            rg_i, label=ensemble.code,
                            color=f"C{i}")
            axes[i].legend(fontsize=8)
            axes[i].set_xlabel(f"Dim {sel_components + 1}")
            axes[i].set_ylabel(r"$R_g$ [nm]")
            data[ensemble.code] = {
                "pc": ensemble.reduce_dim_data[:, sel_components],
                "rg": rg_i
            }

        if ax is None:
            fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'PCA_RG' + analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"PCA Rg correlation plot saved to {os.path.join(self.plot_dir, 'PCA_RG' + analysis.ens_codes[0] + '.png')}"
            logger.info(msg)

        return axes, data
    
    def global_sasa(self, 
                bins: int = 50, 
                hist_range: Tuple = None, 
                violin_plot: bool = True, 
                summary_stat: str = 'mean',
                save: bool = False, 
                dpi = 96,
                color: str = 'lightblue',
                multiple_hist_ax: bool = False,
                x_ticks_rotation: int = 45,
                ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None) -> plt.Axes:
        """
        Plot the distribution of SASA for each conformation within the ensembles.

        Parameters
        ----------
        bins : int, optional
            The number of bins for the histogram. Default is 50.
        hist_range: Tuple, optional
            A tuple with a min and max value for the histogram. Default is None,
            which corresponds to using the min a max value across all data.
        violin_plot : bool, optional
            If True, a violin plot is visualized. Default is True.
        summary_stat: str, optional
            Specifies whether to display the "mean", "median", or "both" as reference lines on the plots.
            This applies when violin_plot is True or when multiple_hist_ax is True for histograms.
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        color : str, optional
            Color of the violin plot. Default is lightblue.
        multiple_hist_ax : bool, optional
            If True, it will plot each histogram in a different axis.
        x_ticks_rotation : int, optional
            The rotation angle of the x-axis tick labels for the violin plot. Default is 45.
        ax : Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The matplotlib Axes object on which to plot. If None, a new Axes object will be created. Default is None.

        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        if self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")

        ensembles = self.analysis.ensembles

        # Calculate features.
        hist_data = []
        labels = []

        for ensemble in ensembles:
            sasa_i = mdtraj.shrake_rupley(ensemble.trajectory)
            total_sasa_i = sasa_i.sum(axis=1)
            hist_data.append(total_sasa_i)
            labels.append(ensemble.code)

        # Plot setup depending on plot type and multiple_hist_ax setting
        custom_axes = ax is not None

        if not violin_plot and multiple_hist_ax:
            # Create one axis for each histogram
            if ax is None:
                fig, ax = plt.subplots(
                    1, len(ensembles), 
                    figsize=(3 * len(ensembles), 3),
                    dpi=96
                )
            else:
                if not isinstance(ax, (list, np.ndarray)):
                    ax = [ax]
                ax = np.array(ax).flatten()
                fig = ax[0].figure
        else:
            # Single axis for all histograms or violin plot
            if ax is None:
                fig, ax = plt.subplots(dpi=dpi)
            else:
                fig = ax.figure

        axis_label = r"SASA (nm$^2$)"
        title = ""

        if violin_plot:
            # Plot the violin plot
            plot_violins(
                ax=ax,
                data=hist_data,
                labels=labels,
                summary_stat=summary_stat,
                title=title,
                xlabel=axis_label,
                color=color,
                x_ticks_rotation=x_ticks_rotation
            )
        else:
            if not multiple_hist_ax:
                # Single histogram plot
                plot_histogram(
                    ax=ax,
                    data=hist_data,
                    labels=labels,
                    bins=bins,
                    range=hist_range,
                    title=title,
                    xlabel=axis_label
                )
            else:
                # Plot separate histograms for each ensemble on separate axes
                _bins = _get_hist_bins(
                    data=hist_data, bins=bins, range=hist_range
                )
                h_args = {"histtype": "step", "density": True}
                y_max = 0
                for hist_data_i in hist_data:
                    counts, _ = np.histogram(hist_data_i, bins=_bins, density=True)
                    y_max = max(y_max, counts.max())
                    
                for i, (name_i, hist_data_i) in enumerate(zip(labels, hist_data)):
                    ax[i].hist(hist_data_i, bins=_bins, label=name_i, **h_args)
                    ax[i].set_ylim(0, y_max * 1.1)  # Add a little margin
                    ax[i].set_title(name_i)
                    if i == 0:
                        ax[i].set_ylabel("Density")
                    ax[i].set_xlabel(axis_label)

                    # Adding mean/median/both lines with legend
                    legend_handles = []
                    if summary_stat == 'mean':
                        mean_sasa = np.mean(hist_data_i)
                        mean_line = ax[i].axvline(mean_sasa, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                    if summary_stat == 'median':
                        median_sasa = np.median(hist_data_i)
                        median_line = ax[i].axvline(median_sasa, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)
                    if summary_stat == 'both':
                        mean_sasa = np.mean(hist_data_i)
                        mean_line = ax[i].axvline(mean_sasa, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                        median_sasa = np.median(hist_data_i)
                        median_line = ax[i].axvline(median_sasa, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)

                    # Add legend if needed
                    if legend_handles:
                        ax[i].legend(handles=legend_handles, loc='upper right')
                if not custom_axes:
                    fig.tight_layout()

        if save:            
            fig.savefig(os.path.join(self.plot_dir, 'Global_SASA_dist_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg= f"Global SASA distribution plot saved to {self.plot_dir}/Global_SASA_dist_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def rg_vs_asphericity(self,
                           dpi: int = 96,
                           save: bool = False,
                           size: int = 4,
                           ax: plt.Axes = None,
                           verbose: bool = True) -> plt.Axes:
        """
        Plots the Rg versus Asphericity and calculates the pearson correlation coefficient to evaluate 
        the correlation between Rg and Asphericity.

        Parameters
        ----------
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        size: int, optional
            The size of the scatter points. Default is 4.
        ax: plt.Axes, optional
            The axes on which to plot. Default is None, which creates a new figure and axes.
        verbose: bool, optional
            Verbosity for the output of the method. Showin the Pearson correlation coefficient for each ensemble.

        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        analysis = self.analysis
        
        if ax is None:
            fig, ax = plt.subplots(dpi=dpi)  # Create a new figure if ax is not provided
        else:
            fig = ax.figure  # Use the figure associated with the provided ax
        
        for ensemble in analysis.ensembles:
            x = mdtraj.compute_rg(ensemble.trajectory)
            y = compute_asphericity(ensemble.trajectory)
            p = np.corrcoef(x, y)
            ax.scatter(x, y, s=size, label=ensemble.code)
            msg = f"Pearson coeff for {ensemble.code} = {round(p[0][1], 3)}"
            if verbose:
                print(msg)
            else:
                logger.info(msg)
        
        ax.set_ylabel("Asphericity")
        ax.set_xlabel( r"Radius of Gyration ($R_g$) [nm]")
        ax.set_title("Rg vs. Asphericity")
        ax.legend()
        
        if save:
            fig.savefig(os.path.join(self.plot_dir, 'Rg_vs_Asphericity_' + analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Rg vs. Asphericity plot saved to {self.plot_dir}/Rg_vs_Asphericity_{analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax
  
    def rg_vs_prolateness(self, 
                          dpi: int = 96,
                          size: int = 4,
                          save: bool = False,
                          ax: plt.Axes = None, 
                          verbose: bool = True) -> plt.Axes:
        """
        Plot the Rg versus Prolateness and get the Pearson correlation coefficient to evaluate 
        the correlation between Rg and Prolateness. 

        Parameters
        ----------
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        size: int, optional
            The size of the scatter marker points. Default is 4.
        save: bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        ax: plt.Axes, optional
            The axes on which to plot. Default is None, which creates a new figure and axes.
        verbose: bool, optional
            Verbosity for the output of the method.

        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        analysis = self.analysis
        
        if ax is None:
            fig, ax = plt.subplots(dpi=dpi)  # Create a new figure if ax is not provided
        else:
            fig = ax.figure  # Use the figure associated with the provided ax

        for ensemble in analysis.ensembles:
            x = mdtraj.compute_rg(ensemble.trajectory)
            y = compute_prolateness(ensemble.trajectory)
            p = np.corrcoef(x, y)
            ax.scatter(x, y, s=size, label=ensemble.code)
            msg = f"Pearson coeff for {ensemble.code} = {round(p[0][1], 3)}"
            if verbose:
                print(msg)
            else:
                logger.info(msg)

        ax.set_ylabel("Prolateness")
        ax.set_xlabel(r"Radius of Gyration ($R_g$) [nm]")
        ax.set_title("Rg vs. Prolateness")
        ax.legend()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'Rg_vs_Prolateness_' + analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Rg vs. Prolateness plot saved to {self.plot_dir}/Rg_vs_Prolateness_{analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def _get_protein_dssp_data_dict(self):
        ensembles = self.analysis.ensembles
        dssp_data_dict = {}
        for ensemble in ensembles:
            dssp_data_dict[ensemble.code] = mdtraj.compute_dssp(ensemble.trajectory)
        return dssp_data_dict
    
    def relative_dssp_content(self,
            dssp_code: str = 'H', 
            dpi: int = 96,
            auto_xticks: bool = False,
            xtick_interval: int = 5,
            figsize: Tuple[float, float] = (10, 5),
            save: bool = False,
            ax: plt.Axes = None,
        ) -> plt.Axes:
        """
        Plot the relative ss content in each ensemble for each residue. 

        Parameters
        ----------
        dssp_code : str, optional
            The selected dssp code , it could be selected between 'H' for Helix, 'C' for Coil and 'E' for strand. It works based on
            the simplified DSSP codes
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96. 
        auto_xticks: bool, optional
            If True, use matplotlib default xticks.
        xtick_interval: int, optional
            If `auto_xticks` is False, this parameter defines the interval between displayed residue indices on the x-axis.
            Residue 1 is always included,followed by every `xtick_interval` residues (e.g., 1, 5, 10, 15 if `xtick_interval`=5).
        figsize : Tuple[float, float], optional
            The size of the figure in inches. Default is (10, 5).
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        ax : plt.Axes, optional
            The axes on which to plot. Default is None, which creates a new figure and axes.



        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        if self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")
        
        protein_dssp_data_dict = self._get_protein_dssp_data_dict()

        if ax is None:
            fig, ax = plt.subplots(dpi=dpi, figsize=(10, 5))
        else:
            fig = ax.figure

        bottom = np.zeros(max(data.shape[1] for data in protein_dssp_data_dict.values()))
        max_length = len(bottom)

        for protein_name, dssp_data in protein_dssp_data_dict.items():
            # Count the occurrences of 'H' in each column
            ss_counts = np.count_nonzero(dssp_data == dssp_code, axis=0)
            
            # Calculate the total number of residues for each position
            total_residues = dssp_data.shape[0]
            
            # Calculate the relative content of 'H' for each residue
            relative_ss_content = ss_counts / total_residues

            # Interpolate or pad the relative content to ensure all ensembles have the same length
            if len(relative_ss_content) < max_length:
                relative_ss_content = np.pad(relative_ss_content, (0, max_length - len(relative_ss_content)), mode='constant')
            
            # Plot the relative content for each protein
            x = np.arange(len(relative_ss_content))
            mask = x < len(dssp_data[0])  # Create a mask to filter out padded values
            ax.plot(x[mask], relative_ss_content[mask], marker='o', linestyle='dashed', label=protein_name, alpha=0.5)

            bottom += relative_ss_content
        if not auto_xticks:

            tick_labels = [1] + [i for i in range(xtick_interval, len(x) + 1, xtick_interval)]
            tick_positions = [i - 1 for i in tick_labels]  # convert to 0-based indexing
            ax.set_xticks(tick_positions, labels=tick_labels)
        
        ax.set_xlabel('Residue Index')
        if dssp_code == 'H':
            dssp_name = 'Helix'
        elif dssp_code == 'C':
            dssp_name = 'Coil'
        elif dssp_code == 'E':
            dssp_name = 'Strand'
        else:
            raise KeyError(dssp_code)
        ax.set_ylabel(f'Relative Content of {dssp_name}')
        ax.set_title(f'{dssp_name} Content per Residue in the Ensemble')
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))# put the legend outside of the plot

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'relative_helix_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
        
        return ax

    def _get_rg_data_dict(self):
        ensembles = self.analysis.ensembles
        rg_dict = {}
        for ensemble in ensembles:
            rg_dict[ensemble.code] = mdtraj.compute_rg(ensemble.trajectory)
        return rg_dict

    def radius_of_gyration(
            self,
            bins: int = 50,
            hist_range: Tuple = None,
            multiple_hist_ax: bool = False,
            violin_plot: bool = True,
            x_ticks_rotation: int = 45,
            summary_stat: str = 'mean',
            color: str = 'lightblue',
            dpi: int = 96,
            save: bool = False,
            ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None,
        ) -> Union[plt.Axes, List[plt.Axes]]:
        """
        Plot the distribution of the radius of gyration (Rg) within each ensemble.

        Parameters
        ----------
        bins : int, optional
            The number of bins for the histogram. Default is 50.
        hist_range : Tuple, optional
            A tuple with a min and max value for the histogram. Default is None,
            which corresponds to using the min and max value across all data.
        multiple_hist_ax: bool, optional
            If True, it will plot each histogram in a different axis.
        violin_plot : bool, optional
            If True, a violin plot is visualized. Default is True.
        x_ticks_rotation : int, optional
            The rotation angle of the x-axis tick labels for the violin plot. Default is 45
        summary_stat: str, optional
            Specifies whether to display the "mean", "median", or "both" as reference lines on the plots.
            This applies when violin_plot is True or when multiple_hist_ax is True for histograms.
        color : str, optional
            Color of the violin plot. Default is lightblue.
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file. Default is False.
        ax : Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The axes on which to plot. If None, new axes will be created. Default is None.

        Returns
        -------
        Union[plt.Axes, List[plt.Axes]]
            Returns a single Axes object or a list of Axes objects containing the plot(s).

        Notes
        -----
        This method plots the distribution of the radius of gyration (Rg) within each ensemble in the analysis.

        The Rg values are binned according to the specified number of bins (`bins`) and range (`hist_range`) and 
        displayed as histograms. Additionally, dashed lines representing the mean and median Rg values are overlaid
        on each histogram.
        """

        # Calculate features.
        rg_data_dict = self._get_rg_data_dict()
        hist_data = list(rg_data_dict.values())
        labels = list(rg_data_dict.keys())
        n_systems = len(rg_data_dict)

        # Plot.
        custom_axes = ax is not None
        if not violin_plot and multiple_hist_ax:
            # One axis for each histogram.
            if ax is None:
                fig, ax = plt.subplots(
                    1, n_systems,
                    figsize=(3 * n_systems, 3),
                    dpi=dpi
                )
            else:
                if not isinstance(ax, (list, np.ndarray)):
                    ax = [ax]
                ax = np.array(ax).flatten()
                fig = ax[0].figure
        else:
            # Only one axis for all histograms.
            if ax is None:
                fig, ax = plt.subplots(dpi=dpi)
            else:
                fig = ax.figure

        axis_label = r"$R_{g} [nm]$"
        title = ""

        if violin_plot:
            
            plot_violins(
                ax=ax,
                data=hist_data,
                labels=labels,
                summary_stat=summary_stat,
                title=title,
                xlabel=axis_label,
                color=color,
                x_ticks_rotation=x_ticks_rotation
            )
        else:
            if not multiple_hist_ax:
                plot_histogram(
                    ax=ax,
                    data=hist_data,
                    labels=labels,
                    bins=bins,
                    range=hist_range,
                    title=title,
                    xlabel=axis_label,
                )
            else:
                _bins = _get_hist_bins(
                    data=hist_data, bins=bins, range=hist_range
                )
                h_args = {"histtype": "step", "density": True}

                if isinstance(ax, np.ndarray):
                    ax = ax.flatten()
                y_max = 0
                for hist_data_i in hist_data:
                    counts, _ = np.histogram(hist_data_i, bins=_bins, density=True)
                    y_max = max(y_max, counts.max())
                for i, (name_i, rg_i) in enumerate(rg_data_dict.items()):
                    ax[i].set_ylim(0, y_max * 1.1)  # Add a little margin
                    ax[i].hist(rg_i, bins=_bins, label=name_i, **h_args)
                    ax[i].set_title(name_i)
                    if i == 0:
                        ax[i].set_ylabel("Density")
                    ax[i].set_xlabel(axis_label)
                    legend_handles = []
                    if summary_stat in ('mean', 'both'):
                        mean_rg = np.mean(rg_i)
                        mean_line = ax[i].axvline(mean_rg, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                    if summary_stat in ('median', 'both'):
                        median_rg = np.median(rg_i)
                        median_line = ax[i].axvline(median_rg, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)

                    if legend_handles:
                        ax[i].legend(handles=legend_handles, loc='upper right')

                    if not custom_axes:
                        fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'rg_comparison_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Rg distribution plot saved to {self.plot_dir}/rg_comparison_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def _get_distance_matrix_ens_dict(self):
        ensembles = self.analysis.ensembles
        distance_matrix_ens_dict = {}
        for ensemble in ensembles:
            selector = ensemble.atom_selector
            
            trajectory = ensemble.trajectory
            xyz_ens = trajectory.xyz[:,trajectory.topology.select(selector)]
            distance_matrix_ens_dict[ensemble.code] = get_distance_matrix(xyz_ens)
        return distance_matrix_ens_dict

    def _get_contact_ens_dict(self):
        ensembles = self.analysis.ensembles
        distance_matrix_ens_dict = {}
        contact_ens_dict = {}
        for ensemble in ensembles:
            xyz_ens = ensemble.trajectory.xyz[:,ensemble.trajectory.topology.select(ensemble.atom_selector)]
            distance_matrix_ens_dict[ensemble.code] = get_distance_matrix(xyz_ens)
            contact_ens_dict[ensemble.code] = get_contact_map(distance_matrix_ens_dict[ensemble.code])
        return contact_ens_dict
     
    def end_to_end_distances(self, rg_norm: bool = False, 
                         bins: int = 50, 
                         hist_range: Tuple = None, 
                         violin_plot: bool = True,
                         summary_stat: str = 'mean',
                         dpi = 96,
                         save: bool = False,
                         color: str = 'lightblue', 
                         multiple_hist_ax = False,
                         x_ticks_rotation: int = 45,
                         ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None) -> Union[plt.Axes, List[plt.Axes]]:
        """
        Plot end-to-end distance distributions.

        Parameters
        ----------
        rg_norm: bool, optional
            Normalize end-to-end distances on the average radius of gyration.
        bins : int, optional
            The number of bins for the histogram. Default is 50.
        hist_range: Tuple, optional
            A tuple with a min and max value for the histogram. Default is None,
            which corresponds to using the min a max value across all data.
        violin_plot : bool, optional
            If True, a violin plot is visualized. Default is True.
        summary_stat: str, optional
            Specifies whether to display the "mean", "median", or "both" as reference lines on the plots. 
            This applies when violin_plot is True or when multiple_hist_ax is True for histograms.
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        ax : Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The axes on which to plot. Default is None, which creates a new figure and axes.
        color: str, optional
            Change the color of the violin plot. Default is lightblue.
        multiple_hist_ax: bool, optional
            If True, it will plot each histogram in a different axis.
        x_ticks_rotation: int, optional
            The rotation angle of the x-axis tick labels for the violin plot. Default is 45

        Returns
        -------
        Union[plt.Axes, List[plt.Axes]]
            The Axes object or a list of Axes objects containing the plot(s).
        """

        ensembles = self.analysis.ensembles

        # Calculate features.
        hist_data = []
        labels = []
        n_systems = len(ensembles)

        for ensemble in ensembles:
            ca_indices = ensemble.trajectory.topology.select(ensemble.atom_selector)
            hist_data_i = mdtraj.compute_distances(
                ensemble.trajectory, [[ca_indices[0], ca_indices[-1]]]
            ).ravel()
            if rg_norm:
                rg_i = mdtraj.compute_rg(ensemble.trajectory).mean()
                hist_data_i = hist_data_i / rg_i
            hist_data.append(hist_data_i)
            labels.append(ensemble.code)

        # Plot setup depending on plot type and multiple_hist_ax setting
        custom_axes = ax is not None

        if not violin_plot and multiple_hist_ax:
            # Create one axis for each histogram
            if ax is None:
                fig, ax = plt.subplots(
                    1, n_systems, 
                    figsize=(3 * n_systems, 3),
                    dpi=dpi
                )
            else:
                if not isinstance(ax, (list, np.ndarray)):
                    ax = [ax]
                ax = np.array(ax).flatten()
                fig = ax[0].figure
        else:
            # Single axis for all histograms or violin plot
            if ax is None:
                fig, ax = plt.subplots(dpi=dpi)
            else:
                fig = ax.figure

        # Set axis labels and title based on rg_norm
        if not rg_norm:
            axis_label = r"$R_{ee} [nm]$"
            title = ""
        else:
            axis_label = r"$R_{ee} / \langle R_g \rangle$"
            title = r"Normalized End-to-End Distance ($R_{ee} / \langle R_g \rangle$) Distribution"

        if violin_plot:
            # Plot the violin plot
            plot_violins(
                ax=ax,
                data=hist_data,
                labels=labels,
                summary_stat=summary_stat,
                title=title,
                xlabel=axis_label,
                color=color,
                x_ticks_rotation=x_ticks_rotation
            )
        else:
            if not multiple_hist_ax:
                # Single histogram plot
                plot_histogram(
                    ax=ax,
                    data=hist_data,
                    labels=labels,
                    bins=bins,
                    range=hist_range,
                    title=title,
                    xlabel=axis_label
                )
            else:
                # Plot separate histograms for each ensemble on separate axes
                _bins = _get_hist_bins(
                    data=hist_data, bins=bins, range=hist_range
                )
                h_args = {"histtype": "step", "density": True}
                y_max = 0
                for hist_data_i in hist_data:
                    counts, _ = np.histogram(hist_data_i, bins=_bins, density=True)
                    y_max = max(y_max, counts.max())
                for i, (name_i, hist_data_i) in enumerate(zip(labels, hist_data)):
                    ax[i].hist(hist_data_i, bins=_bins, label=name_i, **h_args)
                    ax[i].set_ylim(0, y_max * 1.1)  # Add a little margin
                    ax[i].set_title(name_i)
                    if i == 0:
                        ax[i].set_ylabel("Density")
                    ax[i].set_xlabel(axis_label)

                    legend_handles = []
                    if summary_stat == 'mean':
                        mean_dist = np.mean(hist_data_i)
                        mean_line = ax[i].axvline(mean_dist, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                    if summary_stat == 'median':
                        median_dist = np.median(hist_data_i)
                        median_line = ax[i].axvline(median_dist, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)
                    if summary_stat == 'both':
                        mean_dist = np.mean(hist_data_i)
                        mean_line = ax[i].axvline(mean_dist, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                        median_dist = np.median(hist_data_i)
                        median_line = ax[i].axvline(median_dist, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)

                    if legend_handles:
                        ax[i].legend(handles=legend_handles, loc='upper right')
                if not custom_axes:
                    fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'e2e_distances_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"End-to-End distances distribution plot saved to {self.plot_dir}/e2e_distances_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def asphericity(self, 
                    bins: int = 50,
                    hist_range: Tuple = None,
                    violin_plot: bool = True,
                    summary_stat: str = 'mean',
                    dpi: int = 96,
                    save: bool = False,
                    color: str = 'lightblue',
                    multiple_hist_ax: bool = False,
                    x_ticks_rotation: int = 45,
                    ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None) -> plt.Axes:
        """
        Plot asphericity distribution in each ensemble.
        Asphericity is calculated based on the gyration tensor.

        Parameters
        ----------
        bins : int, optional
            The number of bins for the histogram. Default is 50.
        hist_range: Tuple, optional
            A tuple with a min and max value for the histogram range. Default is None,
            which corresponds to using the min a max value across all data.
        violin_plot : bool, optional
            If True, a violin plot is visualized. Default is True.
        summary_stat : str, optional
            Specifies whether to display the "mean", "median", or "both" as reference lines on the plots. 
            This applies when violin_plot is True or when multiple_hist_ax is True for histograms.
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        color : str, optional
            Color of the violin plot. Default is lightblue.
        multiple_hist_ax : bool, optional
            If True, each histogram will be plotted on separate axes. Default is False.
        x_ticks_rotation : int, optional
            The rotation angle of the x-axis tick labels for the violin plot. Default is 45
        ax : Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The axes on which to plot. Default is None, which creates a new figure and axes.

        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        ensembles = self.analysis.ensembles

        # Calculate asphericity for each ensemble
        asph_list = []
        labels = []
        for ensemble in ensembles:
            asphericity = compute_asphericity(ensemble.trajectory)
            asph_list.append(asphericity)
            labels.append(ensemble.code)

        # Plot setup depending on the type of plot and multiple_hist_ax setting
        custom_axes = ax is not None

        if not violin_plot and multiple_hist_ax:
            # Create one axis for each histogram
            if ax is None:
                fig, ax = plt.subplots(
                    1, len(ensembles), 
                    figsize=(3 * len(ensembles), 3),
                    dpi=dpi
                )
            else:
                if not isinstance(ax, (list, np.ndarray)):
                    ax = [ax]
                ax = np.array(ax).flatten()
                fig = ax[0].figure
        else:
            # Single axis for all histograms or violin plot
            if ax is None:
                fig, ax = plt.subplots(dpi=dpi)
            else:
                fig = ax.figure

        axis_label = "Asphericity"
        title = ""

        if violin_plot:
            # Plot the violin plot
            plot_violins(
                ax=ax,
                data=asph_list,
                labels=labels,
                summary_stat=summary_stat,
                title=title,
                xlabel=axis_label,
                color=color
            )
        else:
            if not multiple_hist_ax:
                # Single histogram plot
                plot_histogram(
                    ax=ax,
                    data=asph_list,
                    labels=labels,
                    bins=bins,
                    range=hist_range,
                    title=title,
                    xlabel=axis_label,
                    x_ticks_rotation=x_ticks_rotation
                )
            else:
                # Plot separate histograms for each ensemble on separate axes
                _bins = _get_hist_bins(
                    data=asph_list, bins=bins, range=hist_range
                )
                h_args = {"histtype": "step", "density": True}
                y_max = 0
                for hist_data_i in _bins:
                    counts, _ = np.histogram(hist_data_i, bins=_bins, density=True)
                    y_max = max(y_max, counts.max())
                for i, (name_i, asph_data_i) in enumerate(zip(labels, asph_list)):
                    ax[i].hist(asph_data_i, bins=_bins, label=name_i, **h_args)
                    ax[i].set_ylim(0, y_max * 1.1)  # Add a little margin
                    ax[i].set_title(name_i)
                    if i == 0:
                        ax[i].set_ylabel("Density")
                    ax[i].set_xlabel(axis_label)

                    # Adding mean/median/both lines with legend
                    legend_handles = []
                    if summary_stat == 'mean':
                        mean_asph = np.mean(asph_data_i)
                        mean_line = ax[i].axvline(mean_asph, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                    if summary_stat == 'median':
                        median_asph = np.median(asph_data_i)
                        median_line = ax[i].axvline(median_asph, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)
                    if summary_stat == 'both':
                        mean_asph = np.mean(asph_data_i)
                        mean_line = ax[i].axvline(mean_asph, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                        median_asph = np.median(asph_data_i)
                        median_line = ax[i].axvline(median_asph, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)

                    # Add legend if needed
                    if legend_handles:
                        ax[i].legend(handles=legend_handles, loc='upper right')

                if not custom_axes:
                    fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'asphericity_dist_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Asphericity distribution plot saved to {self.plot_dir}/asphericity_dist_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def prolateness(self,
                bins: int = 50,
                hist_range: Tuple = None,
                violin_plot: bool = True,
                summary_stat: str = 'mean',
                dpi: int = 96,
                save: bool = False,
                color: str = 'lightblue',
                multiple_hist_ax: bool = False,
                x_ticks_rotation: int = 45,
                ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None) -> plt.Axes:
        """
        Plot prolateness distribution in each ensemble.
        Prolateness is calculated based on the gyration tensor.

        Parameters
        ----------
        bins : int, optional
            The number of bins for the histogram. Default is 50.
        hist_range : Tuple, optional
            A tuple with a min and max value for the histogram. Default is None,
            which corresponds to using the min a max value across all data.
        violin_plot : bool, optional
            If True, a violin plot is visualized. Default is True.
        summary_stat : str, optional
            Specifies whether to display the "mean", "median", or "both" as reference lines on the plots.
            This applies when violin_plot is True or when multiple_hist_ax is True for histograms.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        color : str, optional
            Color of the violin plot. Default is lightblue.
        multiple_hist_ax : bool, optional
            If True, each histogram will be plotted on separate axes. Default is False.
        x_ticks_rotation : int, optional
            The rotation angle of the x-axis tick labels for the violin plot. Default is 45
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        ax : Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The axes on which to plot. Default is None, which creates a new figure and axes.

        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        ensembles = self.analysis.ensembles

        # Calculate prolateness for each ensemble
        prolat_list = []
        labels = []
        for ensemble in ensembles:
            prolat = compute_prolateness(ensemble.trajectory)
            prolat_list.append(prolat)
            labels.append(ensemble.code)
        

        # Plot setup depending on the type of plot and multiple_hist_ax setting
        custom_axes = ax is not None

        if not violin_plot and multiple_hist_ax:
            # Create one axis for each histogram
            if ax is None:
                fig, ax = plt.subplots(
                    1, len(ensembles), 
                    figsize=(3 * len(ensembles), 3),
                    dpi= dpi
                )
            else:
                if not isinstance(ax, (list, np.ndarray)):
                    ax = [ax]
                ax = np.array(ax).flatten()
                fig = ax[0].figure
        else:
            # Single axis for all histograms or violin plot
            if ax is None:
                fig, ax = plt.subplots(dpi=96)
            else:
                fig = ax.figure

        axis_label = "Prolateness"
        title = "Prolateness Distribution"

        if violin_plot:
            # Plot the violin plot
            plot_violins(
                ax=ax,
                data=prolat_list,
                labels=labels,
                summary_stat=summary_stat,
                title=title,
                xlabel=axis_label,
                color=color
            )
        else:
            if not multiple_hist_ax:
                # Single histogram plot
                plot_histogram(
                    ax=ax,
                    data=prolat_list,
                    labels=labels,
                    bins=bins,
                    range=hist_range,
                    title=title,
                    xlabel=axis_label,
                    x_ticks_rotation=x_ticks_rotation
                )
            else:
                # Plot separate histograms for each ensemble on separate axes
                _bins = _get_hist_bins(
                    data=prolat_list, bins=bins, range=hist_range
                )
                h_args = {"histtype": "step", "density": True}
                y_max = 0
                for hist_data_i in _bins:
                    counts, _ = np.histogram(hist_data_i, bins=_bins, density=True)
                    y_max = max(y_max, counts.max())
                for i, (name_i, prolat_data_i) in enumerate(zip(labels, prolat_list)):
                    ax[i].hist(prolat_data_i, bins=_bins, label=name_i, **h_args)
                    ax[i].set_ylim(0, y_max * 1.1)  # Add a little margin
                    ax[i].set_title(name_i)
                    if i == 0:
                        ax[i].set_ylabel("Density")
                    ax[i].set_xlabel(axis_label)

                    # Adding mean/median/both lines with legend
                    legend_handles = []
                    if summary_stat == 'mean':
                        mean_prolat = np.mean(prolat_data_i)
                        mean_line = ax[i].axvline(mean_prolat, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                    if summary_stat == 'median':
                        median_prolat = np.median(prolat_data_i)
                        median_line = ax[i].axvline(median_prolat, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)
                    if summary_stat == 'both':
                        mean_prolat = np.mean(prolat_data_i)
                        mean_line = ax[i].axvline(mean_prolat, color='k', linestyle='dashed', linewidth=1)
                        mean_legend = Line2D([0], [0], color='k', linestyle='dashed', linewidth=1, label='Mean')
                        legend_handles.append(mean_legend)
                        median_prolat = np.median(prolat_data_i)
                        median_line = ax[i].axvline(median_prolat, color='r', linestyle='dashed', linewidth=1)
                        median_legend = Line2D([0], [0], color='r', linestyle='dashed', linewidth=1, label='Median')
                        legend_handles.append(median_legend)

                    # Add legend if needed
                    if legend_handles:
                        ax[i].legend(handles=legend_handles, loc='upper right')

                if not custom_axes:
                    fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'prolateness_dist_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Prolateness distribution plot saved to {self.plot_dir}/prolateness_dist_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def alpha_angles(self, bins: int = 50, save: bool = False, ax: plt.Axes = None) -> plt.Axes:
        """
        Alpha angles: Angles between four consecutive Cα atoms along the protein backbone.
        This method calculates the alpha angles for each ensemble in the analysis and plots their distribution

        Parameters
        ----------
        bins : int
            The number of bins for the histogram. Default is 50.
        save : bool, optional
            If True, the plot will be saved as an image file. Default is False.
        ax : plt.Axes, optional
            The axes on which to plot. Default is None, which creates a new figure and axes.

        Returns
        -------
        plt.Axes
            The Axes object containing the plot.
        """

        ensembles = self.analysis.ensembles

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure

        data = []
        labels = []
        for ensemble in ensembles:
            data_i = featurize_a_angle(
                ensemble.trajectory,
                get_names=False,
                atom_selector=ensemble.atom_selector
            ).ravel()
            data.append(data_i)
            labels.append(ensemble.code)

        plot_histogram(
            ax=ax,
            data=data,
            labels=labels,
            bins=bins,
            range=(-np.pi, np.pi),
            title="Distribution of Alpha Angles",
            xlabel="Angle [rad]"
        )

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'alpha_dist_' + self.analysis.ens_codes[0]))

        return ax

    def contact_prob_maps(self,
            log_scale: bool = True,
            avoid_zero_count: bool = False,
            threshold: float = 0.8,
            dpi: int = 96, 
            color: str = 'Blues',
            save: bool = False, 
            ax: Union[None, List[plt.Axes], np.ndarray] = None
        ) -> Union[List[plt.Axes], np.ndarray]:
        """
        Plot the contact probability map based on the threshold.

        Parameters
        ----------
        log_scale : bool, optional
            If True, use log scale range. Default is True.
        avoid_zero_count: bool, optional
            If True, avoid contacts with zero counts by adding to all contacts a pseudo count of 1e-6.
        threshold : float, optional
            Determining the threshold for calculating the contact frequencies. Default is 0.8 [nm].
        dpi : int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        color : str, optional
            The colormap to use for the contact probability map. Default is 'Blues'.
        save : bool, optional
             If True, the plot will be saved as an image file in the specified directory. Default is False.
        ax : Union[None, List[plt.Axes], np.ndarray], optional
            The axes on which to plot. If None, new axes will be created. Default is None.


        Returns
        -------
        Union[List[plt.Axes], np.ndarray]
            Returns a list or array of Axes objects representing the subplot grid.
        """

        ensembles = self.analysis.ensembles
        num_proteins = len(ensembles)
        num_cols = num_proteins
        num_rows = 1

        cmap = plt.get_cmap(color)

        if ax is None:
            custom_axes = False
            fig, axes = plt.subplots(num_rows, num_cols, figsize=(6 * num_cols, 5), dpi=dpi)
            axes = np.atleast_1d(axes).flatten()
        else:
            custom_axes = True
            ax_array = np.array(ax)
            axes = ax_array.flatten()
            fig = axes[0].figure
        for i, ensemble in enumerate(ensembles):
            ax = axes[i]
            
            matrix_p_map = contact_probability_map(
                ensemble.trajectory,
                scheme='ca' if not ensemble.coarse_grained else 'closest',
                threshold=threshold
            )
            if avoid_zero_count:
                matrix_p_map += 1e-6

            if log_scale:
                im = ax.imshow(matrix_p_map, cmap=cmap,
                               norm=LogNorm(vmin=1e-3, vmax=1.0))
            else:
                im = ax.imshow(matrix_p_map, cmap=cmap)
            ax.set_title(ensemble.code, fontsize=14)
            ax.set_xlabel('j')
            ax.set_ylabel('i')
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label('Contact frequency', fontsize=14)
            cbar.ax.tick_params(labelsize=14)

        if not custom_axes:
            fig.tight_layout()

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'contact_prob_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Contact probability map saved to {self.plot_dir}/contact_prob_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return axes

    def _pair_ids(self, min_sep=2,max_sep = None ):
        analysis = self.analysis
        pair_ids = []
        for ens in analysis.ensembles:
            ca_ids = ens.trajectory.topology.select('name')
            atoms = list(ens.trajectory.topology.atoms)
            max_sep = get_max_sep(L=len(atoms), max_sep=max_sep)
    # Get all pair of ids.
            for i, id_i in enumerate(ca_ids):
                for j, id_j in enumerate(ca_ids):
                    if j - i >= min_sep:
                        if j - i > max_sep:
                            continue
                        pair_ids.append([id_i, id_j])
        return pair_ids
    
    def ramachandran_plots(
        self,
        two_d_hist: bool = True,
        bins: Tuple[int, int, int] = (-180, 180, 80),
        dpi: int = 96,
        color: str = 'viridis',
        log_scale: bool = True,
        save: bool = False,
        ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None
     ) -> Union[List[plt.Axes], plt.Axes]:

        """
        Ramachandran plot. If two_d_hist=True it returns a 2D histogram 
        for each ensemble. If two_d_hist=False it returns a simple scatter plot 
        for all ensembles in one plot.

        Parameters
        ----------
        two_d_hist : bool, optional
            If True, it returns a 2D histogram for each ensemble. Default is True.
        bins : tuple, optional
            You can customize the bins for 2D histogram. Default is (-180, 180, 80).
        log_scale : bool, optional
            If True, the histogram will be plotted on a logarithmic scale. Default is True.
        color : str, optional   
            The colormap to use for the 2D histogram. Default is 'viridis'.
        dpi : int, optional 
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.
        ax : Union[None, plt.Axes, np.ndarray, List[plt.Axes]], optional
            The axes on which to plot. If None, new axes will be created. Default is None.

        Returns
        -------
        Union[List[plt.Axes], plt.Axes]
            If two_d_hist=True, returns a list of Axes objects representing the subplot grid for each ensemble. 
            If two_d_hist=False, returns a single Axes object representing the scatter plot for all ensembles.

        """
        if self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")

        ensembles = self.analysis.ensembles
        if two_d_hist:
            if ax is None:
                custom_axes = False
                fig, ax = plt.subplots(1, len(ensembles), figsize=(5 * len(ensembles), 5))
            else:
                custom_axes = True
                if not isinstance(ax, (list, np.ndarray)):
                    ax = [ax]
                ax = np.array(ax).flatten()
                fig = ax[0].figure

            if len(ax) < len(ensembles):
                raise ValueError(f"Not enough axes provided: expected {len(ensembles)}, got {len(ax)}.")

            rama_linspace = np.linspace(bins[0], bins[1], bins[2])
            for ensemble, ax_i in zip(ensembles, ax):
                phi_angles = np.degrees(mdtraj.compute_phi(ensemble.trajectory)[1])[:, :-1]
                psi_angles = np.degrees(mdtraj.compute_psi(ensemble.trajectory)[1])[:, 1:]

                hist2d = ax_i.hist2d(
                    phi_angles.ravel(),
                    psi_angles.ravel(),
                    cmap=color,
                    bins=(rama_linspace, rama_linspace),
                    norm=colors.LogNorm() if log_scale else None,
                    density=True
                )

                ax_i.set_title(f'{ensemble.code}', fontsize=12)
                ax_i.set_xlabel(r'$\phi$ (°)', fontsize=12)
                ax_i.set_ylabel(r'$\psi$ (°)', fontsize=12)
                ax_i.tick_params(axis='both', which='major', labelsize=12)

                colorbar = fig.colorbar(hist2d[3], ax=ax_i)
                colorbar.set_label('Density', fontsize=12)

            if not custom_axes:
                fig.tight_layout()
        else:
            if ax is None:
                fig, ax = plt.subplots(1, 1)
            else:
                fig = ax.figure
            for ensemble in ensembles:
                phi_angles = np.degrees(mdtraj.compute_phi(ensemble.trajectory)[1])
                psi_angles = np.degrees(mdtraj.compute_psi(ensemble.trajectory)[1])
                ax.scatter(phi_angles, psi_angles, s=1, label=ensemble.code)
            ax.set_xlabel('Phi (ϕ) Angle (degrees)', fontsize=12)
            ax.set_ylabel('Psi (ψ) Angle (degrees)', fontsize=12)
            ax.tick_params(axis='both', which='major', labelsize=12)
            ax.set_title('Ramachandran Plot', fontsize=12)
            ax.legend(fontsize=12)

        fig.tight_layout(pad=3.0)
        if save:
            fig.savefig(os.path.join(self.plot_dir, 'ramachandran_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')
            msg = f"Ramachandran plot saved to {self.plot_dir}/ramachandran_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def site_specific_flexibility(self, 
                        pointer: List[int] = None, 
                        auto_xticks: bool = False,
                        xtick_interval: int = 5,
                        dpi: int = 96,
                        figsize: Tuple[int, int] = (15, 5), 
                        save: bool = False,
                        ax: Union[None, plt.Axes] = None) -> plt.Axes:
        """
        Generate a plot of the site-specific flexibility parameter.
        
        This plot shows the site-specific measure of disorder, which is sensitive to local flexibility based on 
        the circular variance of the Ramachandran angles φ and ψ for each residue in the ensemble.
        The score ranges from 0 for identical dihedral angles for all conformers at the residue i to 1 for a 
        uniform distribution of dihedral angles at the residue i. (For more information about this method look at here https://onlinelibrary.wiley.com/doi/full/10.1002/pro.4906)

        Parameters
        ----------
        pointer: List[int], optional
            A list of desired residues. Vertical dashed lines will be added to point to these residues. Default is None.
        auto_xticks: bool, optional
            If True, use matplotlib default xticks.
        xtick_interval: int, optional
            If `auto_xticks` is False, this parameter defines the interval between displayed residue indices on the x-axis.
            Always start with 1, followed by every `xtick_interval` residues (e.g., 1, 5, 10, 15, ... if `xtick_interval`=5).
        figsize: Tuple[int, int], optional
            The size of the figure. Default is (15, 5).
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file. Default is False.
        ax : Union[None, plt.Axes], optional
            The matplotlib Axes object on which to plot. If None, a new Axes object will be created. Default is None.
            
        Returns
        -------
        plt.Axes
            The matplotlib Axes object containing the plot.
        """
        
        if self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")
        
        features_dict = self.analysis.get_features(featurization='phi_psi')
        
        f = ss_measure_disorder(features_dict)
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        else:
            fig = ax.figure

        for key, values in f.items():
            x = np.arange(1, len(values) + 1)
            ax.plot(x, values, marker='o', linestyle='-', label=key)
        
        if not auto_xticks:
            ticks = [1]
            next_tick = xtick_interval
            while next_tick <= len(x):
                ticks.append(next_tick)
                next_tick += xtick_interval
            ax.set_xticks(ticks)
        # ax.set_title("Site-specific Flexibility parameter plot", fontsize=22, weight='bold')
        ax.set_xlabel("Residue Index", fontsize=12)
        ax.set_ylabel("Site-specific Flexibility parameter", fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
        # ax.legend(fontsize=12)

        if pointer is not None:
            for res in pointer:
                ax.axvline(x=res, color='blue', linestyle='--', alpha=0.3, linewidth=1)
        
        if save:
            fig.savefig(os.path.join(self.plot_dir, 'ss_flexibility_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')  
            msg = f"Site-specific flexibility plot saved to {self.plot_dir}/ss_flexibility_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        fig.tight_layout()
        return ax

    def site_specific_order(self, 
                        pointer: List[int] = None,  
                        auto_xticks: bool = True,
                        xtick_interval: int = 5,
                        dpi: int = 96,
                        figsize: Tuple[int, int] = (15, 5),
                        save: bool = False, 
                        ax: Union[None, plt.Axes] = None) -> plt.Axes:
        """
        Generate a plot of the site-specific order parameter.
        The function computes and plots per-residue order parameters that quantify how consistently each residue's backbone orientation 
        is aligned with the rest of the chain across all conformers in an ensemble.
        The result is a per-residue value between 0 and 1: values near 1 indicate high orientational order (rigid or structured regions), 
        while values near 0 reflect disorder (flexible or unstructured regions). This measure captures long-range orientational correlations
        in the backbone and is particularly useful for detecting weakly ordered segments in intrinsically disordered proteins.
        (For more information about this method look at here https://onlinelibrary.wiley.com/doi/full/10.1002/pro.4906)

        Parameters
        ----------
        pointer: List[int], optional
            A list of desired residues. Vertical dashed lines will be added to point to these residues. Default is None.
        auto_xticks: bool, optional
            If True, use matplotlib default xticks.
        xtick_interval: int, optional
            If `auto_xticks` is False, this parameter defines the interval between displayed residue indices on the x-axis.
            Always start with 1, followed by every `xtick_interval` residues (e.g., 1, 5, 10, 15, ... if `xtick_interval`=5).
        figsize: Tuple[int, int], optional
            The size of the figure. Default is (15, 5).
        save : bool, optional
            If True, the plot will be saved as an image file. Default is False.
        ax : Union[None, plt.Axes], optional
            The matplotlib Axes object on which to plot. If None, a new Axes object will be created. Default is None.
            
        Returns
        -------
        plt.Axes
            The matplotlib Axes object containing the plot.
        """
        
        ensembles = self.analysis.ensembles
        dict_ca_xyz = {}
        for ensemble in ensembles:
            ca_index = ensemble.trajectory.topology.select(ensemble.atom_selector)
            dict_ca_xyz[ensemble.code] = ensemble.trajectory.xyz[:, ca_index, :]

        dict_order_parameter = site_specific_order_parameter(dict_ca_xyz)
        
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        else:
            fig = ax.figure

        for key, values in dict_order_parameter.items():
            x = np.arange(1, len(values) + 1)
            ax.plot(x, values, label=key, marker= 'o', linestyle='-')

        if not auto_xticks:
            ticks = [1]
            next_tick = xtick_interval
            while next_tick <= len(x):
                ticks.append(next_tick)
                next_tick += xtick_interval
            ax.set_xticks(ticks)
        ax.set_title("Site-specific Order Parameter")
        ax.set_xlabel("Residue Index")
        ax.set_ylabel("Order parameter")
        ax.legend( loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
        
        if pointer is not None:
            for res in pointer:
                ax.axvline(x=res, color='blue', linestyle='--', alpha=0.3, linewidth=1)
        
        if save:
            fig.savefig(os.path.join(self.plot_dir, 'ss_order_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches='tight')  
            msg = f"Site-specific order parameter plot saved to {self.plot_dir}/ss_order_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def per_residue_mean_sasa(self,
                            probe_radius: float = 0.14,
                            n_sphere_points: int = 960, 
                            figsize: Tuple[int, int] = (15, 5),
                            dpi: int = 96,
                            size: int = 3,
                            auto_xticks: bool = True,
                            xtick_interval: int = 5,
                            pointer: List[int] = None, 
                            save: bool = False, 
                            ax: Union[None, plt.Axes] = None) -> plt.Axes:
        """
        Plot the average solvent-accessible surface area (SASA) for each residue among all conformations in an ensemble.
        This function uses the Shrake–Rupley algorithm as implemented in MDTraj (`mdtraj.shrake_rupley`) to compute
        the solvent-accessible surface area.
        
        Parameters
        ----------
        probe_radius: float, optional
            The radius of the probe sphere used in the Shrake–Rupley algorithm. Default is 0.14 nm.
        n_sphere_points: int, optional
            The number of points representing the surface of each atom, higher values leads to more accuracy. Default is 960.
        figsize: Tuple[int, int], optional
            Tuple specifying the size of the figure. Default is (15, 5).
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        size: int, optional
            The size of the marker points. Default is 3.
        auto_xticks: bool, optional
            If True, use matplotlib default xticks. Default is True.
        xtick_interval: int, optional
            If `auto_xticks` is False, this parameter defines the interval between displayed residue indices
            on the x-axis. Always start with 1, followed by every `xtick_interval` residues (e.g., 1, 5, 10, 15, ... if `xtick_interval`=5).
        pointer: List[int], optional
            List of desired residues to highlight with vertical dashed lines. Default is None.
        save : bool, optional
            If True, the plot will be saved as an image file. Default is False.
        ax : Union[None, plt.Axes], optional
            The matplotlib Axes object on which to plot. If None, a new Axes object will be created. Default is None.

        Returns
        -------
        plt.Axes
            Axes object containing the plot.
        """

        analysis = self.analysis

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        else:
            fig = ax.figure

        # Get the color cycle from matplotlib
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        
        for i, ens in enumerate(analysis.ensembles):
            color = colors[i % len(colors)]
            res_based_sasa = mdtraj.shrake_rupley(ens.trajectory, mode='residue', probe_radius=probe_radius,
                                                  n_sphere_points=n_sphere_points)
            sasa_mean = np.mean(res_based_sasa, axis=0)
            sasa_std = np.std(res_based_sasa, axis=0)        

            ax.plot(np.arange(1, len(sasa_mean) + 1), sasa_mean, '-o',markersize=size, color=color, label=ens.code)
            # ax.fill_between(np.arange(1, len(sasa_mean) + 1), sasa_mean - sasa_std, sasa_mean + sasa_std, alpha=0.3, color=colors[i % len(colors)])
            ax.plot(np.arange(1, len(sasa_mean) + 1), sasa_mean + sasa_std, '--', color=color, alpha=0.5, label=f'{ens.code} (mean ± SD)')
            ax.plot(np.arange(1, len(sasa_mean) + 1), sasa_mean - sasa_std, '--', color=color, alpha=0.5)
        
        # Set x-ticks
        if not auto_xticks:
            ticks = [1]
            next_tick = xtick_interval
            while next_tick <= len(sasa_mean):
                ticks.append(next_tick)
                next_tick += xtick_interval
            ax.set_xticks(ticks)

        ax.set_xlabel('Residue Index')
        ax.set_ylabel('Mean SASA [nm²]')
        ax.set_title('Mean SASA for Each Residue in Ensembles')
        ax.legend( loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
        # ax.grid(True)
        
        if pointer is not None:
            for res in pointer:
                ax.axvline(x=res, color='blue', linestyle='--', alpha=0.3, linewidth=1)

        if save:
            fig.savefig(os.path.join(self.plot_dir, 'local_sasa_' + self.analysis.ens_codes[0]), bbox_inches='tight', dpi=dpi)  
            msg = f"Local SASA plot saved to {self.plot_dir}/local_sasa_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def distance_maps(
        self, 
        min_sep: int = 2, 
        max_sep: Union[int, None] = None, 
        distance_type: str = "both",
        get_names: bool = True, 
        inverse: bool  = False,
        color: str = "plasma",
        dpi: int = 96,
        save: bool = False,
        ax: Union[None, plt.Axes, np.ndarray, List[plt.Axes]] = None,
        
    ) -> List[plt.Axes]:
        """
        Plot CA and/or COM distance maps for one or more protein ensembles.

        Parameters
        ----------
        min_sep : int, default=2
            Minimum sequence separation between residues to consider.
        max_sep : int or None, optional
            Maximum sequence separation. If None, no upper limit is applied.
        distance_type : {'ca', 'com', 'both'}, default='both'
            Specifies which type of distance map(s) to plot.
        get_names : bool, default=True
            Whether to return feature names from featurization (used internally).
        inverse : bool, default=False
            If True, compute and plot 1/distance instead of distance.
        color : str, default='plasma'
            Colormap to use for the distance maps.
        dpi : int, default=96
            The DPI (dots per inch) of the output figure.
        save : bool, default=False
            If True, the plot will be saved as an image file in the specified directory.
        ax : matplotlib Axes or array-like, optional
            Axes on which to plot. If None, a new figure and axes will be created.
       
        Returns
        -------
        List[matplotlib.axes.Axes]
            List of axes objects used for plotting.
        """

        distance_type = distance_type.lower()

        if distance_type in {"com", "both"} and self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")

        if distance_type not in {"ca", "com", "both"}:
            raise ValueError("`distance_type` must be one of {'CA', 'COM', 'both'}")

        if distance_type not in {"ca", "com", "both"}:
            raise ValueError("`distance_type` must be one of {'CA', 'COM', 'both'}")

        num_proteins = len(self.analysis.ensembles)

        # ---- layout -------------------------------------------------------------
        if distance_type == "both":
            nrows, ncols = 2, num_proteins
        else:
            nrows, ncols = 1, num_proteins

        if ax is None:
            custom_axes = False
            fig, axes = plt.subplots(
                nrows, ncols,
                figsize=(4 * ncols, 4 * nrows),
                dpi=dpi,
                squeeze=False   # <--- ensures 2D array
            )
        else:
            custom_axes = True
            axes = np.atleast_1d(ax)
            expected = 2 * num_proteins if distance_type == "both" else num_proteins
            if axes.size != expected:
                raise ValueError(f"`ax` must contain {expected} axes for show='{distance_type}' and {num_proteins} proteins.")
            axes = np.asarray(axes).reshape(nrows, ncols)
            fig = axes.flat[0].figure
        # ------------------------------------------------------------------------

        plotted_axes: List[plt.Axes] = []
        def set_labels(ax: plt.Axes):
            ax.set_xlabel("j")
            ax.set_ylabel("i")


        def maybe_inverse(dmap: np.ndarray, apply: bool) -> np.ndarray:
            if not apply:
                return dmap
            with np.errstate(divide='ignore', invalid='ignore'):
                inv = np.where(dmap != 0, 1.0 / dmap, 0.0)
            return inv

        for i, ens in enumerate(self.analysis.ensembles):
            traj = ens.trajectory
            feat, names = featurize_com_dist(
                traj=traj, min_sep=min_sep, max_sep=max_sep, inverse=inverse, get_names=get_names
            )
            logger.info(f"# Ensemble: {ens.code}")
            logger.info(f"features: {feat.shape}")

            if distance_type in {"ca", "both"}:
                ca_dmap = calc_ca_dmap(traj=traj, min_sep=min_sep, max_sep=max_sep)
                ca_dmap_mean = maybe_inverse(ca_dmap.mean(axis=0), inverse)
                row = 0  # always the first row
                col = i
                ax_ca = axes[row, col]
                im0 = ax_ca.imshow(ca_dmap_mean, cmap=color)
                ax_ca.set_title(f"{ens.code} CA")
                set_labels(ax_ca)
                cbar = fig.colorbar(im0, ax=ax_ca, shrink=0.8)
                label = "1 / distance [1/nm]" if inverse else "distance [nm]"
                cbar.set_label(label)
                plotted_axes.append(ax_ca)

            if distance_type in {"com", "both"}:
                com_dmap = calc_com_dmap(traj=traj, min_sep=min_sep, max_sep=max_sep)
                com_dmap_mean = maybe_inverse(com_dmap.mean(axis=0), inverse)
                row = 0 if distance_type != "both" else 1  # second row only when 'both'
                col = i
                ax_com = axes[row, col]
                im1 = ax_com.imshow(com_dmap_mean, cmap=color)
                ax_com.set_title(f"{ens.code} COM")
                set_labels(ax_com)
                cbar = fig.colorbar(im1, ax=ax_com, shrink=0.8)
                label = "1 / distance [1/nm]" if inverse else "distance [nm]"
                cbar.set_label(label)
                plotted_axes.append(ax_com)

        if not custom_axes:
            fig.tight_layout(pad=1.5)

        if save:
            # Save once (whole panel) or one file per protein; here I keep the whole panel.
            filename = f"dist_{distance_type.lower()}.png"
            fig.savefig(os.path.join(self.plot_dir, filename), dpi=dpi, bbox_inches="tight")
            msg = f"Distance maps saved to {self.plot_dir}/{filename}"
            logger.info(msg)
        return plotted_axes

    def _check_grid_input(self):
        ensembles = self.analysis.ensembles
        ens_lens = set([e.get_num_residues() for e in ensembles])
        if len(ens_lens) != 1:
            # May remove the limit in the future.
            raise ValueError(
                "Cannot build an histogram grid with proteins of different lengths"
            )
        min_len = min(ens_lens)  # Get the minimum number of residues.
        return min_len

    def plot_histogram_grid(self,
            feature: str = "ca_dist",
            ids: Union[np.ndarray, List[list]] = None,
            n_rows: int = 2,
            n_cols: int = 3,
            subplot_width: int = 2.0,
            subplot_height: int = 2.2,
            bins: Union[str, int] = None,
            dpi: int = 90,
            save: bool = False
        ) -> plt.Axes:
        """
        Plot a grid if histograms for distance or angular features. Can only be
        used when analyzing ensembles of proteins with same number of
        residues. The function will create a new matplotlib figure for histogram
        grid.

        Parameters
        ----------
        feature: str, optional
            Feature to analyze. Must be one of `ca_dist` (Ca-Ca distances),
            `a_angle` (alpha angles), `phi` or `psi` (phi or psi backbone
            angles).
        ids: Union[list, List[list]], optional
            Residue indices (integers starting from zero) to define the residues
            to analyze. For angular features it must be a 1d list with N indices
            of the residues. For distance features it must be 2d list/array of
            shape (N, 2) in which N is the number of residue pairs to analyze
            are 2 their indices. Each of the N indices (or pair of indices) will
            be plotted in an histogram of the grid. If this argument is not
            provided, random indices will be sampled, which is useful for
            quickly comparing the distance or angle distributions of multiple
            ensembles.
        n_rows: int, optional
            Number of rows in the histogram grid.
        n_cols: int, optional
            Number of columns in the histogram grid.
        subplot_width: int, optional
            Use to specify the Matplotlib width of the figure. The size of the
            figure will be calculated as: figsize = (n_cols*subplot_width, n_rows*subplot_height).
        subplot_height: int, optional
            See the subplot_width argument.
        bins: Union[str, int], optional
            Number of bins in all the histograms.
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save: bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.

        Returns
        -------
        ax: plt.Axes
            The Axes object for the histogram grid.
        """
        
        ### Check the ensembles.
        ensembles = self.analysis.ensembles
        min_len = self._check_grid_input()
        
        ### Select the features to analyze.
        n_hist = n_rows*n_cols
        if _get_max_plots_in_grid(min_len, feature) < n_hist:
            raise ValueError(f"Not enough residues to plot {n_hist} {feature} histograms")
        if ids is not None and n_hist != len(ids):
            raise ValueError(
                f"The number of provided ids ({len(ids)}) is incompatible with"
                f" the number of histograms ({n_hist})")
        if feature == "ca_dist":
            if ids is not None:
                rand_ids = _to_array(ids)
                if len(rand_ids.shape) != 2 or rand_ids.shape[1] != 2:
                    raise ValueError(
                        "Invalid shape for residue ids for Ca-Ca distances, received"
                        f" {tuple(rand_ids.shape)} expected ({n_hist}, 2)"
                    )
                if np.max(ids) + 1 > min_len:
                    raise ValueError(
                        f"Maximum residue idx ({np.max(ids)}) exceeds the number of"
                        f" residues ({min_len})"
                    )
            else:
                rand_ids = _get_random_pairs(n=n_hist, prot_len=min_len)
        elif feature == "a_angle":
            if ids is not None:
                rand_ids = _get_a_angle_ids(ids)
                if len(rand_ids.shape) != 2 or rand_ids.shape[1] != 4:
                    raise ValueError(
                        "Invalid shape for residue ids for a angles, received"
                        f" {tuple(rand_ids.shape)} expected ({n_hist}, )"
                    )
                if np.max(ids) + 1 > min_len - 3:
                    raise ValueError(
                        f"Maximum residue idx ({max(ids)}) exceeds the number of"
                        f" plottable alpha torsion angles ({min_len - 3})"
                    )
            else:
                rand_ids = _get_random_a_angle_ids(n=n_hist, prot_len=min_len)
        elif feature in ("phi", "psi"):
            if any([e.coarse_grained for e in ensembles]):
                raise ValueError(
                    f"Cannot analyze {feature} angles when a coarse-grained"
                    " ensemble is loaded."
                )
            if ids is not None:
                rand_ids = _to_array(ids)
                if len(rand_ids.shape) != 1:
                    raise ValueError(
                        f"Invalid shape for residue ids for {feature} angles, received"
                        f" {tuple(rand_ids.shape)} expected (*, )"
                    )
                if np.max(rand_ids) > min_len - _phi_psi_offsets[feature]:
                    raise ValueError(
                        f"Maximum residue idx ({max(rand_ids)}) exceeds the number of"
                        f" plottable {feature} angles for proteins with {min_len} residues"
                    )
                if feature == "phi" and 0 in rand_ids:
                    raise ValueError(f"Cannot use residue idx 0 with phi angles")
            else:
                rand_ids = np.random.choice(min_len-1, n_hist, replace=False) + _phi_psi_offsets[feature]
        else:
            raise KeyError(feature)
            
        if np.any(rand_ids < 0):
            raise ValueError("Can only use residue indices >= 0")

        ### Calculate features.
        hist_data = []
        for ensemble in ensembles:
            ca_indices = ensemble.trajectory.topology.select(ensemble.atom_selector)
            if feature == "ca_dist":
                data_k = mdtraj.compute_distances(ensemble.trajectory, ca_indices[rand_ids])
            elif feature == "a_angle":
                data_k = mdtraj.compute_dihedrals(ensemble.trajectory, ca_indices[rand_ids])
            elif feature in ("phi", "psi"):
                data_k = getattr(mdtraj, f"compute_{feature}")(ensemble.trajectory)[1]
                data_k = data_k[:,rand_ids - 1*_phi_psi_offsets[feature]]
            else:
                raise KeyError(feature)
            hist_data.append(data_k)
        
        ### Initialize the plot.
        # Initialize the figure.
        figsize = (n_cols*subplot_width, n_rows*subplot_height)
        fig = plt.figure(
            figsize=figsize,
            dpi=dpi,
            layout="constrained"
        )
        # Initialize the subplots.
        ax = fig.subplots(n_rows, n_cols, squeeze=False)
        # Figure elements.
        if feature == "ca_dist":
            axis_label = "Distance [nm]"
            title = r"C$\alpha$-C$\alpha$ distances"
        elif feature == "a_angle":
            axis_label = "Angle [rad]"
            title = r"$\alpha$ angles"
        elif feature in ("phi", "psi"):
            axis_label = "Angle [rad]"
            title = rf"$\{feature}$ angles"
        else:
            raise KeyError(feature)
        fig.suptitle(title)
        
        ### Plot the histograms.
        row_c = 0
        col_c = 0
        hist_args = {"histtype": "step", "density": True}
        labels = [e.code for e in ensembles]
        for m in range(n_hist):
            
            # Define variables to build the histograms.
            if feature in ("ca_dist", ):
                _min = min([x[:,m].min() for x in hist_data])
                _max = max([x[:,m].max() for x in hist_data])
                idx_i, idx_j = rand_ids[m]
                text = rf"C$\alpha$ {idx_i}-{idx_j}"
            elif feature in ("a_angle", ):
                _min = -np.pi
                _max = np.pi
                idx_i, idx_j, idx_k, idx_l = rand_ids[m]
                text = rf"C$\alpha$ {idx_i}-{idx_j}-{idx_k}-{idx_l}"
            elif feature in ("phi", "psi"):
                _min = -np.pi
                _max = np.pi
                text = rf"Residue {rand_ids[m]}"
            else:
                raise KeyError(feature)
                
            # Histogram.
            for k in range(len(ensembles)):
                data_km = hist_data[k][:,m]
                ax[row_c][col_c].hist(
                    data_km,
                    range=(_min, _max),
                    bins=bins,
                    label=ensembles[k].code if (row_c == 0 and col_c == 0) else None,
                    **hist_args
                )
                
            # Labels and titles.
            default_font_size = plt.rcParams['font.size']
            ax[row_c][col_c].set_title(text, fontsize=default_font_size)
            # ax[row_c][col_c].text(0.95, 0.95, text, verticalalignment='top',
            #                       horizontalalignment='right',
            #                       transform=ax[row_c][col_c].transAxes, fontsize=8,
            #                       color='black', alpha=0.8)

            if col_c == 0:
                ax[row_c][col_c].set_ylabel("Density")
            if row_c + 1 == n_rows:
                ax[row_c][col_c].set_xlabel(axis_label)
                
            # Increase row and column counters.
            col_c += 1
            if col_c == n_cols:
                row_c += 1
                col_c = 0

        # Legend.
        handles, labels = ax[0, 0].get_legend_handles_labels()
        fig.legend(
            handles, labels,
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            bbox_transform=ax[0, n_cols-1].transAxes
        )

        if save:
            plt.savefig(os.path.join(self.plot_dir, 'hist_grid_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches="tight")
            msg = f"Saved histogram grid to {self.plot_dir}/hist_grid_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def plot_rama_grid(self,
            ids: Union[np.ndarray, List[list]] = None,
            n_rows: int = 2,
            n_cols: int = 3,
            subplot_width: int = 2.0,
            subplot_height: int = 2.2,
            dpi: int = 90, 
            save: bool = False
        ) -> plt.Axes:
        """
        Plot a grid if Ramachandran plots for different residues. Can only be
        be used when analyzing ensembles of proteins with same number of
        residues. The function will create a new matplotlib figure for the
        scatter plot grid.

        Parameters
        ----------
        ids: Union[list, List[list]], optional
            Residue indices (integers starting from zero) to define the residues
            to analyze. For angular features it must be a 1d list with N indices
            of the residues. Each of the N indices will be plotted in an scatter
            plot in the grid. If this argument is not provided, random indices
            will be sampled, which is useful for quickly comparing features of
            multiple ensembles.
        n_rows: int, optional
            Number of rows in the scatter grid.
        n_cols: int, optional
            Number of columns in the scatter grid.
        subplot_width: int, optional
            Use to specify the Matplotlib width of the figure. The size of the
            figure will be calculated as: figsize = (n_cols*subplot_width, n_rows*subplot_height).
        subplot_height: int, optional
            See the subplot_width argument.
        dpi: int, optional
            The DPI (dots per inch) of the output figure. Default is 96.
        save : bool, optional
            If True, the plot will be saved as an image file in the specified directory. Default is False.


        Returns
        -------
        ax: plt.Axes
            The Axes object for the scatter plot grid.
        """
        
        ### Check the ensembles.
        ensembles = self.analysis.ensembles
        min_len = self._check_grid_input()
        if self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")
        
        ### Select the features to analyze.
        n_plots = n_rows*n_cols
        if _get_max_plots_in_grid(min_len, "rama") < n_plots:
            raise ValueError(
                f"Not enough residues to make {n_plots} Ramachandran plots"
            )
        if ids is not None and n_plots != len(ids):
            raise ValueError(
                f"The number of provided ids ({len(ids)}) is incompatible with"
                f" the number of scatter plots ({n_plots})")
        if any([e.coarse_grained for e in ensembles]):
            raise ValueError(
                f"Cannot analyze rama angles when a coarse-grained"
                " ensemble is loaded."
            )
        if ids is not None:
            rand_ids = _to_array(ids)
            if len(rand_ids.shape) != 1:
                raise ValueError(
                    f"Invalid shape for residue ids for Ramachandran plots,"
                    f" received {tuple(rand_ids.shape)} expected (*, )"
                )
            if np.max(rand_ids) > min_len - 2:
                raise ValueError(
                    f"Maximum residue idx ({max(rand_ids)}) exceeds the number of"
                    f" plottable rama angles for proteins with {min_len} residues"
                )
            if 0 in rand_ids:
                raise ValueError(f"Cannot use residue idx 0 with phi angles")
        else:
            rand_ids = np.random.choice(min_len - 2, n_plots, replace=False) + 1
            
        if np.any(rand_ids < 0):
            raise ValueError("Can only use residue indices >= 0")

        ### Calculate features.
        plot_data = []
        for ensemble in ensembles:
            # We end up with L-2 Ramachandran plots. We slice on axis=1
            # to pair phi and psi angles of the same residues.
            data_k = ensemble.get_features("phi_psi", ravel=False)
            # Here we use -1 because phi-psi pairs start from the second
            # residue.
            data_k = data_k[:,rand_ids - 1,:]
            plot_data.append(data_k)
        
        ### Initialize the plot.
        # Initialize the figure.
        figsize = (n_cols*subplot_width, n_rows*subplot_height)
        fig = plt.figure(
            figsize=figsize,
            dpi=dpi,
            layout="constrained"
        )
        # Initialize the subplots.
        ax = fig.subplots(n_rows, n_cols, squeeze=False)
        # Figure elements.
        x_label = "phi [rad]"
        y_label = "psi [rad]"
        title = f"Ramachandran plots"
        fig.suptitle(title)
        
        ### Plot the histograms.
        row_c = 0
        col_c = 0
        # hist_args = {"histtype": "step", "density": True}
        hist_args = {}
        labels = [e.code for e in ensembles]
        for m in range(n_plots):
            
            # Define variables to build the histograms.
            ax[row_c][col_c].set_xlim(-np.pi, np.pi)
            ax[row_c][col_c].set_ylim(-np.pi, np.pi)
            text = rf"Residue {rand_ids[m]}"
                
            # Histogram.
            for k in range(len(ensembles)):
                data_km = plot_data[k][:,m]
                ax[row_c][col_c].scatter(
                    data_km[:,0],
                    data_km[:,1],
                    label=ensembles[k].code if (row_c == 0 and col_c == 0) else None,
                    marker=".",
                    **hist_args
                )
                
            # Labels and titles.
            default_font_size = plt.rcParams['font.size']
            ax[row_c][col_c].set_title(text, fontsize=default_font_size)

            if col_c == 0:
                ax[row_c][col_c].set_ylabel(y_label)
            if row_c + 1 == n_rows:
                ax[row_c][col_c].set_xlabel(x_label)
                
            # Increase row and column counters.
            col_c += 1
            if col_c == n_cols:
                row_c += 1
                col_c = 0

        # Legend.
        handles, labels = ax[0, 0].get_legend_handles_labels()
        fig.legend(
            handles, labels,
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            bbox_transform=ax[0, n_cols-1].transAxes
        )
        
        if save:
            plt.savefig(os.path.join(self.plot_dir, 'rama_grid_' + self.analysis.ens_codes[0]), dpi=dpi, bbox_inches="tight")
            msg = f"Saved Ramachandran grid to {self.plot_dir}/rama_grid_{self.analysis.ens_codes[0]}.png"
            logger.info(msg)
        return ax

    def comparison_matrix(self,
            score: str,
            featurization_params: dict = {},
            bootstrap_iters: int = None,
            bootstrap_frac: float = 1.0,
            bootstrap_replace: bool = True,
            confidence_level: float = 0.95,
            significance_level: float = 0.05,
            bins: Union[int, str] = 50,
            random_seed: int = None,
            verbose: bool = False,
            ax: Union[None, plt.Axes] = None,
            figsize: Tuple[int] = (6.00, 5.0),
            dpi: int = 100,
            cmap: str = "viridis_r",
            title: str = None,
            cbar_label: str = None,
            textcolors: Union[str, tuple] = ("black", "white")
        ) -> dict:
        """
        Generates and visualizes the pairwise comparison matrix for the ensembles.
        This function computes the comparison matrix using the specified score
        type and feature. It then visualizes the matrix using a heatmap.

        Parameters:
        -----------
        score, featurization_params, bootstrap_iters, bootstrap_frac,
        bootstrap_replace, bins, random_seed, verbose:
            See the documentation of `EnsembleAnalysis.comparison_scores` for
            more information about these arguments.
        ax: Union[None, plt.Axes], optional
            Axes object where to plot the comparison heatmap. If `None` (the
            default value) is provided, a new Figure will be created.
        figsize: Tuple[int], optional
            The size of the figure for the heatmap. Default is (6.00, 5.0). Only
            takes effect if `ax` is not `None`.
        dpi: int, optional
            DPIs of the figure for the heatmap. Default is 100. Only takes
            effect if `ax` is not `None`.
        confidence_level, significance_level, cmap, title, cbar_label,
        textcolors:
            See the documentation of `dpet.visualization.plot_comparison_matrix`
            for more information about these arguments.

        Returns:
        --------
        results: dict
            A dictionary containing the following keys:
                `ax`: the Axes object with the comparison matrix heatmap.
                `scores`: comparison matrix. See `EnsembleAnalysis.comparison_scores`
                    for more information.
                `codes`: codes of the ensembles that were compared.
                `fig`: Figure object, only returned when a new figure is created
                    inside this function.

        Notes:
        ------
        The comparison matrix is annotated with the scores, and the axes are
        labeled with the ensemble labels.

        """

        ### Check input.
        if score == "ramaJSD" and self.analysis.exists_coarse_grained():
            raise ValueError("This analysis is not possible with coarse-grained models.")

        ### Score divergences.
        score_type, feature = scores_data[score]

        codes = [e.code for e in self.analysis.ensembles]
        comparison_out = self.analysis.comparison_scores(
            score=score,
            featurization_params=featurization_params,
            bootstrap_iters=bootstrap_iters,
            bootstrap_frac=bootstrap_frac,
            bootstrap_replace=bootstrap_replace,
            bins=bins,
            random_seed=random_seed,
            verbose=verbose
        )

        ### Setup the plot.
        # Axes.
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        else:
            fig = None
        # Title.
        if title is None:
            if score_type == "jsd":
                if feature == "ca_dist":
                    title = "adaJSD"
                elif feature == "alpha_angle":
                    title = "ataJSD"
                elif feature == "rama":
                    title = "ramaJSD"
                else:
                    title = f"{score_type.upper()} based on {feature}"
            else:
                raise ValueError(score_type)
        # Colorbar label.
        if cbar_label is None:
            cbar_label = f"{score_type.upper()} score"

        ### Actually plots.
        plot_comparison_matrix(
            ax=ax,
            comparison_out=comparison_out,
            codes=codes,
            confidence_level=confidence_level,
            significance_level=significance_level,
            cmap=cmap,
            title=title,
            cbar_label=cbar_label,
            textcolors=textcolors
        )

        ### Return results.
        results = {"ax": ax, "comparison": comparison_out, "codes": codes}
        if fig is not None:
            results["fig"] = fig
        return results