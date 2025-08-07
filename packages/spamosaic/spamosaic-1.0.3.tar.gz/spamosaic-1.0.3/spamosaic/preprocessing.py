from typing import Optional
import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '3'
import sklearn
import anndata
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse
import sklearn.decomposition
import sklearn.feature_extraction.text
import sklearn.neighbors
import sklearn.preprocessing
import sklearn.utils.extmath
from harmony import harmonize

from spamosaic.utils import split_adata_ob

def sparse_log1p_scale(X, scale=1e4):
    """
    Apply log1p transformation to sparse or dense matrix, scaled by a factor.

    Parameters
    ----------
    X : Union[scipy.sparse.spmatrix, np.ndarray]
        Input expression matrix.
    scale : float, default=1e4
        Scaling factor applied before log1p.

    Returns
    -------
    Transformed matrix (same type as input)
    """
    if scipy.sparse.issparse(X):
        X = X.copy()
        X.data = np.log1p(X.data * scale)
        return X
    else:
        return np.log1p(X * scale)

class tfidfTransformer:
    """
    TF-IDF Transformer for sparse count data.
    """
    def __init__(self):
        self.idf = None
        self.fitted = False

    def fit(self, X):
        """
        Compute IDF vector from input data.

        Parameters
        ----------
        X : array-like or sparse matrix
            Count matrix.
        """
        self.idf = X.shape[0] / (1e-8+X.sum(axis=0))
        self.fitted = True

    def transform(self, X):
        """
        Apply TF-IDF transformation using precomputed IDF.

        Parameters
        ----------
        X : array-like or sparse matrix
            Count matrix to transform.

        Returns
        -------
        Transformed matrix.
        """
        if not self.fitted:
            raise RuntimeError("Transformer was not fitted on any data")
        if scipy.sparse.issparse(X):
            tf = X.multiply(1 / (1e-8+X.sum(axis=1)))
            return tf.multiply(self.idf)
        else:
            tf = X / (1e-8+X.sum(axis=1, keepdims=True))
            return tf * self.idf

    def fit_transform(self, X):
        """
        Fit to data, then transform it.

        Parameters
        ----------
        X : array-like or sparse matrix

        Returns
        -------
        Transformed matrix.
        """
        self.fit(X)
        return self.transform(X)

# optional, other reasonable preprocessing steps also ok
class lsiTransformer:
    """
    Latent Semantic Indexing (LSI) pipeline for dimensionality reduction.

    Parameters
    ----------
    n_components : int
        Number of SVD components.
    drop_first : bool
        Whether to drop the first principal component.
    use_highly_variable : bool or None
        Whether to subset to highly variable features.
    log : bool
        Whether to apply log1p transformation.
    norm : bool
        Whether to normalize features.
    z_score : bool
        Whether to z-score features.
    tfidf : bool
        Whether to apply TF-IDF normalization.
    svd : bool
        Whether to apply SVD transformation.
    use_counts : bool
        Use `.layers['counts']` instead of `.X` for data.
    pcaAlgo : str
        SVD backend.
    """

    def __init__(
        self, n_components: int = 20, drop_first=True, use_highly_variable=None, log=True, norm=True, z_score=True,
        tfidf=True, svd=True, use_counts=False, pcaAlgo='arpack'
    ):  

        self.drop_first = drop_first
        self.n_components = n_components + drop_first
        self.use_highly_variable = use_highly_variable

        self.log = log
        self.norm = norm
        self.z_score = z_score
        self.svd = svd
        self.tfidf = tfidf
        self.use_counts = use_counts

        self.tfidfTransformer = tfidfTransformer()
        self.normalizer = sklearn.preprocessing.Normalizer(norm="l1")
        self.pcaTransformer = sklearn.decomposition.TruncatedSVD(
            n_components=self.n_components, random_state=777, algorithm=pcaAlgo
        )
        self.fitted = None

    def fit(self, adata: anndata.AnnData):
        """
        Fit the transformer on AnnData object.
        """
        if self.use_highly_variable is None:
            self.use_highly_variable = "highly_variable" in adata.var
        adata_use = (
            adata[:, adata.var["highly_variable"]]
            if self.use_highly_variable
            else adata
        )
        if self.use_counts:
            X = adata_use.layers['counts']
        else:
            X = adata_use.X
        if self.tfidf:
            X = self.tfidfTransformer.fit_transform(X)
        # if scipy.sparse.issparse(X):
        #     X = X.A.astype("float32")
        if self.norm:
            X = self.normalizer.fit_transform(X)
        if self.log:
            # X = np.log1p(X * 1e4)    # L1-norm and target_sum=1e4 and log1p
            X = sparse_log1p_scale(X, 1e4)
        self.pcaTransformer.fit(X)
        self.fitted = True

    def transform(self, adata):
        """
        Transform AnnData using fitted transformer.
        """
        if not self.fitted:
            raise RuntimeError("Transformer was not fitted on any data")
        adata_use = (
            adata[:, adata.var["highly_variable"]]
            if self.use_highly_variable
            else adata
        )
        if self.use_counts:
            X_pp = adata_use.layers['counts']
        else:
            X_pp = adata_use.X
        if self.tfidf:
            X_pp = self.tfidfTransformer.transform(X_pp)
        # if scipy.sparse.issparse(X_pp):
        #     X_pp = X_pp.A.astype("float32")
        if self.norm:
            X_pp = self.normalizer.transform(X_pp)
        if self.log:
            # X_pp = np.log1p(X_pp * 1e4)
            X_pp = sparse_log1p_scale(X_pp, 1e4)
        if self.svd:
            X_pp = self.pcaTransformer.transform(X_pp)
        if self.z_score:
            X_pp -= X_pp.mean(axis=1, keepdims=True)
            X_pp /= (1e-8+X_pp.std(axis=1, ddof=1, keepdims=True))
        pp_df = pd.DataFrame(X_pp, index=adata_use.obs_names).iloc[
            :, int(self.drop_first) :
        ]
        return pp_df

    def fit_transform(self, adata):
        """
        Fit and transform AnnData.
        """
        self.fit(adata)
        return self.transform(adata)
   
# CLR-normalization     
def clr_normalize(adata):
    """
    Perform centered log-ratio (CLR) normalization on count data.

    Parameters
    ----------
    adata : AnnData
        Input data with count matrix in `.X`.

    Returns
    -------
    adata : AnnData
        Normalized AnnData object.
    """
    def seurat_clr(x):
        s = np.sum(np.log1p(x[x > 0]))
        exp = np.exp(s / len(x))
        return np.log1p(x / exp)

    adata.X = np.apply_along_axis(
        seurat_clr, 1, (adata.X.A if scipy.sparse.issparse(adata.X) else np.array(adata.X))
    )
    # sc.pp.pca(adata, n_comps=min(50, adata.n_vars-1))
    return adata

def harmony(latent, batch_labels, use_gpu=True):
    """
    Batch correction using Harmony.

    Parameters
    ----------
    latent : np.ndarray
        Low-dimensional representation (e.g., PCA).
    batch_labels : list or array
        Corresponding batch annotations.
    use_gpu : bool, default=True
        Whether to use GPU acceleration.

    Returns
    -------
    np.ndarray
        Batch-corrected latent representation.
    """
    df_batches = pd.DataFrame(np.reshape(batch_labels, (-1, 1)), columns=['batch'])
    bc_latent = harmonize(
        latent, df_batches, batch_key="batch", use_gpu=use_gpu, verbose=True
    )
    return bc_latent

def RNA_preprocess(
        rna_ads, batch_corr=False, favor='adapted', n_hvg=5000, lognorm=True, 
        scale=False, n_comps=50, batch_key='src', key='dimred_bc', return_hvf=False
    ):
    """
    Preprocessing pipeline for RNA modality.

    Parameters
    ----------
    rna_ads : list of AnnData
        RNA modality per batch.
    batch_corr : bool
        Whether to perform batch correction.
    favor : {'adapted', 'scanpy'}
        Which pipeline to use.
    n_hvg : int
        Number of highly variable genes.
    lognorm : bool
        Whether to apply log-normalization.
    scale : bool
        Whether to scale features.
    n_comps : int
        Number of output components.
    batch_key : str
        Key in `.obs` indicating batch identity.
    key : str
        Key to store result in `.obsm`.
    return_hvf : bool
        If True, return indices of selected HVGs.

    Returns
    -------
    If return_hvf is True, returns tuple of (gene names, indices).
    """

    measured_ads = [ad for ad in rna_ads if ad is not None]
    ad_concat = sc.concat(measured_ads)
    if favor=='scanpy':
        if lognorm:
            sc.pp.normalize_total(ad_concat, target_sum=1e4)
            sc.pp.log1p(ad_concat)
        if n_hvg:
            sc.pp.highly_variable_genes(ad_concat, n_top_genes=n_hvg, batch_key=batch_key)
            ad_concat = ad_concat[:, ad_concat.var.query('highly_variable').index.to_numpy()].copy()
        if scale: 
            sc.pp.scale(ad_concat)
        sc.pp.pca(ad_concat, n_comps=min(n_comps, ad_concat.n_vars-1))
        tmp_key = 'X_pca'
    else:
        n_hvg = n_hvg if n_hvg else ad_concat.shape[1]
        sc.pp.highly_variable_genes(ad_concat, flavor='seurat_v3', n_top_genes=n_hvg, batch_key=batch_key)
        transformer = lsiTransformer(
            n_components=n_comps, drop_first=False, log=True, norm=True, 
            z_score=True, tfidf=False, svd=True, pcaAlgo='arpack'
        )
        ad_concat.obsm['X_lsi'] = transformer.fit_transform(ad_concat[:, ad_concat.var.query('highly_variable').index.to_numpy()]).values
        tmp_key = 'X_lsi'
    
    if len(measured_ads) > 1 and batch_corr:
        ad_concat.obsm[key] = harmony(
            ad_concat.obsm[tmp_key], 
            ad_concat.obs[batch_key].to_list(), 
            use_gpu=True
        )
    else:
        ad_concat.obsm[key] = ad_concat.obsm[tmp_key]
    split_adata_ob([ad for ad in rna_ads if ad is not None], ad_concat, ob='obsm', key=key)

    if n_hvg and return_hvf:
        return ad_concat.var.query('highly_variable').index.to_numpy(), np.where(ad_concat.var['highly_variable'])[0]

def ADT_preprocess(
        adt_ads, batch_corr=False, favor='clr', lognorm=True, scale=False, 
        n_comps=50, batch_key='src', key='dimred_bc'
    ):
    """
    Preprocessing pipeline for ADT (protein) modality.

    Parameters
    ----------
    adt_ads : list of AnnData
        ADT modality per batch.
    batch_corr : bool
        Whether to perform batch correction.
    favor : {'clr', 'lognorm'}
        Whether to use CLR or log-normalization.
    lognorm : bool
        Apply log-normalization (if favor='lognorm').
    scale : bool
        Whether to scale features.
    n_comps : int
        Number of components for PCA.
    batch_key : str
        Key for batch annotation.
    key : str
        Key to store reduced dimension result.

    Returns
    -------
    None
    """

    measured_ads = [ad for ad in adt_ads if ad is not None]
    ad_concat = sc.concat(measured_ads)
    if favor=='clr':
        ad_concat = clr_normalize(ad_concat)
        # if scale: sc.pp.scale(ad_concat)
    else:
        if lognorm:
            sc.pp.normalize_total(ad_concat, target_sum=1e4)
            sc.pp.log1p(ad_concat)
        if scale: sc.pp.scale(ad_concat)
            
    sc.pp.pca(ad_concat, n_comps=min(n_comps, ad_concat.n_vars-1))

    if len(measured_ads) > 1 and batch_corr:
        ad_concat.obsm[key] = harmony(ad_concat.obsm['X_pca'], ad_concat.obs[batch_key].to_list(), use_gpu=True)
    else:
        ad_concat.obsm[key] = ad_concat.obsm['X_pca']
    split_adata_ob([ad for ad in adt_ads if ad is not None], ad_concat, ob='obsm', key=key)

def Epigenome_preprocess(
        epi_ads, batch_corr=False, n_peak=100000, 
        n_comps=50, batch_key='src', key='dimred_bc', return_hvf=False):
    """
    Preprocessing pipeline for epigenomic modality (e.g. ATAC-seq).

    Parameters
    ----------
    epi_ads : list of AnnData
        Epigenomic modality per batch.
    batch_corr : bool
        Whether to apply Harmony batch correction.
    n_peak : int
        Number of variable peaks to keep.
    n_comps : int
        Number of LSI components.
    batch_key : str
        Batch identifier key.
    key : str
        Output key in `.obsm`.
    return_hvf : bool
        Whether to return selected peak indices.

    Returns
    -------
    Optional[Tuple[np.ndarray, np.ndarray]]
        If return_hvf is True, returns names and indices of selected peaks.
    """
    
    measured_ads = [ad for ad in epi_ads if ad is not None]
    ad_concat = sc.concat(measured_ads)
    sc.pp.highly_variable_genes(ad_concat, flavor='seurat_v3', n_top_genes=n_peak, batch_key=batch_key)

    transformer = lsiTransformer(
        n_components=n_comps, drop_first=True, log=True, norm=True, 
        z_score=True, tfidf=True, svd=True, pcaAlgo='arpack'
    )
    ad_concat.obsm['X_lsi'] = transformer.fit_transform(ad_concat[:, ad_concat.var.query('highly_variable').index.to_numpy()]).values

    if len(measured_ads) > 1 and batch_corr:
        ad_concat.obsm[key] = harmony(ad_concat.obsm['X_lsi'], ad_concat.obs[batch_key].to_list(), use_gpu=True)
    else:
        ad_concat.obsm[key] = ad_concat.obsm['X_lsi']
    
    split_adata_ob([ad for ad in epi_ads if ad is not None], ad_concat, ob='obsm', key=key)

    if return_hvf:
        return ad_concat.var.query('highly_variable').index.to_numpy(), np.where(ad_concat.var['highly_variable'])[0]


