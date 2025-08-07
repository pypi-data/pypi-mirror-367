# Task

Types:

```python
from chunkr_ai.types import Task
```

Methods:

- <code title="get /tasks">client.task.<a href="./src/chunkr_ai/resources/task/task.py">list</a>(\*\*<a href="src/chunkr_ai/types/task_list_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task/task.py">SyncTasksPage[Task]</a></code>
- <code title="delete /task/{task_id}">client.task.<a href="./src/chunkr_ai/resources/task/task.py">delete</a>(task_id) -> None</code>
- <code title="get /task/{task_id}/cancel">client.task.<a href="./src/chunkr_ai/resources/task/task.py">cancel</a>(task_id) -> None</code>
- <code title="get /task/{task_id}">client.task.<a href="./src/chunkr_ai/resources/task/task.py">get</a>(task_id, \*\*<a href="src/chunkr_ai/types/task_get_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task/task.py">Task</a></code>

## Parse

Methods:

- <code title="post /task/parse">client.task.parse.<a href="./src/chunkr_ai/resources/task/parse.py">create</a>(\*\*<a href="src/chunkr_ai/types/task/parse_create_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task/task.py">Task</a></code>
- <code title="patch /task/{task_id}/parse">client.task.parse.<a href="./src/chunkr_ai/resources/task/parse.py">update</a>(task_id, \*\*<a href="src/chunkr_ai/types/task/parse_update_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task/task.py">Task</a></code>

# Health

Types:

```python
from chunkr_ai.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/chunkr_ai/resources/health.py">check</a>() -> str</code>
