import numpy as np
import torch
import torch.nn as nn


def check_progan_generator(generator: nn.Module):
    resolutions = [4, 8, 16, 32, 64, 128, 256, 512]
    latent_vector = torch.randn(2, 128)
    for res in resolutions:
        print(f'Testing the generator at resolution {res}')
        output = generator(latent_vector, res, alpha=np.random.rand())
        width, height = output.shape[2], output.shape[3]
        assert width == res and height == res, \
            f'The output resolution is {width}x{height} but the expected resolution is {res}x{res}'
    print('You successfully implemented the generator of a ProGan model!')
