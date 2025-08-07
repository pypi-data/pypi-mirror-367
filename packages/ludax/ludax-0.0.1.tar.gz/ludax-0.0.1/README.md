# Ludax

Ludax is a domain specific language for board games that compiles into hardware-accelerated learning environments using [JAX](https://github.com/jax-ml/jax). Ludax draws inspiration from the [Ludii](https://ludii.games/index.php) game description language as well as [PGX](https://github.com/sotetsuk/pgx), a library of JAX implementations for classic board games and video games. Ludax supports a variety of two-player perfect-information board games and can run at tens of millions of steps per second on modern GPUs.

![Throughput of Ludax environments compared to PGX and Ludii implementations](/renders/throughput_comparison.png)
## ToDo before merge
- Fix compare_implementations.py and other scripts

## Issues
- Confusingly, 'state.game_state.current_player' is not the current player? See connectivity test.
- `state.first_player` should be removed, why not define P1 as the first player? Graphically, we can still encode the first player as black or some other color, but it should not be part of the state.
- remove `state.truncated`, that should be handled by the client.
- `state.observation` should be removed, we can provide a function to convert game state to an observation instead.
- `state.legal_action_mask` should be False for all actions after the game is over, no? Right now it's True for all actions.
- It doesn't feel intuitive that the mover_reward is in `state.mover_reward` but the current_player is hidden in `state.game_state.current_player`. Is game_state supposed to represent internal variables who's API can change from game to game? If so, it should not be part of the public API.
- We need to make a decision about whether we intend to support non-two player games and games where the same player can play multiple times in a row. If we don't support this, we can simplify the API, e.g. by guaranteeing that if global step is even, the current player is P1 (unless the game is over, but then it doesn't matter what action you take).
- We really need to demonstrate that fp16 is faster than fp32 on our target hardware. If it isn't then we should stick to fp32 since that's what most other libraries use.
- config.State should inherit from pgx_core.PGXState no?

## Installation
Ludax requires a Python version of at least `3.11`. First, install the JAX library (see [here](https://docs.jax.dev/en/latest/installation.html) for instructions). Then, create a new Python environment and run
```
pip install -r requirements.txt
```

## Basic Usage
To instantiate an environment in Ludax, you pass in the path to grammatically-valid `.ldx` file (see `grammar.lark` for syntax details). The general environment API is very similar to PGX and gymnax:
```python
import jax
import jax.numpy as jnp

GAME_PATH = "games/tic_tac_toe.ldx"
BATCH_SIZE = 1024

env = LudaxEnvironment(GAME_PATH)
init = jax.jit(jax.vmap(env.init))
step = jax.jit(jax.vmap(env.step))

def _run_batch(state, key):
    def cond_fn(args):
        state, _ = args
        return ~(state.terminated | state.truncated).all()
    
    def body_fn(args):
        state, key = args
        key, subkey = jax.random.split(key)
        logits = jnp.log(state.legal_action_mask.astype(jnp.float32))
        action = jax.random.categorical(key, logits=logits, axis=1)
        state = step(state, action)
        return state, key
    
    state, key = jax.lax.while_loop(cond_fn, body_fn, (state, key))

    return state, key

run_batch = jax.jit(_run_batch)

key = jax.random.PRNGKey(42)
key, subkey = jax.random.split(key)
keys = jax.random.split(subkey, BATCH_SIZE)

state = init(keys)
state, key = run_batch(state, key)
```

## Comparisons
To generate comparisons against Ludii and PGX, run `compare_implementations.py` with the appropriate command-line arguments. For instance, to compare on Tic-Tac-Toe on batch sizes of 1 to 1024, you would run
```
python compare_implementations.py --game tic_tac_toe --batch_size_step 2 --num_batch_sizes 11
```

## Reinforcement Learning
We provide a demonstration of using the PGX AlphaZero implementation to train agents in the Ludax implementation in `pgx_alphazero/train.py`.

## Interactive Mode
To play a game interactively, run `python interactive.py`. This will launch an app on your local host on port 8080. After running the command, navigate to [http://127.0.0.1:8080](http://127.0.0.1:8080) and you will see the list games currently in the `games/` directory. Navigating to any of the links will let you playtest the game in the browser by clicking on a square to make your move.