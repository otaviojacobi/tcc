import torch
import torch.nn.functional as F


def alpha_go_zero_loss(p, v, pi, z):
    """
    N -> replay_buffer_size
    p -> [N * [p0, p1, p2m ... p81]] -> N x a shaped tensor where for alhago zero a = 82 (othello = 64 + pass)
    v -> [N] -> N x 1 shaped tensor
    pi -> [N * [p0, p1, p2m ... p81]] -> N x a shaped tensor where for alhago zero a = 82 (othello = 64 + pass)
    z -> [N] -> N x 1 shaped tensor
    Note: Using softmax to solve the possible log(0) issue
    """

    value_error = (z - v) ** 2                      # shape is N, 1

    p = F.log_softmax(p, dim=-1)                    # shape is N, a

    policy_error = torch.sum(pi * p, dim=1)         # shape is N, 1

    return (value_error - policy_error).mean()        # shape is 1,1


def __test_loss():
    """
    This is a test function (playground) where the replay_buffer_size is 4 and the action space is 3 (instead of 82)
    """

    samples = [
        (0., [0.5, 0., 0.5], 1.),
        (0., [0., 1., 0.], -1.),
        (0., [0., 0., 1.], 1.),
        (0., [0.6, 0.1, 0.3], 1.)
    ]

    y_target = [(pi, r) for (_, pi, r) in samples]
    pi, z = list(zip(*y_target))

    pi = torch.tensor(pi)
    z = torch.tensor(z)

    p = torch.tensor([[0.5, 0., 0.5],
                      [0., 0., 0.],
                      [0., 0., 1.],
                      [0.6, 0.1, 0.3]])

    v = torch.tensor([1, -1, 1., 1.])

    loss = alpha_go_zero_loss(p, v, pi, z)
    print(loss)

__test_loss()