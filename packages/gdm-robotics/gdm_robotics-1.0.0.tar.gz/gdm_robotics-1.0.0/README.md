# `gdm_robotics`: The Google DeepMind Robotics interfaces

This package describes a set of interfaces for Python reinforcement learning
(RL) environments. It consists of the following core components:

*   `gdm_robotics.interfaces.Environment`: An abstract base class for RL environments.
*   `gdm_robotics.interfaces.Policy`: An abstract base class for Agent policies.
*   `gdm_robotics.interfaces.EpisodicLogger`: An abstract base class for loggers for Agent/Environment interaction.
*   `gdm_robotics.runtime.RunLoop`: A concrete RunLoop class to run a policy against an environment and logging their interaction.

## Installation

`gdm_robotics` can be installed from PyPI using `pip`:

```bash
pip install gdm_robotics
```
