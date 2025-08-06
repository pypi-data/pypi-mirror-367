from typing import List, Optional, Union

from rich.table import Table
from sqlmodel import select

from ...core.constants import RecoverableToolError, allow_unused, user_only_tool
from ...core.ctx import ElroyContext
from ...db.db_models import Goal
from ...utils.clock import db_time_to_local


def get_active_goals(ctx: ElroyContext) -> List[Goal]:
    """
    Retrieve active goals for a given user.

    Args:
        session (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[Goal]: A list of active goals.
    """
    return list(get_goals(ctx, True))


def get_goals(ctx: ElroyContext, active: bool):
    return ctx.db.exec(
        select(Goal)
        .where(
            Goal.user_id == ctx.user_id,
            Goal.is_active == active,
        )
        .order_by(Goal.priority)  # type: ignore
    ).all()


def get_db_goal_by_name(ctx: ElroyContext, name: str) -> Optional[Goal]:
    return ctx.db.exec(
        select(Goal).where(
            Goal.user_id == ctx.user_id,
            Goal.name == name,
            Goal.is_active == True,
        )
    ).first()


def get_active_goal_names(ctx: ElroyContext) -> List[str]:
    """Gets the list of names for all active goals

    Returns:
        List[str]: List of names for all active goals
    """

    return [goal.name for goal in get_active_goals(ctx)]


@allow_unused
def get_goal_by_name(ctx: ElroyContext, goal_name: str) -> Optional[str]:
    """Get the fact for a goal by name

    Args:
        ctx (ElroyContext): context obj
        goal_name (str): Name of the goal

    Returns:
        Optional[str]: The fact for the goal with the given name
    """
    goal = get_db_goal_by_name(ctx, goal_name)
    if goal:
        return goal.to_fact()
    else:
        raise RecoverableToolError(f"Goal '{goal_name}' not found")


@user_only_tool
def print_active_goals(ctx: ElroyContext, n: Optional[int] = None) -> Union[str, Table]:
    """Prints the last n active goals. If n is None, prints all active goals.

    Args:
        n (Optional[int], optional): Number of goals to print. Defaults to None.

    """

    return _print_goals(ctx, True, n)


@user_only_tool
def print_complete_goals(ctx: ElroyContext, n: Optional[int] = None) -> Union[str, Table]:
    """Prints the last n complete goals. If n is None, prints all complete goals.

    Args:
        n (Optional[int], optional): Number of goals to print. Defaults to None.

    """
    return _print_goals(ctx, False, n)


def _print_goals(ctx: ElroyContext, active: bool, n: Optional[int] = None) -> Union[Table, str]:
    """Prints the last n active goals. If n is None, prints all active goals.

    Args:
        ctx (ElroyContext): context obj
        n (Optional[int], optional): Number of goals to print. Defaults to None.
    """
    # sort by priority, last update time
    goals = sorted(get_goals(ctx, active), key=lambda g: (g.priority, g.updated_at), reverse=True)

    if not goals:
        return "No goals found."

    title = "Active Goals" if active else "Complete Goals"
    table = Table(title=title, show_lines=True)
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Priority", justify="left", style="green")
    table.add_column("Last Updated At", justify="left", style="green")
    table.add_column("Description", justify="left", style="green")
    table.add_column("Strategy", justify="left", style="green")
    table.add_column("End Condition", justify="left", style="green")
    table.add_column("Target Completion Time", justify="left", style="green")
    table.add_column("Status Updates", justify="left", style="green")

    for goal in goals[:n]:
        table.add_row(
            goal.name,
            str(goal.priority),
            db_time_to_local(goal.updated_at).strftime("%Y-%m-%d %H:%M:%S"),
            goal.description,
            goal.strategy,
            goal.end_condition,
            db_time_to_local(goal.target_completion_time).strftime("%Y-%m-%d %H:%M:%S") if goal.target_completion_time else None,
            "\n".join(goal.get_status_updates()),
        )
    return table
