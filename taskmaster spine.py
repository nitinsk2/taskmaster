@dataclass
class Task:
    name: str
    reward: float
    context_fit: float
    pressure: float
    energy_penalty: float
    overlength: float
    urgency: float
    energy_level: int       # 1-5, how much energy this task needs
    mood_fit: int           # -2..2, mood type the task suits
    estimated_time: int     # minutes
    score: float = 0.0
    final_score: float = 0.0

def score_task(task: Task, weights: Weights, user: State, available_time: int) -> float:
    # Base weighted score
    task.score = (
        weights.Wreward * task.reward +
        weights.Wctx * task.context_fit +
        weights.Wpressure * task.pressure -
        weights.Wenergy * task.energy_penalty -
        weights.Wlength * task.overlength +
        weights.Wurgency * task.urgency
    )
    # Match to user state
    F_energy = 1 - abs(task.energy_level - user.energy)/5
    F_mood   = 1 - abs(task.mood_fit - user.mood)/4
    F_time   = min(1, available_time / task.estimated_time)

    task.final_score = task.score * F_energy * F_mood * F_time
    return task.final_score

# Example:
state = State(energy=3, mood=-1, stress=0)
weights = dynamic_weights(state)
available_time = 30  # minutes

tasks = [
    Task('Email cleanup', 0.4, 1.0, 0.6, 0.2, 0.2, 0.3, 2, -1, 15),
    Task('Write report draft', 0.8, 0.9, 0.7, 0.6, 0.7, 0.5, 4, 0, 45),
    Task('Organize notes', 0.5, 1.0, 0.8, 0.3, 0.3, 0.2, 3, -1, 25)
]

for t in tasks:
    score_task(t, weights, state, available_time)

tasks_sorted = sorted(tasks, key=lambda t: t.final_score, reverse=True)

for t in tasks_sorted:
    print(f"{t.name}: base={t.score:.2f}, final={t.final_score:.2f}")
