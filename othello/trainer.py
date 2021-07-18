import torch

import numpy as np

from loss import alpha_go_zero_loss

def run_train(net, optimizer, memory, batch_size):

    if len(memory) < batch_size:
        return

    device = net.get_device()

    batch = memory.sample(batch_size)

    s = np.array([b.s for b in batch])
    pi = np.array([b.pi for b in batch])
    z = np.array([b.z for b in batch])

    s = torch.from_numpy(s).to(device, dtype=torch.float)
    pi = torch.from_numpy(pi).to(device, dtype=torch.float)
    z = torch.from_numpy(z).to(device, dtype=torch.float)

    p, v = net.forward(s)

    loss = alpha_go_zero_loss(p, v, pi, z)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
