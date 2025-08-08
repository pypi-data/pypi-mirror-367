# =============== MAB Solver ===============

## About the Developer:
- Name: Shreyas Sawant
- College: Mukesh Patel School of Technology Management and Engineering
- Department: Artificial Intelligence
- Related Course: Reinforcement Learning

## About the Library
The MAB solver or the Multi Agent Bandit problem solver consists of five main functions.
Naturally it is meant to solve the MAB problem but it uses Pure Exploration, Pure exploitation, Fixed Exploration + Greedy Exploitation, Epsilon Greedy approach and finally Upper Confidence Bound (UCB).
There are a handful of parameters which can be tweaked like time steps (t), number of arms (n), fixed time steps (tf) (used in Fixed Exploration + Greedy Exploitation), epsilon (eps) (used in Epsilon Greedy),  constant (c) (used in UCB).
The library handles the outputs randomly and for this version, there is no way of manipulating the input probabilities. But it can be expected in the future versions of the library.

## Steps to use:
* First install the PyMABSolver library using the pip command
* Next initialise the MABSolver class by creating an instance
* Important parameters: 
    1. Time steps (t): An integer for number of iterations.
    2. Number of arms (n): An integer for number of Machines/Bandits to choose from.
    3. Fixed time steps (tf): [only while using Fixed Exploration + Greedy Exploitation] An integer for number of fixed exploration iterations
    4. epsilon (eps): [only while using Epsilon Greedy] A float number between 0 and 1 acting as a threshold for Exploring vs Exploiting
    6. c: [only while using UCB] A float number greater than 0 acting as a constant to determine whether to prioritise exploration or exploitation
        if c -> 0: then Exploitation is emphasized
        if c -> 1: then Exploration is emphasized
* Next call the respective functions namely: exploration, exploitation, fixed_exploration_greedy_exploitation, epsilon_greedy, ucb
* (Optional) Finally for visualisation the plot_comparison function can be called

For Referal code follow below GitHub link:
https://github.com/Shreyswan/PyMABSolver.git