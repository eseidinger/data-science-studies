from typing import Callable

import torch


FAKE_LOGITS = torch.tensor([-0.2990,  1.6582,  0.0880, -0.2078,  0.1899,  1.9609,  0.1763,  0.9490,
                            -0.1863,  0.0479, -0.6072,  0.7648,  0.0189,  0.3165,  0.4645, -0.9585])

REAL_LOGITS = torch.tensor([-0.2219,  2.3058, -0.7330, -1.3858, -0.1590,  0.2727, -1.0026,  0.1778,
                            -0.3092,  1.1968,  1.4372,  1.2228,  1.3839, -0.7218,  1.5818, -1.1987])


def check_gen_w_loss(loss_fn: Callable):
    expected = torch.tensor(-0.2735)
    torch.testing.assert_close(loss_fn(FAKE_LOGITS), 
                               expected, 
                               atol=1e-4,
                               rtol=1e-4,
                               msg='There is something wrong with your implementation.')
    print('Congratulations, you successfully implemented the W-Loss for the generator')

    
def check_disc_w_loss(loss_fn: Callable):
    expected = torch.tensor(0.0331)
    torch.testing.assert_close(loss_fn(REAL_LOGITS, FAKE_LOGITS), 
                               expected, 
                               atol=1e-4,
                               rtol=1e-4,                          
                               msg='There is something wrong with your implementation.')
    print('Congratulations, you successfully implemented the W-Loss for the discriminator')