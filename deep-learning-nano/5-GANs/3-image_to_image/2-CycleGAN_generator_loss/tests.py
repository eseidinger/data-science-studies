from typing import Callable 

import torch
import torch.nn as nn


def check_cycle_generator(generator: nn.Module):
    image = torch.randn(1, 3, 128, 128)
    output = generator(image)
    assert image.shape == output.shape, \
        f'Expected output shape {image.shape}, received {output.shape}'
    print('Congrats, you successfully implemented a CycleGan generator!')

    
def check_losses(real_mse_loss: Callable, 
                 fake_mse_loss: Callable, 
                 cycle_consistency_loss: Callable):
    D_out = torch.tensor([[-0.8577]])
    
    output = real_mse_loss(D_out)
    expected_output = torch.tensor(3.4510493)
    assert torch.equal(expected_output, output), \
        'The real mse loss implementation is incorrect'
    
    output = fake_mse_loss(D_out)
    expected_output = torch.tensor(0.7356493)
    assert torch.equal(expected_output, output), \
        'The fake mse loss implementation is incorrect'    
    
    real_im = torch.randn(1, 3, 128, 128)
    reconstructed_im = torch.randn(1, 3, 128, 128)
    lambda_weight = torch.tensor(0.8, dtype=torch.float32)
    output = cycle_consistency_loss(real_im, reconstructed_im, lambda_weight)
    print('Congratulations, you successfully implemented CycleGan losses!')
    