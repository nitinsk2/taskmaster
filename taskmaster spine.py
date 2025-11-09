# === Adaptive Task Scheduler (Simplified: No Energy Penalty, Context Fit, or Overlength) ===

from dataclasses import dataclass
from typing import List

# === 1. Helper: Linear interpolation ===
def lerp(a, b, t):
    """Linearly interpolate between a and b by factor t (0..1)."""
    return a + (b - a) * t


# === 2. State & Dynamic Weights ===
@dataclass
class State:
    energy: int  # 1–5
    mood: int    # -2..+2
    stress: int  # -2..+2


@dataclass
class Weights:
    Wreward: float
    Wpressure: float
    Wenergy: float
    Wurgency: float


def dynamic_weights(state: State) -> Weights:
    """
    Adjust weights dynamically based on user's current state:
      - Higher mood → reward matters more.
      - Higher stress → pressure matters more.
      - Lower energy → energy mismatch penalties matter more.
    """
    e = (state.energy - 1) / 4  # normalize 0..1
    m = (state.mood + 2) / 4
    s = (state.stress + 2) / 4

    return Weights(
        Wreward=lerp(0.8, 1.2, m),
        Wpressure=lerp(0.6, 0.9, s),
        Wenergy=lerp(1.4, 0.6, e),
        Wurgency=1.0
    )


# === 3. Task and Scoring ===
@dataclass
class Task:
    name: str
    reward: float       # 0..1 (how satisfying/meaningful it feels)
    pressure: float     # 0..1 (external urgency or accountability)
    urgency: float      # 0..1 (time pressure)
    energy_level: int   # 1–5 (energy required)
    mood_fit: int       # -2..+2 (emotional state it fits)
    estimated_time: int # minutes
    score: float = 0.0
    final_score: float = 0.0


def score_task(task: Task, weights: Weights, user: State, available_time: int) -> float:
    """Compute weighted priority score for each task, adjusting for user alignment."""
    # Base weighted score
    task.score = (
        weights.Wreward * task.reward +
        weights.Wpressure * task.pressure +
        weights.Wurgency * task.urgency
    )

    # State-based modifiers (alignment)
    F_energy = 1 - abs(task.energy_level - user.energy) / 5
    F_mood   = 1 - abs(task.mood_fit - user.mood) / 4
    F_time   = min(1, available_time / task.estimated_time)

    # Final composite score
    task.final_score = task.score * F_energy * F_mood * F_time
    return task.final_score


def block_length(energy: int, mood: int) -> int:
    """Estimate how long you can comfortably focus given current state."""
    base_lengths = [0, 18, 28, 45, 65, 75]  # index 1–5
    tweak = -8 if mood <= -1 else 8 if mood >= 1 else 0
    return max(10, base_lengths[energy] + tweak)


# === 5. Example Usage ===

#Energy: 2
# Mood: 0
# Stress: 1
# Available time: 45



if _name_ == '_main_':
     # Current user state (tired but slightly positive)
    state = State(energy=2, mood=0, stress=1)
    available_time = 45
    weights = dynamic_weights(state)

    # More complex, real-world task list
    tasks: List[Task] = [
        Task('Morning workout', 0.7, 0.3, 0.4, 5, 1, 40),
        Task('Reply to urgent client email', 0.6, 0.9, 1.0, 2, -1, 15),
        Task('Code feature update', 0.9, 0.7, 0.8, 4, 0, 90),
        Task('Plan weekend trip', 0.8, 0.2, 0.3, 2, 2, 25),
        Task('Team meeting prep', 0.7, 0.8, 0.6, 3, 0, 30),
        Task('Clean workspace', 0.4, 0.3, 0.2, 1, -1, 10),
        Task('Read new research article', 0.5, 0.2, 0.4, 2, 1, 20),
        Task('Fix budget spreadsheet', 0.6, 0.8, 0.7, 3, -1, 45),
    ]

    # Score each task
    for t in tasks:
        score_task(t, weights, state, available_time)

    # Sort by priority (best fit = highest score)
    tasks_sorted = sorted(tasks, key=lambda t: t.final_score, reverse=True)

    # Output results
    print(f"\n🧩 User State → Energy: {state.energy}, Mood: {state.mood}, Stress: {state.stress}")
    print(f"Available Time: {available_time} min")
    print(f"Recommended Focus Block: {block_length(state.energy, state.mood)} min\n")

    print("📊 Task Priorities:")
    final = []
    for t in tasks_sorted:
        print(f"{t.name:30} | base={t.score:.2f} | final={t.final_score:.2f}")
        final.append(t.name)

    print("\n✅ Final Recommended Order:")
    for i, name in enumerate(final, 1):
        print(f"{i}. {name}")