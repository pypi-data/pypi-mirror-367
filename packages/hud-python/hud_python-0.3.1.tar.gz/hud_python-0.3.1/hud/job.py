from __future__ import annotations

import asyncio
import functools
import inspect
import logging
import sys
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar, cast

from pydantic import BaseModel, PrivateAttr, TypeAdapter

import hud.server
from hud import Response, gym
from hud.agent import ResponseAgent
from hud.settings import settings
from hud.task import Task
from hud.taskset import TaskSet
from hud.trajectory import Trajectory
from hud.utils.progress import StepProgressTracker

if TYPE_CHECKING:
    from hud.adapters.common import Adapter
    from hud.agent.base import Agent
    from hud.utils.common import Observation

logger = logging.getLogger("hud.job")

# Type variable for the decorator
T = TypeVar("T", bound=Callable)

# Global registry to store active jobs created by decorators
_ACTIVE_JOBS = {}


class Job(BaseModel):
    """
    A job represents a collection of related trajectories.
    It holds metadata and provides methods to interact with job data.
    Instances should typically be obtained via `create_job`, `load_job`, or the new `run_job`.
    """

    id: str
    name: str
    metadata: dict[str, Any] | None = None
    created_at: datetime
    status: str

    # Internal cache for trajectories
    _trajectories: list[Trajectory] | None = PrivateAttr(default=None)
    # Store execution errors for debugging
    errors: list[dict[str, Any]] = []

    async def load_trajectories(
        self, *, api_key: str | None = None, force_reload: bool = False
    ) -> list[Trajectory]:
        """
        Loads the trajectories associated with this job.
        Uses cached results unless force_reload is True.

        Args:
            api_key: Optional API key.
            force_reload: If True, fetches trajectories from the API even if cached.

        Returns:
            List[Trajectory]: The trajectories in the job
        """
        if self._trajectories is not None and not force_reload:
            logger.debug("Returning cached trajectories for Job %s", self.id)
            return self._trajectories

        logger.debug("Fetching trajectories for Job %s from API...", self.id)
        api_key = api_key or settings.api_key

        try:
            data = await hud.server.make_request(
                method="GET",
                url=f"{settings.base_url}/v2/jobs/{self.id}/trajectories",
                api_key=api_key,
            )
            self._trajectories = TypeAdapter(list[Trajectory]).validate_python(data)
            logger.debug("Loaded %d trajectories for Job %s", len(self._trajectories), self.id)
            return self._trajectories
        except Exception as e:
            logger.exception("Failed to load trajectories for Job %s: %s", self.id, e)
            self._trajectories = None  # Ensure cache is cleared on error
            return []  # Return empty list on error

    async def get_analytics(self, *, force_reload: bool = False) -> dict[str, Any]:
        """
        Calculates and returns analytics for the job based on its trajectories.

        Args:
            force_reload: If True, re-fetches trajectories before calculating.

        Returns:
            Dictionary containing analytics (e.g., task_count, avg_reward).
        """
        trajectories = await self.load_trajectories(force_reload=force_reload)

        task_count = len(trajectories)
        if task_count == 0:
            return {"task_count": 0, "avg_reward": None, "success_rate": None}  # Or other default

        total_reward = 0
        successful_tasks = 0
        valid_rewards = 0

        for traj in trajectories:
            # Example: Assume reward is numeric and success is reward >= 1.0
            # Adjust based on actual trajectory data structure and evaluation logic
            if isinstance(traj.reward, int | float):
                total_reward += traj.reward
                valid_rewards += 1
                if traj.reward >= 1.0:
                    successful_tasks += 1
            # Add more complex logic here if needed based on traj.evaluation_result or metadata

        avg_reward = (total_reward / valid_rewards) if valid_rewards > 0 else None
        success_rate = (successful_tasks / task_count) * 100 if task_count > 0 else None

        return {
            "task_count": task_count,
            "avg_reward": avg_reward,
            "success_rate": success_rate,
            # Add other relevant stats here
        }


async def create_job(
    name: str,
    gym_id: str | None = None,
    evalset_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Job:
    """
    Creates a new job.

    Args:
        name: The name of the job
        metadata: Metadata for the job

    Returns:
        Job: The created job instance
    """
    api_key = settings.api_key
    metadata = metadata or {}

    data = await hud.server.make_request(
        method="POST",
        url=f"{settings.base_url}/v2/jobs",
        json={
            "name": name,
            "metadata": metadata,
            "gym_id": gym_id,
            "evalset_id": evalset_id,
        },
        api_key=api_key,
    )

    # Assume the backend API returns the full job data upon creation
    # or at least the necessary fields (id, name, metadata, created_at, status)
    # If not, we might need to make a subsequent GET request
    job_data = data  # Adjust if the API response structure is different

    created_at = datetime.fromisoformat(job_data["created_at"].replace("Z", "+00:00"))

    logger.info("View job at https://app.hud.so/jobs/%s.", job_data["id"])

    return Job(
        id=job_data["id"],
        name=job_data["name"],
        metadata=job_data.get("metadata", {}),  # Ensure metadata is dict
        created_at=created_at,  # Parse datetime
        status=job_data["status"],
    )


async def load_job(job_id: str, api_key: str | None = None) -> Job:
    """
    Retrieves a job by its ID.

    Args:
        job_id: The ID of the job to retrieve

    Returns:
        Job: The retrieved job instance
    """
    api_key = api_key or settings.api_key

    data = await hud.server.make_request(
        method="GET",
        url=f"{settings.base_url}/v2/jobs/{job_id}",
        api_key=api_key,
    )

    if not data:
        raise ValueError(f"Job {job_id} not found")

    # Validate and create the Job instance from the fetched data
    return Job.model_validate(data)


def job(name: str, metadata: dict[str, Any] | None = None) -> Callable[[T], T]:
    """
    Decorator to automatically create and associate a job with all environments
    created within the decorated function.

    Args:
        name: The name of the job
        metadata: Additional metadata for the job

    Returns:
        A decorator function that creates a job and associates it with environments
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a job for this function call using the new function
            job = await create_job(name=name, metadata=metadata)

            # Store in global registry with a unique key based on function and call
            call_id = f"{func.__module__}.{func.__qualname__}_{id(wrapper)}"
            _ACTIVE_JOBS[call_id] = job

            try:
                # Add the function's frame to the stack for lookup
                frame = inspect.currentframe()
                if frame:
                    frame.f_locals["_job_call_id"] = call_id

                # Run the decorated function
                result = await func(*args, **kwargs)
                return result
            finally:
                # Clean up
                _ACTIVE_JOBS.pop(call_id, None)

        return cast("T", wrapper)

    return decorator


def get_active_job() -> Job | None:
    """
    Get the currently active job from the call stack, if any.
    Used internally by gym.make to automatically associate environments with jobs.

    Returns:
        The active job or None if no job is active
    """
    # Walk up the stack to find any frame with _job_call_id
    frame = inspect.currentframe()
    while frame:
        if "_job_call_id" in frame.f_locals:
            call_id = frame.f_locals["_job_call_id"]
            if call_id in _ACTIVE_JOBS:
                return _ACTIVE_JOBS[call_id]
        frame = frame.f_back

    return None


async def _maybe_resample_action(
    obs: Observation, action: Any, response_agent: ResponseAgent
) -> tuple[Observation, bool]:
    if isinstance(action, Response):
        action = action.model_dump()
    if isinstance(action, dict) and action.get("type") == "response":
        response_text = action.get("text", "")
        if response_agent and response_text:
            try:
                decision = await response_agent.determine_response(response_text)
                if decision == "CONTINUE":
                    logger.info("ResponseAgent indicated CONTINUE. for message: %s", response_text)
                    obs.text = "Yes, please continue."
                    return obs, False
                else:
                    logger.warning("ResponseAgent indicated STOP for message: %s", response_text)
            except Exception as e:
                logger.warning("Error using ResponseAgent: %s", e)
    return obs, True


async def _execute_task(
    agent_cls: type[Agent],
    adapter_cls: type[Adapter] | None,
    agent_kwargs: dict[str, Any] | None,
    adapter_kwargs: dict[str, Any] | None,
    task: Task,
    job_name: str,
    task_id: str,
    max_steps_per_task: int,
    job: Job,
    tracker: StepProgressTracker | None = None,
    auto_reply_question: bool = False,
    # Use semaphores instead of rate limiter
    env_creation_semaphore: asyncio.Semaphore | None = None,
    agent_predict_semaphore: asyncio.Semaphore | None = None,
) -> None:
    """Helper function to instantiate/run/evaluate a single task, with concurrency limits via
    semaphores."""
    if tracker:
        tracker.start_task(task_id)
    env = None
    agent_instance: Agent | None = None
    status = "error"
    error_msg = "Initialization failed"
    try:
        response_agent = ResponseAgent() if auto_reply_question else None

        adapter_instance = None
        if adapter_cls:
            adapter_instance = adapter_cls(**(adapter_kwargs or {}))
        agent_instance = agent_cls(
            adapter=adapter_instance,
            **(agent_kwargs or {}),
        )
        if agent_instance is None:
            raise RuntimeError("Agent could not be instantiated")

        agent_name = agent_instance.name
        logger.info("Using agent: %s", agent_name)
        if task.metadata is None or not isinstance(task.metadata, dict):
            task.metadata = {}
        task.metadata["agent_name"] = agent_name

        # Environment creation with semaphore
        if env_creation_semaphore:
            async with env_creation_semaphore:
                env = await gym.make(task, job=job)
        else:
            env = await gym.make(task, job=job)

        if not env:
            raise ValueError(f"Environment creation failed for task {task_id}")

        obs_tuple = await env.reset()
        if obs_tuple is None:
            raise ValueError(f"env.reset() returned None for task {task_id}")
        obs, _ = obs_tuple

        step_error = None

        resampled_actions = 0

        for step in range(max_steps_per_task):
            action, done = (None, False)
            try:
                # Agent prediction with semaphore
                try:
                    if agent_predict_semaphore:
                        async with agent_predict_semaphore:
                            action, done = await agent_instance.predict(obs)
                    else:
                        action, done = await agent_instance.predict(obs)
                except Exception as e:
                    # if agent prediction fails, pass back the error to the agent
                    logger.exception("[TR: %s] Agent prediction failed: %s", task_id, e)
                    resampled_actions += 1
                    if resampled_actions > 5:
                        logger.warning(
                            "[TR: %s] Resampled action %d times. Stopping.",
                            task_id,
                            resampled_actions,
                        )
                        break
                    continue

                if tracker:
                    tracker.increment_step(task_id)

                finish = False
                if done and response_agent and action and len(action) > 0:
                    obs, finish = await _maybe_resample_action(obs, action[-1], response_agent)
                    resampled_actions += 1
                    if resampled_actions > 5:
                        logger.warning(
                            "[TR: %s] Resampled action %d times. Stopping.",
                            task_id,
                            resampled_actions,
                        )
                        break
                    if not finish:
                        continue

                step_result = await env.step(action)
                if step_result is None:
                    terminated = True
                else:
                    obs, _, terminated, _ = step_result
                if terminated or done or finish:
                    break

            except Exception as agent_step_err:
                logger.exception(
                    "[TR: %s] Step %d Error: %s",
                    task_id,
                    step + 1,
                    agent_step_err,
                )
                step_error = f"Error at step {step + 1}: {agent_step_err}"
                # Store step error in job
                job.errors.append(
                    {
                        "task_id": task_id,
                        "type": "step_error",
                        "step": step + 1,
                        "error": str(agent_step_err),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                continue
        else:
            logger.warning("[TR: %s] Max steps reached.", task_id)

        # --- Evaluate Task ---
        evaluation_result = None
        if step_error:
            status = "error"
            error_msg = step_error
        else:
            try:
                evaluation_result = await env.evaluate()
                status = "completed"
                error_msg = None
                # logger.info("Evaluation result: %s", evaluation_result)
            except Exception as eval_err:
                logger.exception(
                    "[TR: %s] Evaluation Error: %s",
                    task_id,
                    eval_err,
                )
                status = "error"
                error_msg = f"Evaluation failed: {eval_err}"
                # Store evaluation error in job
                job.errors.append(
                    {
                        "task_id": task_id,
                        "type": "evaluation_error",
                        "error": str(eval_err),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    except Exception as e:
        logger.exception("[TR: %s] Setup/Run Error: %s", task_id, e)
        status = "error"
        error_msg = str(e)
        # Store setup/initialization error in job
        job.errors.append(
            {
                "task_id": task_id,
                "type": "setup_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )

    finally:
        if tracker:
            tracker.finish_task(task_id)
        if env:
            try:
                await env.close()
            except Exception as close_err:
                logger.exception("[TR: %s] Close Error: %s", task_id, close_err)
                # Store environment close error in job
                job.errors.append(
                    {
                        "task_id": task_id,
                        "type": "env_close_error",
                        "error": str(close_err),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    log_suffix = f" Error: {error_msg}" if status == "error" else f" Eval: {evaluation_result}"
    logger.info(
        "[TR: %s] Finished local execution. Status: %s.%s",
        task_id,
        status,
        log_suffix,
    )


async def _progress_monitor(tracker: StepProgressTracker, interval: float = 1.0) -> None:
    """Coroutine to periodically display progress using the tracker."""
    try:
        while not tracker.is_finished():
            sys.stderr.write(f"\r{tracker.display()}")
            sys.stderr.flush()
            await asyncio.sleep(interval)
        sys.stderr.write(f"\r{tracker.display()}\n")
        sys.stderr.flush()
        logger.debug("Progress monitor finished.")
    except asyncio.CancelledError:
        sys.stderr.write("\nProgress monitor cancelled.\n")
        sys.stderr.flush()
        logger.debug("Progress monitor cancelled.")
    except Exception as e:
        sys.stderr.write(f"\nProgress monitor error: {e}\n")
        sys.stderr.flush()
        logger.exception("Progress monitor error: %s", e)


# --- New run_job function ---


async def run_job(
    agent_cls: type[Agent],
    task_or_taskset: Task | TaskSet,
    job_name: str,
    auto_reply_question: bool = False,
    adapter_cls: type[Adapter] | None = None,
    agent_kwargs: dict[str, Any] | None = None,
    adapter_kwargs: dict[str, Any] | None = None,
    max_steps_per_task: int = 20,
    run_parallel: bool = True,
    job_metadata: dict[str, Any] | None = None,
    show_progress: bool = True,
    verbose: bool = False,
    # Concurrency control with semaphores
    max_concurrent_env_creations: int | None = 30,  # Limits gym.make calls
    max_concurrent_agent_predictions: int | None = None,  # No limit on LLM calls
    max_concurrent_tasks: int | None = 30,  # Limits overall task concurrency
) -> Job:
    """
    Creates Job, executes tasks locally, linking them to the Job.
    Instantiates agent/adapter per task. Shows step-based progress.

    Controls concurrency in three ways:
    1. Limits concurrent environment creations
    2. Limits concurrent agent predictions
    3. Limits overall concurrent tasks (when run_parallel=True)

    All concurrency controls use semaphores for reliability.
    Tracks all errors that occur during execution in job.errors.

    Args:
        agent_cls: Agent class to instantiate.
        task_or_taskset: Task or TaskSet to run.
        job_name: Name for the Job.
        adapter_cls: Optional Adapter class.
        agent_kwargs: Optional kwargs for agent constructor.
        adapter_kwargs: Optional kwargs for adapter constructor.
        max_steps_per_task: Step limit per task.
        run_parallel: Run TaskSet tasks concurrently if True (limited by max_concurrent_tasks).
        job_metadata: Metadata for the created Job.
        show_progress: Display the step-based progress tracker.
        max_concurrent_env_creations: Max concurrent environment creation calls.
        max_concurrent_agent_predictions: Max concurrent agent prediction calls.
        max_concurrent_tasks: Max number of tasks to run actively at the same time.

    Returns:
        The created Job object with errors stored in job.errors.
    """

    tasks_to_run: list[Task] = []
    created_job: Job | None = None

    # Get hud logger
    if not verbose:
        logger = logging.getLogger("hud")
        logger.setLevel(logging.CRITICAL)
    logger = logging.getLogger("hud.job")

    evalset_id = None
    if isinstance(task_or_taskset, TaskSet):
        evalset_id = task_or_taskset.id
        task_or_taskset.fit(agent_cls)

    gym_id = None
    if isinstance(task_or_taskset, Task):
        gym_id = task_or_taskset.gym if isinstance(task_or_taskset.gym, str) else None
    elif isinstance(task_or_taskset, TaskSet):
        gym_id = (
            task_or_taskset.tasks[0].gym if isinstance(task_or_taskset.tasks[0].gym, str) else None
        )

    # --- Create Job ---
    try:
        logger.info("Creating job with name: '%s'", job_name)
        created_job = await create_job(
            name=job_name,
            metadata=job_metadata,
            evalset_id=evalset_id,
            gym_id=gym_id,
        )
        # logger.info("Created job with ID: %s", created_job.id)
    except Exception as e:
        logger.exception("Failed to create job '%s': %s", job_name, e)
        raise

    # --- Task Setup ---
    is_taskset = isinstance(task_or_taskset, TaskSet)
    if is_taskset:
        tasks_to_run = task_or_taskset.tasks if task_or_taskset.tasks else []
    elif isinstance(task_or_taskset, Task):
        tasks_to_run = [task_or_taskset]
        run_parallel = False
    else:
        raise TypeError("task_or_taskset must be either a Task or a TaskSet")

    if not tasks_to_run:
        logger.warning("Job '%s' (%s): No tasks found to run.", created_job.name, created_job.id)
        return created_job

    task_ids = [(str(task.id) if task.id else f"task_{i}") for i, task in enumerate(tasks_to_run)]
    num_tasks = len(tasks_to_run)

    # --- Create semaphores for concurrency control ---
    env_creation_sema = None
    if max_concurrent_env_creations and max_concurrent_env_creations > 0:
        env_creation_sema = asyncio.Semaphore(max_concurrent_env_creations)
        logger.info(
            "Limiting concurrent environment creations to %d.", max_concurrent_env_creations
        )

    agent_predict_sema = None
    if max_concurrent_agent_predictions and max_concurrent_agent_predictions > 0:
        agent_predict_sema = asyncio.Semaphore(max_concurrent_agent_predictions)
        logger.info(
            "Limiting concurrent agent predictions to %d.", max_concurrent_agent_predictions
        )
    else:
        logger.info("No limit on concurrent agent predictions.")

    task_execution_sema = None
    effective_concurrency = num_tasks  # Default to running all if parallel
    if run_parallel and max_concurrent_tasks and max_concurrent_tasks > 0:
        effective_concurrency = min(num_tasks, max_concurrent_tasks)
        task_execution_sema = asyncio.Semaphore(effective_concurrency)
        logger.info("Limiting concurrent task executions to %d.", effective_concurrency)
    elif not run_parallel:
        effective_concurrency = 1  # Sequential means concurrency of 1

    # --- Instantiate Tracker & Start Monitor ---
    tracker = None
    monitor_task = None
    if show_progress and num_tasks > 0:
        tracker = StepProgressTracker(total_tasks=num_tasks, max_steps_per_task=max_steps_per_task)
        monitor_task = asyncio.create_task(_progress_monitor(tracker))

    # --- Execute Tasks ---
    job_desc_suffix = f" (Job ID: {created_job.id})"

    async def task_wrapper(task_coro: Coroutine, semaphore: asyncio.Semaphore | None) -> None:
        if semaphore:
            async with semaphore:
                await task_coro
        else:
            await task_coro

    try:
        if run_parallel and is_taskset:
            logger.info(
                "Job '%s'%s: Running %d tasks with concurrency %d.",
                created_job.name,
                job_desc_suffix,
                num_tasks,
                effective_concurrency,
            )

            task_coroutines = [
                _execute_task(
                    agent_cls=agent_cls,
                    adapter_cls=adapter_cls,
                    agent_kwargs=agent_kwargs,
                    adapter_kwargs=adapter_kwargs,
                    task=task,
                    job_name=created_job.name,
                    task_id=task_id,
                    max_steps_per_task=max_steps_per_task,
                    job=created_job,
                    tracker=tracker,
                    env_creation_semaphore=env_creation_sema,
                    agent_predict_semaphore=agent_predict_sema,
                    auto_reply_question=auto_reply_question,
                )
                for task, task_id in zip(tasks_to_run, task_ids, strict=True)
            ]

            # Wrap coroutines with semaphore management if limiting concurrency
            wrapped_tasks = [
                task_wrapper(coro, task_execution_sema) for i, coro in enumerate(task_coroutines)
            ]

            # Run all wrapped tasks
            await asyncio.gather(*wrapped_tasks)

        else:
            # SEQUENTIAL (or single task)
            logger.info(
                "Job '%s'%s: Running %d tasks sequentially.",
                created_job.name,
                job_desc_suffix,
                num_tasks,
            )
            for i, task in enumerate(tasks_to_run):
                task_id = task_ids[i]
                await _execute_task(
                    agent_cls=agent_cls,
                    adapter_cls=adapter_cls,
                    agent_kwargs=agent_kwargs,
                    adapter_kwargs=adapter_kwargs,
                    task=task,
                    job_name=created_job.name,
                    task_id=task_id,
                    max_steps_per_task=max_steps_per_task,
                    job=created_job,
                    tracker=tracker,
                    env_creation_semaphore=env_creation_sema,
                    agent_predict_semaphore=agent_predict_sema,
                    auto_reply_question=auto_reply_question,
                )

    finally:
        # Ensure monitor task is stopped and awaited cleanly
        if monitor_task is not None and not monitor_task.done():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error("Error awaiting progress monitor task: %s", e)

    logger.info(
        "Job '%s'%s finished local execution phase for %d tasks.",
        created_job.name,
        job_desc_suffix,
        num_tasks,
    )
    return created_job


"""
c7f85f7d-3730-4c9a-85a3-a1dc436c3bd2


de12c3cc-9d9c-4e90-82cc-1d71d30ede54
59104743-0a63-4569-a8b5-1eda1a1b55ac
ff759429-056c-4cde-8851-11e26729ff03


7b98ea22-e243-4eeb-a6db-79f4a76da2b3

7aad3f7b-d74f-470d-826d-d817f95fdd67

e356ede6-074a-49ef-9fcd-69e5bcfbdec9

26cd1192-3991-4d1b-b599-b2bed1bcb606

31ece277-970f-4763-b0c8-bf19a56f56c7


f9b722a0-5f33-466b-bce0-8ece101f2bc6
33d1af33-8952-4945-b901-229bcfd88354

6c3d6557-e745-44ab-bc10-300180a81c79
6c3d6557-e745-44ab-bc10-300180a81c79
502e02b5-9939-4e57-91af-4fcbcb90a979

7aad3f7b-d74f-470d-826d-d817f95fdd67


31ece277-970f-4763-b0c8-bf19a56f56c7


e356ede6-074a-49ef-9fcd-69e5bcfbdec9"""
