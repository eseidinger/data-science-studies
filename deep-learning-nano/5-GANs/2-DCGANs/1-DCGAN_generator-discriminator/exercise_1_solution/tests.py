import torch
import torch.nn as nn


def check_discriminator(model: nn.Module, image_res: int):
    batch_size = 16
    model_input = torch.randn(batch_size, 3, image_res, image_res)
    assert model(model_input).shape == torch.Size([batch_size, 1]), \
        'Your model should output a single score for each element in the batch'
    print('Congrats, you successfully implemented your discriminator')


def check_generator(model: nn.Module, latent_dim: int, image_res: int):
    batch_size = 16
    model_input = torch.randn(batch_size, latent_dim, 1, 1)
    assert model(model_input).shape == torch.Size([batch_size, 3, image_res, image_res]), \
        'Your model should output a single score for each element in the batch'
    print('Congrats, you successfully implemented your discriminator')
