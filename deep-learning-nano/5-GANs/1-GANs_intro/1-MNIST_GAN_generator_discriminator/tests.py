import torch
from torch.nn import Module


def check_discriminator(model: Module, input_dim: int):
    batch_size = 16
    model_input = torch.randn(batch_size, input_dim)
    assert model(model_input).shape == torch.Size([batch_size, 1]), \
        'Your model should output a single score for each element in the batch'
    print('Congrats, you successfully implemented your discriminator')


def check_generator(model: Module, latent_dim: int, output_dim: int):
    batch_size = 16
    model_input = torch.randn(batch_size, latent_dim)
    assert model(model_input).shape == torch.Size([batch_size, output_dim]), \
        'Your model should output a single score for each element in the batch'
    print('Congrats, you successfully implemented your generator')
