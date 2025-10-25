import torch
import torch.nn as nn


def check_apply_noise(layer: nn.Module):
    rand_input = torch.randn(1, layer.channels, 64, 64)
    
    # check parameters
    parameters = [p for p in layer.parameters()]
    assert len(parameters) == 1, 'Your layer should only have one parameter vector!'
    expected_shape = (1, layer.channels, 1, 1)
    assert parameters[0].shape[1] == layer.channels, \
        f'The scaling factor shape should be {expected_shape}. Received {parameters[0].shape}'
    assert torch.equal(torch.sum(parameters[0]), torch.tensor(0, dtype=torch.float32)), \
        'Your scaling factor is not zero initialized.'
    
    # forward pass
    output = layer(rand_input)  
    print('Congrats, you successfully implemented a noise injection layer!')
    

def check_adain(layer: nn.Module):
    image = torch.randn(1, layer.channels, 64, 64)
    noise = torch.randn(1, layer.w_dim)
    output = layer(image, noise)
    assert output.shape == image.shape, \
        f'Expected output shape {image.shape}. Received {output.shape}.'
    print('Congrats, you successfully implemented the AdaIN layer!')
