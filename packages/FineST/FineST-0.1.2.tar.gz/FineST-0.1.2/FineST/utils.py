import numpy as np
import random
import pandas as pd
import torch
import scanpy as sc
from anndata import AnnData
import os
import sys
import logging
logging.getLogger().setLevel(logging.INFO)
from matplotlib.path import Path
import matplotlib.pyplot as plt
from skimage import draw, measure, io
import squidpy as sq
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import torch
import gc
import scanpy as sc
from scipy.spatial import cKDTree


## set the device
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"  
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


## set the random seed
def setup_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        print("CUDA is available. GPU:", torch.cuda.get_device_name(torch.cuda.current_device()))
    else:
        print("CUDA is not available. Using CPU.")


def map_subspot_to_nuclei(adata_subspot, adata_nuclei, 
                          inherit_uns_from="subspot", spatial_key="spatial"):
    """
    Map each subspot to its nearest nuclei and keep unique mappings.

    Parameters
    ----------
    adata_subspot : AnnData
        AnnData object containing subspot data (to be mapped).
    adata_nuclei : AnnData
        AnnData object containing nuclei data (reference).
    spatial_key : str
        Key in obsm for spatial coordinates.

    Returns
    -------
    adata_map : AnnData
        AnnData object with only the uniquely mapped subspots, 
        including spatial coordinates.
    """
    ## Build tree for nuclei coordinates, find nearest nuclei index for each subspot
    tree = cKDTree(adata_nuclei.obsm[spatial_key])
    _, closest_indices = tree.query(adata_subspot.obsm[spatial_key], k=1)
    
    ## Get the corresponding coordinates of mapped nuclei, Keep only unique mappings
    mapped_coords = adata_nuclei.obsm[spatial_key][closest_indices]
    _, unique_idx = np.unique(mapped_coords, axis=0, return_index=True)
    
    ## Construct new AnnData object with unique mappings
    adata_map = sc.AnnData(
        adata_subspot.X[unique_idx],
        var=adata_subspot.var.copy(),
        obs=adata_subspot.obs.iloc[unique_idx].copy()
    )
    adata_map.obsm[spatial_key] = mapped_coords[unique_idx]
    adata_map.var_names = adata_subspot.var_names

    # Copy .uns["spatial"]
    if inherit_uns_from == "subspot":
        adata_map.uns["spatial"] = adata_subspot.uns["spatial"].copy()
    elif inherit_uns_from == "nuclei":
        adata_map.uns["spatial"] = adata_nuclei.uns["spatial"].copy()
    else:
        raise ValueError("inherit_uns_from must be 'subspot' or 'nuclei'.")

    return adata_map


def list_gpu_tensors(scope_vars):
    """
    List all GPU tensors in the given scope.
    :param scope_vars: Use globals() or locals() to pass the variable dictionary.
    :return: [(variable_name, variable_object, size_in_MB, shape), ...], sorted by size descending.
    """
    results = []
    for name, var in scope_vars.items():
        if isinstance(var, torch.Tensor) and var.is_cuda:
            size_mb = var.element_size() * var.nelement() / 1024 / 1024  # in MB
            results.append((name, var, size_mb, tuple(var.shape)))
    return sorted(results, key=lambda x: -x[2])


def release_gpu_tensors(scope_vars):
    """
    Delete all GPU tensor variables in the given scope and free GPU memory.
    :param scope_vars: Use globals() or locals() to pass the variable dictionary.
    """
    gpu_tensors = list_gpu_tensors(scope_vars)
    if not gpu_tensors:
        print("No GPU tensors detected.")
        return
    print("Releasing the following GPU tensors:")
    for name, var, mb, shape in gpu_tensors:
        print(f"{name:20s}  {mb:.2f} MB  shape={shape}")
        scope_vars[name] = None  # Remove reference from the scope
        del var                  # Delete the variable
    gc.collect()
    torch.cuda.empty_cache()
    print("Released GPU memory occupied by the above variables.")


##################################
# 2025.07.04 For SSIM calculation
##################################
def vector2matrix(locs, cnts, shape):
    x_reconstructed = np.full(shape, np.nan)
    for loc, cnt in zip(locs, cnts):
        x_reconstructed[loc[0], loc[1]] = cnt
    return x_reconstructed

def count_rows_and_cols(locs):
    min_row, max_row = np.min(locs[:, 0]), np.max(locs[:, 0])
    min_col, max_col = np.min(locs[:, 1]), np.max(locs[:, 1])
    num_rows = max_row - min_row + 1
    num_cols = max_col - min_col + 1
    return (num_rows, num_cols)


def create_mask(polygon, shape):
    """
    Create a mask for the given shape
    Parameters:
        polygon : (N, 2) array, Points defining the shape.
        shape : tuple of two ints, Shape of the output mask.
    Returns: 
        mask : (shape[0], shape[1]) array, Boolean mask of the given shape.
    """
    polygon = polygon.iloc[:, -2:].values
    print("polygon: \n", polygon)
    polygon = np.clip(polygon, a_min=0, a_max=None)
    print("polygon adjusted: \n", polygon)
    ## Keep the order of x and y unchanged
    rr, cc = draw.polygon(polygon[:, 0], polygon[:, 1], shape) 
    # rr, cc = draw.polygon(polygon.iloc[:, -2], polygon.iloc[:, -1], shape) 

    ## Set negative coordinate to 0
    mask = np.zeros(shape, dtype=bool)
    mask[rr, cc] = True
    return mask, polygon


def crop_img_adata(roi_path, img_path, adata_path, crop_img_path, crop_adata_path, 
                   segment=False, save=None):
    """
    Crop an image and an AnnData object based on a region of interest.
    Parameters:
        roi_path : numpy.ndarray, A numpy array specifying the region of interest.
        img_path : str, The path to the image file.
        adata_path : str, The path to the AnnData file.
        crop_img_path : str, The path where the cropped image will be saved.
        crop_adata_path : str, The path where the cropped AnnData object will be saved.
        save: bool, optional, Default is None, which means not to save.
    Returns:
        tuple, A tuple containing the cropped image and the cropped AnnData object.
    """
    roi_coords = pd.read_csv(roi_path)
    print("ROI coordinates from napari package: \n", roi_coords)

    img = io.imread(img_path)
    print("img shape: \n", img.shape)

    ## Create a mask for the region of interest
    mask, roi_coords = create_mask(roi_coords, img.shape[:2])
    ## Find the bounding box of the region of interest
    props = measure.regionprops_table(mask.astype(int), properties=('bbox',))

    minr = props['bbox-0'][0]
    minc = props['bbox-1'][0]
    maxr = props['bbox-2'][0]
    maxc = props['bbox-3'][0]

    cropped_img = img[minr:maxr, minc:maxc]
    print("cropped_img shape: \n", cropped_img.shape)

    if save:
        io.imsave(crop_img_path, cropped_img)

    adata = sc.read_h5ad(adata_path)

    print("The adata: \n", adata)
    print("The range of original adata: \n", 
          [[adata.obsm["spatial"][:,0].min(), adata.obsm["spatial"][:,0].max()], 
           [adata.obsm["spatial"][:,1].min(), adata.obsm["spatial"][:,1].max()]])
    
    ## replace x and y of adata
    roi_yx = roi_coords[:, [1, 0]]   
    # roi_yx = np.stack([roi_coords.iloc[:, -1], roi_coords.iloc[:, -2]]).T
    adata_roi = adata[Path(roi_yx).contains_points(adata.obsm["spatial"]), :].copy()

    ## Update the 'spatial' field of the AnnData object
    ## if you no need segment, then it can be omitted.
    if segment:
        if roi_coords[2][0] == 0: 
            adata_roi.obsm["spatial"] = adata_roi.obsm["spatial"] - \
                                        np.array([roi_coords[0][1], 0])
        else: 
            adata_roi.obsm["spatial"] = adata_roi.obsm["spatial"] - \
                                        np.array([roi_coords[0][1], roi_coords[0][0]])
    if save:
        adata_roi.write(crop_adata_path)

    return cropped_img, adata_roi


def adata_nuclei_filter(adata_sp, img_path, whole_path, roi_path):
    coord_cell = adata_sp.uns['cell_locations']
    coord_cell = coord_cell.dropna()
    coord_cell.columns = ['pxl_row_in_fullres', 'pxl_col_in_fullres', 
                          'spot_index', 'cell_index', 'cell_nums']
    
    image = plt.imread(img_path)
    img = sq.im.ImageContainer(image)
    coord_image = pd.read_csv(whole_path)
    print("Coordinates from napari package: \n", coord_image)
    _, coord_image = create_mask(coord_image, img.shape[:2])

    ## adjust adata_sp.obsm["spatial"] using the cropped whole image coords
    if coord_image[2][0] == 0: 
        adata_sp.obsm["spatial"] = adata_sp.obsm["spatial"] + \
                                    np.array([coord_image[0][1], 0])
        coord_cell[['pxl_row_in_fullres', 'pxl_col_in_fullres']] += np.array([coord_image[0][1], 0])
    else: 
        adata_sp.obsm["spatial"] = adata_sp.obsm["spatial"] + \
                                    np.array([coord_image[0][1], coord_image[0][0]])
        coord_cell[['pxl_row_in_fullres', 'pxl_col_in_fullres']] += np.array([coord_image[0][1], coord_image[0][0]])
    print("adata_sp.obsm: spatial: \n", adata_sp.obsm["spatial"])

    ## select adata_sp.obsm["spatial"] using the cropped ROI image coords
    roi_coords = pd.read_csv(roi_path)
    print("ROI coordinates from napari package: \n", roi_coords)
    _, roi_coords = create_mask(roi_coords, img.shape[:2])
    roi_yx = roi_coords[:, [1, 0]]   
    ad_sp_crop = adata_sp[Path(roi_yx).contains_points(adata_sp.obsm["spatial"]), :].copy()

    ## filter
    ad_sp_crop.uns['cell_locations'] = (
        ad_sp_crop.uns['cell_locations']
        .loc[ad_sp_crop.uns['cell_locations'].spot_index.isin(ad_sp_crop.obs.index)]
        .reset_index(drop=True)
    )
    
    return ad_sp_crop, coord_image, coord_cell


def scale(cnts):
    """
    First performs column-wise scaling and then applies a global max scaling.
    Parameters:
        cnts (numpy.ndarray): A two-dimensional count matrix.
    Returns:
        numpy.ndarray: The scaled count matrix.
    """

    cnts = cnts.astype(np.float64)  # Convert to float to avoid integer division issues

    # ## Calculate the minimum and maximum values for each column
    # cnts_min = cnts.min(axis=0)
    # cnts_max = cnts.max(axis=0)

    # ## Apply Min-Max normalization to each column
    # # cnts -= cnts_min
    # # cnts /= (cnts_max - cnts_min) + 1e-12  
    # ## Apply column-wise scaling & global scaling to [0, 1]
    # cnts /= (cnts_max - cnts_min) + 1e-12  # Adding a small constant to avoid division by zero
    
    cnts /= cnts.max()

    return cnts


def configure_logging(logger_name):
    LOG_LEVEL = logging.DEBUG
    log_filename = logger_name+'.log'
    importer_logger = logging.getLogger('importer_logger')
    importer_logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=log_filename)
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)
    importer_logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(LOG_LEVEL)
    sh.setFormatter(formatter)
    importer_logger.addHandler(sh)
    return importer_logger


## set the logging
def setup_logger(model_save_folder):
        
    level =logging.INFO

    log_name = 'model.log'
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(model_save_folder + log_name)
    logger.setLevel(level)
    
    fileHandler = logging.FileHandler(os.path.join(model_save_folder, log_name), mode = 'a')
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    return logger


## define function
def reshape_latent_image(inputdata, dataset_class='Visium64'):   

    ## set ‘split_num’, according 'dataset_class'
    if dataset_class == 'Visium16':
        split_num = 16
    elif dataset_class == 'Visium64':
        split_num = 64
    elif dataset_class == 'VisiumSC':
        split_num = 1
    elif dataset_class == 'VisiumHD':
        split_num = 4
    else:
        raise ValueError('Invalid dataset_class. Only "Visium16", "Visium64", "VisiumSC" and "VisiumHD" are supported.')            

    ## [adata.shape[0]*256, 384]  -->  [adata.shape[0], 384]
    inputdata_reshaped = inputdata.view(int(inputdata.shape[0]/split_num), 
                                        split_num, inputdata.shape[1]) # [adata.shape[0], 256, 384]
    average_inputdata_reshaped = torch.sum(inputdata_reshaped, dim=1) / inputdata_reshaped.size(1)
    return inputdata_reshaped, average_inputdata_reshaped



class DatasetCreatImageBetweenSpot(torch.utils.data.Dataset):
    def __init__(self, image_paths, spatial_pos_path, dataset_class):
        self.spatial_pos_csv = pd.read_csv(spatial_pos_path, sep=",", header=None)
        
        ## Load .pth file
        self.images = []
        for image_path in image_paths:
            if image_path.endswith('.pth'):
                image_tensor = torch.load(image_path)
                self.images.extend(image_tensor)
        self.image_data = torch.stack(self.images)
        self.image_tensor = self.image_data.view(self.image_data.size(0), -1)  

        ## set ‘split_num’, according 'dataset_class'
        if dataset_class == 'Visium16':
            self.split_num = 16
        elif dataset_class == 'Visium64':
            self.split_num = 64
        elif dataset_class == 'VisiumSC':
            self.split_num = 1
        elif dataset_class == 'VisiumHD':
            self.split_num = 4
        else:
            raise ValueError('Invalid dataset_class. Only "Visium" and "VisiumHD" are supported.')
                
        print("Finished loading all files")

    def __getitem__(self, idx):
        item = {}
        v1 = self.spatial_pos_csv.loc[idx, 0]   
        v2 = self.spatial_pos_csv.loc[idx, 1]  
    
        ## Stack the tensors in the list along a new dimension  
        item['image'] = self.image_tensor[idx * self.split_num : (idx + 1) * self.split_num]    
        item['spatial_coords'] = [v1, v2]  

        return item

    def __len__(self):
        return len(self.spatial_pos_csv)
    

def subspot_coord_expr_adata(recon_mat_reshape_tensor, adata, gene_hv, patch_size=56, 
                             p=None, q=None, dataset_class=None):
    ## Extract x, y coordinates based on the type of `adata`
    def get_x_y(adata, p):
        if isinstance(adata, AnnData):
            return adata.obsm['spatial'][p][0], adata.obsm['spatial'][p][1]
        else:
            return adata[p][0], adata[p][1]

    NN = recon_mat_reshape_tensor.shape[1]
    N = int(np.sqrt(NN))  # Determine the grid size
    ################
    # IMPORTANT
    ################
    pixel_step = patch_size / (2*N)  # Calculate the half of pixel step size
    print('pixel_step (half of patch_size):', pixel_step)
    all_spot_all_variable = np.zeros((recon_mat_reshape_tensor.shape[0] * recon_mat_reshape_tensor.shape[1], 
                                      recon_mat_reshape_tensor.shape[2]))
    C2 = np.zeros((recon_mat_reshape_tensor.shape[0] * recon_mat_reshape_tensor.shape[1], 2), dtype=int)
    first_spot_first_variable = None

    ## Set `split_num` according to `dataset_class`
    if dataset_class == 'Visium16':
        split_num = 16
    elif dataset_class == 'Visium64':
        split_num = 64
    elif dataset_class == 'VisiumSC':
        split_num = 1
    elif dataset_class == 'VisiumHD':
        split_num = 4
    else:
        raise ValueError('Invalid dataset_class. Only "Visium16", '
                 '"Visium64", "VisiumSC" and "VisiumHD" are supported.')

    if p is None and q is None:

        if split_num not in [1, 4, 16, 64]:
            raise ValueError("split_num must be 1, 4, 16, or 64")
        
        for p_ in range(recon_mat_reshape_tensor.shape[0]):
            x, y = get_x_y(adata, p_)
            C = np.zeros((NN, 2), dtype=int)

            ##############################
            ## from left-down to right-up
            ##############################
            for k in range(1, split_num + 1):
                s = k % N
                if s == 0:
                    i = N
                    j = k // N
                else:
                    i = s
                    j = (k - i) // N + 1

                if split_num == 4:
                    C[k - 1, 0] = x - pixel_step + (i - 1) * (2*pixel_step)
                    C[k - 1, 1] = y - pixel_step + (j - 1) * (2*pixel_step)
                elif split_num == 16:
                    C[k - 1, 0] = x - pixel_step - 1 * (2*pixel_step) + (i - 1) * (2*pixel_step)
                    C[k - 1, 1] = y - pixel_step - 1 * (2*pixel_step) + (j - 1) * (2*pixel_step)
                elif split_num == 64:
                    C[k - 1, 0] = x - pixel_step - 3 * (2*pixel_step) + (i - 1) * (2*pixel_step)
                    C[k - 1, 1] = y - pixel_step - 3 * (2*pixel_step) + (j - 1) * (2*pixel_step)
                elif split_num == 1:
                    C[k - 1, 0] = x
                    C[k - 1, 1] = y

            C2[p_ * split_num:(p_ + 1) * split_num, :] = C

        for q_ in range(recon_mat_reshape_tensor.shape[2]):
            all_spot_all_variable[:, q_] = recon_mat_reshape_tensor[:, :, q_].flatten().cpu().detach().numpy()

    else:
        x, y = get_x_y(adata, p)

        ## Select the information of the pth spot and the qth variable
        first_spot_first_variable = recon_mat_reshape_tensor[p, :, q].cpu().detach().numpy()

        ## Initialize C as a zero matrix of integer type
        C = np.zeros((NN, 2), dtype=int)

        #########################################
        ## from left-up to right-down
        #########################################
        for k in range(1, split_num + 1):
            s = k % N
            if s == 0:
                i = N
                j = k // N
            else:
                i = s
                j = (k - i) // N + 1

            if split_num == 4:
                C[k - 1, 0] = x - pixel_step + (i - 1) * (2*pixel_step)
                C[k - 1, 1] = y - pixel_step + (j - 1) * (2*pixel_step)
            elif split_num == 16:
                C[k - 1, 0] = x - pixel_step - 1 * (2*pixel_step) + (i - 1) * (2*pixel_step)
                C[k - 1, 1] = y - pixel_step - 1 * (2*pixel_step) + (j - 1) * (2*pixel_step)
            elif split_num == 64:
                C[k - 1, 0] = x - pixel_step - 3 * (2*pixel_step) + (i - 1) * (2*pixel_step)
                C[k - 1, 1] = y - pixel_step - 3 * (2*pixel_step) + (j - 1) * (2*pixel_step)


    ## Establish new anndata in sub-spot level
    adata_spot = sc.AnnData(X=pd.DataFrame(all_spot_all_variable))
    adata_spot.var_names = gene_hv
    adata_spot.obs["x"] = C2[:, 0]
    adata_spot.obs["y"] = C2[:, 1]
    adata_spot.obsm['spatial'] = adata_spot.obs[["x", "y"]].values
    
    return first_spot_first_variable, C, all_spot_all_variable, C2, adata_spot