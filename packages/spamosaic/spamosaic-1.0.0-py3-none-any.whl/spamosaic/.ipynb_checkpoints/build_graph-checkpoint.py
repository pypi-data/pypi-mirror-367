import os, gc
import scipy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scanpy as sc
# import squidpy as sq
import pandas as pd
import h5py
import math
import sklearn
from tqdm import tqdm
import scipy.sparse as sps
import scipy.io as sio
import seaborn as sns
import warnings
import networkx as nx

from os.path import join
import torch
from collections import Counter
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.decomposition import PCA
from annoy import AnnoyIndex
from sklearn.preprocessing import normalize
from sklearn.ensemble import IsolationForest

import spamosaicv2.MNN as MNN

RAD_CUTOFF = 2000

## adapted from stagate
def Cal_Spatial_Net(adata, rad_cutoff=None, k_cutoff=None,
                    max_neigh=50, model='Radius', verbose=True):
    assert (model in ['Radius', 'KNN'])
    if verbose:
        print('------Calculating spatial graph...')
    coor = pd.DataFrame(adata.obsm['spatial'])
    coor.index = adata.obs.index
    coor.columns = ['imagerow', 'imagecol']

    nbrs = sklearn.neighbors.NearestNeighbors(
        n_neighbors=max_neigh + 1, algorithm='ball_tree').fit(coor)
    distances, indices = nbrs.kneighbors(coor)
    if model == 'KNN':
        indices = indices[:, 1:k_cutoff + 1]
        distances = distances[:, 1:k_cutoff + 1]
    if model == 'Radius':
        indices = indices[:, 1:]
        distances = distances[:, 1:]

    KNN_list = []
    for it in range(indices.shape[0]):
        KNN_list.append(pd.DataFrame(zip([it] * indices.shape[1], indices[it, :], distances[it, :])))
    KNN_df = pd.concat(KNN_list)
    KNN_df.columns = ['Cell1', 'Cell2', 'Distance']

    Spatial_Net = KNN_df.copy()
    if model == 'Radius':
        Spatial_Net = KNN_df.loc[KNN_df['Distance'] < rad_cutoff,]
    id_cell_trans = dict(zip(range(coor.shape[0]), np.array(coor.index), ))
    Spatial_Net['Cell1'] = Spatial_Net['Cell1'].map(id_cell_trans)
    Spatial_Net['Cell2'] = Spatial_Net['Cell2'].map(id_cell_trans)

    if verbose:
        print('The graph contains %d edges, %d cells.' % (Spatial_Net.shape[0], adata.n_obs))
        print('%.4f neighbors per cell on average.' % (Spatial_Net.shape[0] / adata.n_obs))
    adata.uns['Spatial_Net'] = Spatial_Net

    cells = np.array(adata.obs.index)
    cells_id_tran = dict(zip(cells, range(cells.shape[0])))
    if 'Spatial_Net' not in adata.uns.keys():
        raise ValueError("Spatial_Net is not existed! Run Cal_Spatial_Net first!")
        
    Spatial_Net = adata.uns['Spatial_Net']
    G_df = Spatial_Net.copy()
    G_df['Cell1'] = G_df['Cell1'].map(cells_id_tran)
    G_df['Cell2'] = G_df['Cell2'].map(cells_id_tran)
    G = sps.coo_matrix((np.ones(G_df.shape[0]), (G_df['Cell1'], G_df['Cell2'])), shape=(adata.n_obs, adata.n_obs))
    G = G + sps.eye(G.shape[0])  # self-loop
    adata.uns['adj'] = G

def build_intra_graph(ads, rad_cutoff, knns):
    for k, ad in zip(knns, ads):
        if ad is not None:
            Cal_Spatial_Net(ad, rad_cutoff=rad_cutoff, max_neigh=k)

def determine_kSize(adi, adj, knn_base, auto_thr):
    size_ratio = min(adi.n_obs, adj.n_obs) / max(adi.n_obs, adj.n_obs)
    if size_ratio >= auto_thr:
        return knn_base, knn_base
    
    if adi.n_obs > adj.n_obs:
        return max(1, int(knn_base * size_ratio)), knn_base
    else:
        return knn_base, max(1, int(knn_base * size_ratio))

def remove_outlier(mnn_set, ad1, ad2,  contamination='auto'):
    X_spatial_1 = ad1[[p[0] for p in mnn_set]].obsm['spatial']
    X_spatial_2 = ad2[[p[1] for p in mnn_set]].obsm['spatial']
    data = np.c_[X_spatial_1, X_spatial_2, X_spatial_1-X_spatial_2]

    clf = IsolationForest(max_samples='auto', contamination=contamination, random_state=0)
    y_outlier = clf.fit_predict(data)

    new_mnn_set = set()
    for p, y in zip(mnn_set, y_outlier):
        if y==1:
            new_mnn_set.add(p)
    
    return new_mnn_set

def build_mnn_graph(
        bridge_ads, test_ads, use_rep, batch_key,
        knn_base=10, auto_knn=False, auto_thr=0.8, 
        rmv_outlier=False, contamination='auto', seed=1234
    ):  # work within the same modality
    n_bridge_ad, n_test_ad = len(bridge_ads), len(test_ads)
    if n_bridge_ad == 0:
        n_ref = n_test_ad
        bridge_ads = test_ads
    else:
        n_ref = n_bridge_ad

    mnn_bridge_bridge, mnn_bridge_test = set(), set()
    for i in range(n_ref):
        for j in range(i+1, n_bridge_ad):
            adi, adj = bridge_ads[i], bridge_ads[j]
            if not auto_knn:
                knn1, knn2 = knn_base, knn_base
            else:
                knn1, knn2 = determine_kSize(adi, adj, knn_base, auto_thr)
            print(f"Finding MNN between ({adi.obs[batch_key][0]}, {adj.obs[batch_key][0]}) using KNN ({knn1}, {knn2})")

            mnn_set = MNN.mnn(
                adi.obsm[use_rep], adj.obsm[use_rep], 
                adi.obs_names, adj.obs_names, 
                knn1=knn1, knn2=knn2, approx = True, 
                way='annoy', metric='manhattan', norm=True
            )
            if rmv_outlier:
                n_mnn1 = len(mnn_set)
                mnn_set = remove_outlier(mnn_set, adi, adj, contamination)
                n_mnn2 = len(mnn_set)
                print(f'==> filter {n_mnn1-n_mnn2} from {n_mnn1} ({(n_mnn1-n_mnn2)/n_mnn1*100:.2f})%')
            mnn_bridge_bridge = mnn_bridge_bridge | mnn_set

        for j in range(n_test_ad):
            adi, adj = bridge_ads[i], test_ads[j]
            if not auto_knn:
                knn1, knn2 = knn_base, knn_base
            else:
                knn1, knn2 = determine_kSize(adi, adj, knn_base, auto_thr)
            print(f"Finding MNN between ({adi.obs[batch_key][0]}, {adj.obs[batch_key][0]}) using KNN ({knn1}, {knn2})")
            
            mnn_set = MNN.mnn(
                adi.obsm[use_rep], adj.obsm[use_rep], 
                adi.obs_names, adj.obs_names, 
                knn1=knn1, knn2=knn2, approx = True, 
                way='annoy', metric='manhattan', norm=True
            )
            if rmv_outlier:
                n_mnn1 = len(mnn_set)
                mnn_set = remove_outlier(mnn_set, adi, adj, contamination)
                n_mnn2 = len(mnn_set)
                print(f'==> filter {n_mnn1-n_mnn2} from {n_mnn1} ({(n_mnn1-n_mnn2)/n_mnn1*100:.2f})%')
            mnn_bridge_test = mnn_bridge_test | mnn_set
    concat_mnn = mnn_bridge_bridge | mnn_bridge_test
    return concat_mnn

def mergeGraph(ads, mnn_set, merge_graph=True, inter_weight=1., use_rep='X_pca'):  # make sure that obs_name unique
    # concat_ads = bridge_ads + test_ads
    concat_obs = pd.concat([ad.obs.copy() for ad in ads])
    concat_obsm = np.vstack([ad.obsm[use_rep] for ad in ads])
    ad_merge = sc.AnnData(np.zeros((len(concat_obs), 2)), obs=concat_obs, obsm={use_rep:concat_obsm})
    intra_graph = sps.block_diag((ad.uns['adj'] for ad in ads))  # coo matrix

    name2idx = dict(zip(ad_merge.obs_names, np.arange(ad_merge.n_obs)))
    idx2name = {v:k for k,v in name2idx.items()}
    if len(mnn_set)>0:
        mnn_ind1 = [name2idx[e[0]] for e in mnn_set]
        mnn_ind2 = [name2idx[e[1]] for e in mnn_set]
        symm_mnn_ind1 = np.hstack([mnn_ind1, mnn_ind2])
        symm_mnn_ind2 = np.hstack([mnn_ind2, mnn_ind1])
        inter_graph = sps.coo_matrix((np.ones(len(symm_mnn_ind1)), (symm_mnn_ind1, symm_mnn_ind2)), 
                                    shape=(ad_merge.n_obs, ad_merge.n_obs)) * inter_weight  # coo matrix
    else:
        inter_graph = sps.coo_matrix((ad_merge.n_obs, ad_merge.n_obs))
    ad_merge.uns['mnn_graph'] = inter_graph

    if merge_graph:  # for lgcn, gat
        ad_merge.uns['adj'] = (intra_graph + inter_graph).tocoo()
        ad_merge.uns['edgeList'] = (ad_merge.uns['adj'].row, ad_merge.uns['adj'].col)
        ad_merge.uns['edgeW'] = ad_merge.uns['adj'].data
    else:
        ad_merge.uns['adj'] = intra_graph
        ad_merge.uns['edgeList'] = (ad_merge.uns['adj'].row, ad_merge.uns['adj'].col)
        ad_merge.uns['edgeW'] = ad_merge.uns['adj'].data
        # ad_merge.uns['intra_edgeList'] = np.nonzero(ad_merge.uns['adj'])
        # ad_merge.uns['inter_edgeList'] = np.nonzero(ad_merge.uns['mnn_graph'])
    return ad_merge, idx2name