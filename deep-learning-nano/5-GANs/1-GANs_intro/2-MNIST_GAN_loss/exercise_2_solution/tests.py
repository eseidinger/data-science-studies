from typing import Callable

import torch


def check_real_loss(loss_function: Callable):
    D_out = torch.tensor([[-0.6136], [ 0.0316], [-0.4927], [ 0.2484], [ 0.4397], [ 0.1124], [ 0.6408], [ 0.4412]])
    loss_value = loss_function(D_out)
    assert torch.equal(loss_value, torch.tensor(0.66570544)), 'The real loss calculation is not correct'
    print('Congrats, you successfully implemented the real loss function')
    loss_value = loss_function(D_out, smooth=True)
    assert torch.equal(loss_value, torch.tensor(0.675803)), 'The real loss calculation with smoothing is not correct'
    print('Congrats, you successfully implemented the real loss function with smoothing')   

    
def check_fake_loss(loss_function: Callable):
    D_out = torch.tensor([[-0.6136], [ 0.0316], [-0.4927], [ 0.2484], [ 0.4397], [ 0.1124], [ 0.6408], [ 0.4412]])
    loss_value = loss_function(D_out)
    assert torch.equal(loss_value, torch.tensor(0.7666805)), 'The fake loss calculation is not correct'
    print('Congrats, you successfully implemented the fake loss function')
 