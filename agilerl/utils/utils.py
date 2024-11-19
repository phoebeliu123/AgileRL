from typing import Dict, Any, Optional, List, Union
import gymnasium as gym
from gymnasium import spaces
import matplotlib.pyplot as plt
import numpy as np

from agilerl.algorithms.base import EvolvableAlgorithm
from agilerl.algorithms.cqn import CQN
from agilerl.algorithms.ddpg import DDPG
from agilerl.algorithms.dqn import DQN
from agilerl.algorithms.dqn_rainbow import RainbowDQN
from agilerl.algorithms.maddpg import MADDPG
from agilerl.algorithms.matd3 import MATD3
from agilerl.algorithms.neural_ts_bandit import NeuralTS
from agilerl.algorithms.neural_ucb_bandit import NeuralUCB
from agilerl.algorithms.ppo import PPO
from agilerl.algorithms.td3 import TD3
from agilerl.vector.pz_async_vec_env import AsyncPettingZooVecEnv
from agilerl.networks.base import EvolvableModule

PopulationType = list[EvolvableAlgorithm]

def make_vect_envs(env_name: str, num_envs: int = 1) -> gym.vector.AsyncVectorEnv:
    """Returns async-vectorized gym environments.

    :param env_name: Gym environment name
    :type env_name: str
    :param num_envs: Number of vectorized environments, defaults to 1
    :type num_envs: int, optional
    """
    return gym.vector.AsyncVectorEnv(
        [lambda: gym.make(env_name) for i in range(num_envs)]
    )

def make_multi_agent_vect_envs(env: Any, num_envs: int = 1, **env_kwargs: Any) -> AsyncPettingZooVecEnv:
    """Returns async-vectorized PettingZoo parallel environments.

    :param env: PettingZoo parallel environment object
    :type env: pettingzoo.utils.env.ParallelEnv
    :param num_envs: Number of vectorized environments, defaults to 1
    :type num_envs: int, optional
    """
    env_fns = [lambda: env(**env_kwargs) for _ in range(num_envs)]
    return AsyncPettingZooVecEnv(env_fns=env_fns)

def make_skill_vect_envs(env_name: str, skill: Any, num_envs: int = 1) -> gym.vector.AsyncVectorEnv:
    """Returns async-vectorized gym environments.

    :param env_name: Gym environment name
    :type env_name: str
    :param skill: Skill wrapper to apply to environment
    :type skill: agilerl.wrappers.learning.Skill
    :param num_envs: Number of vectorized environments, defaults to 1
    :type num_envs: int, optional
    """
    return gym.vector.AsyncVectorEnv(
        [lambda: skill(gym.make(env_name)) for i in range(num_envs)]
    )

GymSpaceType = Union[spaces.Space, List[spaces.Space]]

def create_population(
    algo: str,
    observation_space: GymSpaceType,
    action_space: GymSpaceType,
    one_hot: bool,
    net_config: Optional[Dict[str, Any]],
    INIT_HP: Dict[str, Any],
    actor_network: Optional[EvolvableModule] = None,
    critic_network: Optional[EvolvableModule] = None,
    population_size: int = 1,
    num_envs: int = 1,
    device: str = "cpu",
    accelerator: Optional[Any] = None,
    torch_compiler: Optional[Any] = None,
) -> PopulationType:
    """Returns population of identical agents.

    :param algo: RL algorithm
    :type algo: str
    :param observation_space: Observation space
    :type observation_space: spaces.Space
    :param action_space: Action space
    :type action_space: spaces.Space
    :param one_hot: One-hot encoding
    :type one_hot: bool
    :param net_config: Network configuration
    :type net_config: dict or None
    :param INIT_HP: Initial hyperparameters
    :type INIT_HP: dict
    :param actor_network: Custom actor network, defaults to None
    :type actor_network: nn.Module, optional
    :param critic_network: Custom critic network, defaults to None
    :type critic_network: nn.Module, optional
    :param population_size: Number of agents in population, defaults to 1
    :type population_size: int, optional
    :param num_envs: Number of vectorized environments, defaults to 1
    :type num_envs: int, optional
    :param device: Device for accelerated computing, 'cpu' or 'cuda', defaults to 'cpu'
    :type device: str, optional
    :param accelerator: Accelerator for distributed computing, defaults to None
    :type accelerator: accelerate.Accelerator(), optional
    :param torch_compiler: Torch compiler, defaults to None
    :type torch_compiler: Any, optional
    :return: Population of agents
    :rtype: list[EvolvableAlgorithm]
    """
    population = []
    if algo == "DQN":
        for idx in range(population_size):
            agent = DQN(
                observation_space=observation_space,
                action_space=action_space,
                one_hot=one_hot,
                index=idx,
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr=INIT_HP["LR"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                double=INIT_HP["DOUBLE"],
                actor_network=actor_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "Rainbow DQN":
        for idx in range(population_size):
            agent = RainbowDQN(
                observation_space=observation_space,
                action_space=action_space,
                one_hot=one_hot,
                index=idx,
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr=INIT_HP["LR"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                beta=INIT_HP["BETA"],
                prior_eps=INIT_HP["PRIOR_EPS"],
                num_atoms=INIT_HP["NUM_ATOMS"],
                v_min=INIT_HP["V_MIN"],
                v_max=INIT_HP["V_MAX"],
                n_step=INIT_HP["N_STEP"],
                actor_network=actor_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "DDPG":
        for idx in range(population_size):
            agent = DDPG(
                observation_space=observation_space,
                action_space=action_space,
                one_hot=one_hot,
                max_action=INIT_HP["MAX_ACTION"],
                min_action=INIT_HP["MIN_ACTION"],
                O_U_noise=INIT_HP["O_U_NOISE"],
                expl_noise=INIT_HP["EXPL_NOISE"],
                vect_noise_dim=num_envs,
                mean_noise=INIT_HP["MEAN_NOISE"],
                theta=INIT_HP["THETA"],
                dt=INIT_HP["DT"],
                index=idx,
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr_actor=INIT_HP["LR_ACTOR"],
                lr_critic=INIT_HP["LR_CRITIC"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                policy_freq=INIT_HP["POLICY_FREQ"],
                actor_network=actor_network,
                critic_network=critic_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "PPO":
        for idx in range(population_size):
            agent = PPO(
                observation_space=observation_space,
                action_space=action_space,
                one_hot=one_hot,
                discrete_actions=INIT_HP["DISCRETE_ACTIONS"],
                index=idx,
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr=INIT_HP["LR"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                gae_lambda=INIT_HP["GAE_LAMBDA"],
                action_std_init=INIT_HP["ACTION_STD_INIT"],
                clip_coef=INIT_HP["CLIP_COEF"],
                ent_coef=INIT_HP["ENT_COEF"],
                vf_coef=INIT_HP["VF_COEF"],
                max_grad_norm=INIT_HP["MAX_GRAD_NORM"],
                target_kl=INIT_HP["TARGET_KL"],
                update_epochs=INIT_HP["UPDATE_EPOCHS"],
                actor_network=actor_network,
                critic_network=critic_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "CQN":
        for idx in range(population_size):
            agent = CQN(
                observation_space=observation_space,
                action_space=action_space,
                one_hot=one_hot,
                index=idx,
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr=INIT_HP["LR"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                double=INIT_HP["DOUBLE"],
                actor_network=actor_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "TD3":
        for idx in range(population_size):
            agent = TD3(
                observation_space=observation_space,
                action_space=action_space,
                one_hot=one_hot,
                max_action=INIT_HP["MAX_ACTION"],
                min_action=INIT_HP["MIN_ACTION"],
                O_U_noise=INIT_HP["O_U_NOISE"],
                expl_noise=INIT_HP["EXPL_NOISE"],
                vect_noise_dim=num_envs,
                mean_noise=INIT_HP["MEAN_NOISE"],
                theta=INIT_HP["THETA"],
                dt=INIT_HP["DT"],
                index=idx,
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr_actor=INIT_HP["LR_ACTOR"],
                lr_critic=INIT_HP["LR_CRITIC"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                policy_freq=INIT_HP["POLICY_FREQ"],
                actor_network=actor_network,
                critic_networks=critic_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "MADDPG":
        for idx in range(population_size):
            agent = MADDPG(
                observation_spaces=observation_space,
                action_spaces=action_space,
                one_hot=one_hot,
                n_agents=INIT_HP["N_AGENTS"],
                agent_ids=INIT_HP["AGENT_IDS"],
                O_U_noise=INIT_HP["O_U_NOISE"],
                expl_noise=INIT_HP["EXPL_NOISE"],
                vect_noise_dim=num_envs,
                mean_noise=INIT_HP["MEAN_NOISE"],
                theta=INIT_HP["THETA"],
                dt=INIT_HP["DT"],
                index=idx,
                max_action=INIT_HP["MAX_ACTION"],
                min_action=INIT_HP["MIN_ACTION"],
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr_actor=INIT_HP["LR_ACTOR"],
                lr_critic=INIT_HP["LR_CRITIC"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                discrete_actions=INIT_HP["DISCRETE_ACTIONS"],
                actor_networks=actor_network,
                critic_networks=critic_network,
                device=device,
                accelerator=accelerator,
                torch_compiler=torch_compiler,
            )
            population.append(agent)

    elif algo == "MATD3":
        for idx in range(population_size):
            agent = MATD3(
                observation_spaces=observation_space,
                action_spaces=action_space,
                one_hot=one_hot,
                n_agents=INIT_HP["N_AGENTS"],
                agent_ids=INIT_HP["AGENT_IDS"],
                O_U_noise=INIT_HP["O_U_NOISE"],
                expl_noise=INIT_HP["EXPL_NOISE"],
                vect_noise_dim=num_envs,
                mean_noise=INIT_HP["MEAN_NOISE"],
                theta=INIT_HP["THETA"],
                dt=INIT_HP["DT"],
                index=idx,
                max_action=INIT_HP["MAX_ACTION"],
                min_action=INIT_HP["MIN_ACTION"],
                net_config=net_config,
                batch_size=INIT_HP["BATCH_SIZE"],
                lr_actor=INIT_HP["LR_ACTOR"],
                lr_critic=INIT_HP["LR_CRITIC"],
                policy_freq=INIT_HP["POLICY_FREQ"],
                learn_step=INIT_HP["LEARN_STEP"],
                gamma=INIT_HP["GAMMA"],
                tau=INIT_HP["TAU"],
                discrete_actions=INIT_HP["DISCRETE_ACTIONS"],
                actor_networks=actor_network,
                critic_networks=critic_network,
                device=device,
                accelerator=accelerator,
                torch_compiler=torch_compiler,
            )
            population.append(agent)

    elif algo == "NeuralUCB":
        for idx in range(population_size):
            agent = NeuralUCB(
                observation_space=observation_space,
                action_space=action_space,
                index=idx,
                net_config=net_config,
                gamma=INIT_HP["GAMMA"],
                lamb=INIT_HP["LAMBDA"],
                reg=INIT_HP["REG"],
                batch_size=INIT_HP["BATCH_SIZE"],
                lr=INIT_HP["LR"],
                learn_step=INIT_HP["LEARN_STEP"],
                actor_network=actor_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    elif algo == "NeuralTS":
        for idx in range(population_size):
            agent = NeuralTS(
                observation_space=observation_space,
                action_space=action_space,
                index=idx,
                net_config=net_config,
                gamma=INIT_HP["GAMMA"],
                lamb=INIT_HP["LAMBDA"],
                reg=INIT_HP["REG"],
                batch_size=INIT_HP["BATCH_SIZE"],
                lr=INIT_HP["LR"],
                learn_step=INIT_HP["LEARN_STEP"],
                actor_network=actor_network,
                device=device,
                accelerator=accelerator,
            )
            population.append(agent)

    return population


def calculate_vectorized_scores(
    rewards: np.ndarray,
    terminations: np.ndarray,
    include_unterminated: bool = False,
    only_first_episode: bool = True,
) -> List[float]:
    """
    Calculate the vectorized scores for episodes based on rewards and terminations.

    :param rewards: Array of rewards for each environment.
    :type rewards: np.ndarray
    :param terminations: Array indicating termination points for each environment.
    :type terminations: np.ndarray
    :param include_unterminated: Whether to include rewards from unterminated episodes, defaults to False.
    :type include_unterminated: bool, optional
    :param only_first_episode: Whether to consider only the first episode, defaults to True.
    :type only_first_episode: bool, optional
    :return: List of episode rewards.
    :rtype: list[float]
    """
    episode_rewards = []
    num_envs, _ = rewards.shape

    for env_index in range(num_envs):
        # Find the indices where episodes terminate for the current environment
        termination_indices = np.where(terminations[env_index] == 1)[0]

        # If no terminations, sum the entire reward array for this environment
        if len(termination_indices) == 0:
            episode_reward = np.sum(rewards[env_index])
            episode_rewards.append(episode_reward)
            continue  # Skip to the next environment

        # Initialize the starting index for segmenting
        start_index = 0

        for termination_index in termination_indices:
            # Sum the rewards for the current episode
            episode_reward = np.sum(
                rewards[env_index, start_index : termination_index + 1]
            )

            # Store the episode reward
            episode_rewards.append(episode_reward)

            # If only the first episode is required, break after processing it
            if only_first_episode:
                break

            # Update the starting index for segmenting
            start_index = termination_index + 1

        # If include_unterminated is True, sum the rewards from the last termination index to the end
        if (
            not only_first_episode
            and include_unterminated
            and start_index < len(rewards[env_index])
        ):
            episode_reward = np.sum(rewards[env_index, start_index:])
            episode_rewards.append(episode_reward)

    return episode_rewards

def print_hyperparams(pop: PopulationType) -> None:
    """Prints current hyperparameters of agents in a population and their fitnesses.

    :param pop: Population of agents
    :type pop: list[object]
    """

    for agent in pop:
        print(
            "Agent ID: {}    Mean 5 Fitness: {:.2f}    Attributes: {}".format(
                agent.index, np.mean(agent.fitness[-5:]), agent.inspect_attributes()
            )
        )

def plot_population_score(pop: PopulationType) -> None:
    """Plots the fitness scores of agents in a population.

    :param pop: Population of agents
    :type pop: list[object]
    """
    plt.figure()
    for agent in pop:
        scores = agent.fitness
        steps = agent.steps[:-1]
        plt.plot(steps, scores)
    plt.title("Score History - Mutations")
    plt.xlabel("Steps")
    plt.ylim(bottom=-400)
    plt.show()


def get_env_defined_actions(info, agents):
    env_defined_actions = {
        agent: info[agent].get("env_defined_action", None) for agent in agents
    }

    if all(eda is None for eda in env_defined_actions.values()):
        return

    return env_defined_actions
