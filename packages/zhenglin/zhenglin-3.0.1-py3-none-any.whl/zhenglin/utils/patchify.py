import numpy as np
import cv2
import torch
from PIL import Image
from contextlib import contextmanager
from typing import Union

@contextmanager
def patchify(image: Union[np.ndarray, torch.Tensor], 
             patch_size: tuple = (128, 128), 
             overlap_width: int = 0, 
             blend_alpha: float = 0.5):
    '''Patchify an image into smaller patches with optional overlap and blending.
    
        Example usage:
        with patchify(image, patch_size=(128, 128)) as patches:
            for patch in patches:
                patch[i] = do_something(patch[i])

    '''

    assert not isinstance(image, Image.Image), "Input should be a NumPy array or a PyTorch tensor, not a PIL Image."

    is_tensor = isinstance(image, torch.Tensor)
    
    if is_tensor:
        b, c, h, w = image.shape
        ph, pw = patch_size
        
        patches = []
        original_image = image.clone()
        reconstructed_image = image.clone()
        
        rows = (h + ph - overlap_width - 1) // (ph - overlap_width)
        cols = (w + pw - overlap_width - 1) // (pw - overlap_width)
        
        for i in range(rows):
            for j in range(cols):
                y = i * (ph - overlap_width)
                x = j * (pw - overlap_width)
                
                patch = image[:, :, 
                    max(0, y):min(y + ph, h), 
                    max(0, x):min(x + pw, w)
                ]
                
                if patch.shape[2:] != patch_size:
                    patch = torch.nn.functional.interpolate(
                        patch.unsqueeze(0), 
                        size=patch_size, 
                        mode='bilinear', 
                        align_corners=False
                    )[0]
                
                patches.append(patch)
    
    else:
        if image.ndim == 2:
            image = np.stack([image]*3, axis=-1)
        
        h, w = image.shape[:2]
        ph, pw = patch_size
        
        patches = []
        original_image = image.copy()
        reconstructed_image = image.copy()
        
        rows = (h + ph - overlap_width - 1) // (ph - overlap_width)
        cols = (w + pw - overlap_width - 1) // (pw - overlap_width)
        
        for i in range(rows):
            for j in range(cols):
                y = i * (ph - overlap_width)
                x = j * (pw - overlap_width)
                
                patch = image[
                    max(0, y):min(y + ph, h), 
                    max(0, x):min(x + pw, w)
                ]
                
                if patch.shape[:2] != patch_size:
                    patch = cv2.resize(patch, patch_size)
                
                patches.append(patch)
    
    try:
        yield patches
    finally:
        if is_tensor:
            for idx, patch in enumerate(patches):
                row = idx // cols
                col = idx % cols
                
                y = row * (ph - overlap_width)
                x = col * (pw - overlap_width)
                
                y_start = max(0, y)
                x_start = max(0, x)
                y_end = min(y + ph, h)
                x_end = min(x + pw, w)
                
                orig_region = original_image[:, :, y_start:y_end, x_start:x_end]
                new_region = patch[:, :, :orig_region.shape[-2], :orig_region.shape[-1]]
                
                blended_region = (1 - blend_alpha) * orig_region + blend_alpha * new_region
                
                reconstructed_image[:, :, y_start:y_end, x_start:x_end] = blended_region
            
            image.data[:] = reconstructed_image
        else:
            for idx, patch in enumerate(patches):
                row = idx // cols
                col = idx % cols
                
                y = row * (ph - overlap_width)
                x = col * (pw - overlap_width)
                
                y_start = max(0, y)
                x_start = max(0, x)
                y_end = min(y + ph, h)
                x_end = min(x + pw, w)
                
                orig_region = original_image[y_start:y_end, x_start:x_end]
                new_region = patch[:orig_region.shape[0], :orig_region.shape[1]]
                
                min_h = min(orig_region.shape[0], new_region.shape[0])
                min_w = min(orig_region.shape[1], new_region.shape[1])
                
                orig_region = orig_region[:min_h, :min_w]
                new_region = new_region[:min_h, :min_w]
                
                blended_region = cv2.addWeighted(
                    orig_region, 1 - blend_alpha, 
                    new_region, blend_alpha, 0
                )
                
                reconstructed_image[y_start:y_start+min_h, x_start:x_start+min_w] = blended_region
            
            image[:] = reconstructed_image


if __name__ == '__main__':

    def process_patch(patch: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        if isinstance(patch, torch.Tensor):
            processed_patch = cv2.GaussianBlur(patch[0].cpu().numpy().transpose(1, 2, 0), (11, 11), 11)
            cv2.putText(processed_patch, 'Processed', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            processed_patch = torch.tensor(processed_patch).permute(2, 0, 1).unsqueeze(0)
            return processed_patch
        else:
            processed_patch = cv2.GaussianBlur(patch, (11, 11), 11)
            cv2.putText(processed_patch, 'Processed', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            return processed_patch

    # Example usage
    cv_image = cv2.imread(r'C:\Users\Lenovo\Desktop\validation\genga\1.png')
    with patchify(cv_image, patch_size=(128, 128)) as patches:
        for i in range(len(patches)):
            patches[i] = process_patch(patches[i])
    cv2.imwrite(r'C:\Users\Lenovo\Desktop\validation\genga\cv_processed.png', cv_image)

    torch_image = torch.rand(1, 3, 512, 512)
    with patchify(torch_image, patch_size=(128, 128)) as patches:
        for i in range(len(patches)):
            patches[i] = process_patch(patches[i])
    from torchvision.utils import save_image
    save_image(torch_image, r'C:\Users\Lenovo\Desktop\validation\genga\torch_processed.png')
