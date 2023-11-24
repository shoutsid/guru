import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KDTree


class QLearningBase:
    def __init__(self, num_states, num_actions, k_neighbors, gamma):
        self.num_states = num_states
        self.num_actions = num_actions
        self.k = k_neighbors
        self.gamma = gamma
        self.Q = np.zeros((num_states, num_actions))
        self.max_k_neighbors = k_neighbors

    def fit_neighbors(self, state_action_pairs):
        self.neighbors = KDTree(state_action_pairs, leaf_size=30)
        self.fitted_points = state_action_pairs.shape[0]

    def discretize_state(self, state, state_space):
        return np.argmin(np.abs(state_space - state))

    def get_k_neighbors(self):
        # Ensure k does not exceed the number of fitted points
        return min(self.max_k_neighbors, self.fitted_points - 1)


class OfflineQLearning(QLearningBase):
    def update_q_values(self, experiences, state_space, action_space):
        # Vectorize state and action discretization
        states, actions, rewards, next_states = zip(*experiences)
        state_indices = np.digitize(states, state_space) - 1
        action_indices = [action_space.index(a) for a in actions]
        next_state_indices = np.digitize(next_states, state_space) - 1

        # Prepare state-action pairs for KDTree
        state_action_pairs = np.column_stack((state_indices, action_indices))
        self.fit_neighbors(state_action_pairs)

        # Vectorize Q-value updates
        for state_idx, action_idx, reward, next_state_idx in zip(state_indices, action_indices, rewards, next_state_indices):
            _, indices = self.neighbors.query(
                [[state_idx, action_idx]], k=self.get_k_neighbors())
            valid_indices = indices[indices <
                                    self.num_states * self.num_actions]

            # Extract Q-values and ensure it's two-dimensional
            q_values = self.Q[valid_indices // self.num_actions,
                              valid_indices % self.num_actions]
            if q_values.ndim == 1:
                q_values = q_values.reshape(1, -1)

            # Compute the mean of the max Q-values
            self.Q[state_idx, action_idx] = np.mean(
                reward + self.gamma * np.max(q_values, axis=1))


class OnlineQLearning(QLearningBase):
    def update_q_value(self, state, action, reward, next_state, state_space, action_space):
        state_idx = np.digitize([state], state_space)[0] - 1
        action_idx = action_space.index(action)
        next_state_idx = np.digitize([next_state], state_space)[0] - 1

        # Ensure that fit_neighbors is called to initialize the neighbors attribute
        if not hasattr(self, 'neighbors'):
            state_action_pairs = np.array([[self.discretize_state(
                s, state_space), a] for s in state_space for a in action_space])
            self.fit_neighbors(state_action_pairs)

        _, indices = self.neighbors.query(
            [[state_idx, action_idx]], k=self.get_k_neighbors())
        valid_indices = indices[indices < self.num_states * self.num_actions]

        # Extract Q-values and ensure it's two-dimensional
        q_values = self.Q[valid_indices // self.num_actions,
                          valid_indices % self.num_actions]
        if q_values.ndim == 1:
            q_values = q_values.reshape(1, -1)

        # Compute the mean of the max Q-values
        self.Q[state_idx, action_idx] = np.mean(
            reward + self.gamma * np.max(q_values, axis=1))


def get_reward(state, goal_state):
    return -np.abs(state - goal_state)


def next_state(state, action):
    return state + action


def collect_data(state_space, action_space, episodes, goal_state):
    experiences = []
    for _ in range(episodes):
        state = np.random.uniform(low=0, high=100)
        action = np.random.choice(action_space)
        new_state = next_state(state, action)
        reward = get_reward(new_state, goal_state)
        experiences.append((state, action, reward, new_state))
    return experiences


def run_simulation(ql_algorithm, episodes, goal_state, state_space, action_space):
    total_rewards = []
    for episode in range(episodes):
        state = np.random.uniform(low=0, high=100)
        done = False
        total_reward = 0
        while not done:
            action = np.random.choice(action_space)
            new_state = next_state(state, action)
            reward = get_reward(new_state, goal_state)
            ql_algorithm.update_q_value(
                state, action, reward, new_state, state_space, action_space)
            state = new_state
            total_reward += reward
            if new_state == goal_state:
                done = True
        total_rewards.append(total_reward)
    return total_rewards


def plot_q_table(q_table, title="Q-Table Heatmap"):
    plt.figure(figsize=(14, 8))
    plt.imshow(q_table, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.title(title)
    plt.xlabel('Actions')
    plt.ylabel('States')
    plt.show()


def plot_rewards(rewards, title="Total Rewards Over Episodes"):
    plt.figure(figsize=(10, 6))
    plt.plot(rewards, label='Total Reward per Episode')
    plt.xlabel('Episodes')
    plt.ylabel('Total Reward')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()


# Environment setup
state_space = np.linspace(0, 100, 100)  # Reduced state space
action_space = [-1, 0, 1]
goal_state = 50
episodes = 2  # Reduced for testing

# Offline Q Learning
offline_ql = OfflineQLearning(len(state_space), len(
    action_space), k_neighbors=3, gamma=0.9)
pre_collected_data = collect_data(
    state_space, action_space, episodes, goal_state)
offline_ql.update_q_values(pre_collected_data, state_space, action_space)
print(offline_ql)

# Online Q Learning
online_ql = OnlineQLearning(len(state_space), len(
    action_space), k_neighbors=3, gamma=0.9)
online_rewards = run_simulation(
    online_ql, episodes, goal_state, state_space, action_space)

plot_q_table(online_ql.Q, "Online Q-Learning: Q-Table Heatmap")
plot_rewards(online_rewards, "Online Q-Learning: Total Rewards Over Episodes")
