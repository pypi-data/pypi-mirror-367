import numpy as np
import scanpy as sc
import anndata as ad
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt 
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, ArrowStyle


def mclust_R(adata, num_cluster, modelNames='EEE', used_obsm='embedding', random_seed=666):
    """\
    Clustering using the mclust algorithm.
    The parameters are the same as those in the R package mclust.
    """

    np.random.seed(random_seed)
    import rpy2
    import rpy2.robjects as robjects
    robjects.r.library("mclust")

    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    r_random_seed = robjects.r['set.seed']
    r_random_seed(random_seed)
    rmclust = robjects.r['Mclust']

    res = rmclust(adata.obsm[used_obsm], num_cluster, modelNames)
    mclust_res = np.array(res[-2])

    adata.obs['mclust'] = mclust_res
    adata.obs['mclust'] = adata.obs['mclust'].astype('int')
    adata.obs['mclust'] = adata.obs['mclust'].astype('category')
    return adata

def mclust_init(emb, num_clusters, modelNames='EEE', random_seed=2024):
    """\
    Clustering using the mclust algorithm.
    The parameters are the same as those in the R package mclust.
    """

    np.random.seed(random_seed)
    import rpy2
    import rpy2.robjects as robjects
    robjects.r.library("mclust")

    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    r_random_seed = robjects.r['set.seed']
    r_random_seed(random_seed)
    rmclust = robjects.r['Mclust']

    res = rmclust(emb, num_clusters, modelNames)
    #res = mclustpy(emb, G=num_clusters)
    
    mclust_res = np.array(res[-2])

    return mclust_res


def get_signifcant_node(adata,result_LR, nei_adj,coord,p_val_cutoff,type = 'weight',topk = 2):
    LRs = list(result_LR.keys())
    gene_cell_pd = pd.DataFrame(data = adata.X.T, index = adata.var.index, columns = adata.obs.index)
    sample_lst = []# node
    interccc_lst = []#scores
    pscore_lst = []#pvalue
    sender_lst = []# sender
    sender_x_lst = []
    sender_y_lst = []
    receiver_x_lst = []# the central node
    receiver_y_lst = []
    lrp_lst = []
    for i in range(len(LRs)):
        p_i = result_LR[LRs[i]]['score_strength'].iloc[:,1]# strength
        s_i = result_LR[LRs[i]]['score_strength'].iloc[:,0]# score
        index_i = np.where(p_i < p_val_cutoff)[0].tolist() # the significant central nodes
        if len(index_i) > 0 :
            if type == 'weight':
                att = result_LR[LRs[i]]['inter_att'] # use attention
                #or attention*ligands?
            else:
                att0 = result_LR[LRs[i]]['inter_att']
                # associated with ligands, multiply the expression of ligands
                lr_l = LRs[i].split('-')[0]
                data_l_all = gene_cell_pd.loc[lr_l].values
                data_l = np.zeros(att0.shape)
                for k in range(att0.shape[0]):
                    data_l[k,:] = data_l_all[nei_adj[k,:]]
                att = att0*data_l
            
            # return the top k positions for each significant cells
            for j in range(len(index_i)):
                row_np = nei_adj[index_i[j],:]
                data_np = att.iloc[index_i[j],:]
                sorted_idj = np.argsort( -data_np )[:topk]# from large to small
                tmp_idj = row_np[ sorted_idj ]# top k senders
                sample_name = p_i.index.tolist()[index_i[j]]
                pscore = p_i[index_i[j]]
                interccc = s_i[index_i[j]]
                sender = tmp_idj
                sender_x = coord.iloc[sender]['x']
                sender_y = coord.iloc[sender]['y']
                receiver_x = coord.iloc[index_i[j]]['x']
                receiver_y = coord.iloc[index_i[j]]['y']
                LR_name = LRs[i]
                
                if topk > 1:
                    sample_name = [sample_name] * topk
                    interccc = [interccc]* topk
                    pscore = [pscore]* topk
                    receiver_x = [receiver_x]* topk
                    receiver_y = [receiver_y]* topk
                    LR_name = [LR_name]* topk
                sample_lst.extend(sample_name)
                interccc_lst.extend(interccc)
                pscore_lst.extend(pscore)
                sender_lst.extend(sender.tolist())
                sender_x_lst.extend(sender_x)
                sender_y_lst.extend(sender_y)
                receiver_x_lst.extend(receiver_x)
                receiver_y_lst.extend(receiver_y)
                lrp_lst.extend(LR_name)
                
    res_df = pd.DataFrame({
        'Sample_Name': sample_lst,
        'LR_Name': lrp_lst,
        'Comm_Score': interccc_lst,
        'P_Score': pscore_lst,
        'Sender': sender_lst,
        'Sender_x': sender_x_lst,
        'Sender_y': sender_y_lst,
        'Receiver_x': receiver_x_lst,
        'Receiver_y': receiver_y_lst
    })
    return res_df


def rank_LR_cell_type(result, type_record, type_name, nei_adj, p_value_cutoff):
    k = nei_adj.shape[1]
    LRPs = list(result.keys())
    type_num = np.zeros((len(LRPs),len(type_name))) # record the number count
    for i in range(len(LRPs)):
        result_i_strength = result[LRPs[i]]['score_strength'].iloc[:,1]# strength
        inter_att = result[LRPs[i]]['inter_att'].to_numpy()
        # detect the significant ones
        id_spots = np.where(result_i_strength < p_value_cutoff)[0] # just focus on the significant position
        if len(id_spots) > 0:
            for j in range(len(id_spots)): # each one
                index_j = type_record[id_spots[j]] # k*type_name
                # select neighbors, whose att is high
                id_j = np.where(inter_att[id_spots[j],:] > 1/k)[0]
                # focuse on the type name of id_j
                for t in range(len(id_j)): 
                    # detect nonzero index
                    index_t = np.where(index_j[id_j[t],:] == 1)[0][0]
                    type_num[i,index_t] = type_num[i,index_t] + 1 
    type_num_pd = pd.DataFrame(type_num, index = LRPs, columns = type_name)
    return type_num_pd
