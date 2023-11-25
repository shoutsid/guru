import gym
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import namedtuple

# Define the Q-network


class QNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# Define the experience replay buffer
Experience = namedtuple(
    'Experience', ('state', 'action', 'next_state', 'reward', 'done'))


class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def store(self, experience):
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
        else:
            self.buffer[self.position] = experience
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):  # Add this method to get the length of the buffer
        return len(self.buffer)

# Define the DQN agent


class DQNAgent:
    def __init__(self, input_size, hidden_size, output_size, capacity, batch_size, gamma, epsilon_start, epsilon_end, epsilon_decay):
        self.q_network = QNetwork(
            input_size, hidden_size, output_size).cuda()  # Move to GPU
        self.target_network = QNetwork(
            input_size, hidden_size, output_size).cuda()  # Move to GPU
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()
        self.optimizer = optim.Adam(self.q_network.parameters())
        self.memory = ReplayBuffer(capacity)
        self.batch_size = batch_size
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.output_size = output_size  # Store output_size as an attribute

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.output_size - 1)  # Use output_size
        else:
            with torch.no_grad():
                state = state.cuda()  # Move state to GPU
                return self.q_network(state).argmax().item()

    def train(self):
        if len(self.memory) < self.batch_size:
            return

        experiences = self.memory.sample(self.batch_size)
        batch = Experience(*zip(*experiences))

        state_batch = torch.stack(batch.state).cuda()  # Move to GPU
        action_batch = torch.tensor(
            batch.action, dtype=torch.int64).unsqueeze(1).cuda()  # Move to GPU
        next_state_batch = torch.stack(batch.next_state).cuda()  # Move to GPU
        reward_batch = torch.tensor(
            batch.reward, dtype=torch.float32).cuda()  # Move to GPU
        done_batch = torch.tensor(
            batch.done, dtype=torch.float32).cuda()  # Move to GPU

        q_values = self.q_network(state_batch).gather(1, action_batch)

        next_q_values = self.target_network(
            next_state_batch).max(1)[0].detach()
        expected_q_values = reward_batch + \
            (1 - done_batch) * self.gamma * next_q_values

        loss = nn.MSELoss()(q_values, expected_q_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network
        self.update_target_network()

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())


# Initialize the CartPole-v1 environment
env = gym.make('CartPole-v1')
input_size = env.observation_space.shape[0]
output_size = env.action_space.n

# Define hyperparameters
hidden_size = 128
capacity = 10000
batch_size = 64
gamma = 0.99
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 0.995
target_update_frequency = 10

# Initialize the DQN agent
agent = DQNAgent(input_size, hidden_size, output_size, capacity,
                 batch_size, gamma, epsilon_start, epsilon_end, epsilon_decay)

# Training loop
epsilon = epsilon_start
for episode in range(100):
    state = env.reset()
    total_reward = 0

    while True:
        # Check if the state is a tuple and extract the first element
        if isinstance(state, tuple):
            state = state[0]

        # Convert state to a tensor
        state_tensor = torch.tensor(
            state, dtype=torch.float32).cuda()  # Move to GPU

        action = agent.select_action(state_tensor)

        step_result = env.step(action)
        next_state, reward, done, _ = step_result[:4]

        agent.memory.store(Experience(state_tensor, action, torch.tensor(
            next_state, dtype=torch.float32), reward, done))
        agent.train()
        total_reward += reward
        state = next_state

        if done:
            break

    epsilon = max(epsilon_end, epsilon * epsilon_decay)

    if episode % target_update_frequency == 0:
        print(
            f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {epsilon}")

    print(
        f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {epsilon}, State: {state}")
