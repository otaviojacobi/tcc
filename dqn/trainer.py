import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter

import gym

from DQN import DQN
from ReplayMemory import ReplayMemory, Transition
from helpers import preprocess_image, shift_tensor

import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
writer = SummaryWriter()

if torch.cuda.is_available():
    print(f"Training on {torch.cuda.get_device_name(0)}")

def _init_state(observation, stack_frames):
    history = torch.zeros(stack_frames, 84, 84).to(device)
    state = preprocess_image(observation).squeeze(0)

    for k in range(stack_frames):
        history[k, :, :] = state.clone()

    return history

def _select_action(state, epsilon, action_space, policy_net):

    if random.random() < epsilon:
        return torch.tensor([[random.randrange(action_space)]], device=device, dtype=torch.long)
    else:
        with torch.no_grad():
            return policy_net(state.unsqueeze(0)).max(1)[1].view(1,1)

def optimize_model(optimizer, policy_net, target_net, gamma, lr, memory, batch_size):

    if len(memory) < batch_size:
        return 0 #yes, this will mess up the plot

    transitions = memory.sample(batch_size)

    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool)

    non_final_next_states = torch.stack(tuple([s for s in batch.next_state if s is not None]))

    state_batch = torch.stack(batch.state)
    action_batch = torch.stack(batch.action).squeeze(1)
    reward_batch = torch.stack(batch.reward).squeeze(1)

    # Compute Q(s, a) and select the action taken
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    next_state_values = torch.zeros(batch_size, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()

    # Compute the expected Q values
    expected_state_action_values = (next_state_values * gamma) + reward_batch

    # Compute Huber loss
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()

    return loss.item()

def train(env, memory_size, batch_size, gamma, target_update, lr, episodes, stack_frames, save_every):

    env = gym.make(env)

    action_space = env.action_space.n

    policy_net = DQN(action_space).to(device)
    target_net = DQN(action_space).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.RMSprop(policy_net.parameters(), lr=lr)

    memory = ReplayMemory(memory_size)

    epsilon = 1.0

    total_steps = 0

    for episode in range(episodes):

        if episode % 5 == 1:
            print(f'Alive. Iteration {episode}. Epsilon {epsilon}. Replay Memory Size {len(memory)}. Last total reward: {total_reward}')
        
        o = env.reset()
        done = False
        steps = 0
        total_reward = 0
        total_loss = 0
        state = _init_state(o, stack_frames).to(device)
        while not done:
            steps += 1
            total_steps += 1

            action = _select_action(state, epsilon, action_space, policy_net)

            observation, reward, done, _ = env.step(action.item())

            total_reward += reward

            reward = torch.tensor([reward], device=device)

            if not done:
                frame = preprocess_image(observation)
                new_state = shift_tensor(state, frame)
            else:
                new_state = None

            memory.push(state, action, reward, new_state)

            loss = optimize_model(optimizer, policy_net, target_net, gamma, lr, memory, batch_size)
            total_loss += loss

            if total_steps % target_update == 0:
                target_net.load_state_dict(policy_net.state_dict())

            epsilon = max(0.1, epsilon - 4.5e-07)

            state = None if new_state is None else new_state.clone()

        writer.add_scalar('Train/Loss', total_loss, episode)
        writer.add_scalar('Train/Reward', total_reward, episode)
        writer.add_scalar('Train/Epsilon', epsilon, episode)

        if episode % save_every == 0:
            torch.save(policy_net.state_dict(), f'./models/policy_net_{episode}.pth')
            torch.save(target_net.state_dict(), f'./models/target_net_{episode}.pth')

    torch.save(policy_net.state_dict(), './models/policy_net_latest.pth')
    torch.save(target_net.state_dict(), './models/target_net_latest.pth')








