"""Cancel command - Terminate running GPU tasks.

This module implements the cancel command for the Flow CLI. It allows users to
terminate running tasks gracefully, with optional confirmation prompts.

Examples:
    # Cancel a specific task
    $ flow cancel my-training-job

    # Cancel last task from status (using index)
    $ flow cancel :1

    # Cancel all dev tasks without confirmation
    $ flow cancel --name-pattern "dev-*" --yes

Command Usage:
    flow cancel TASK_ID_OR_NAME [OPTIONS]

The command will:
- Verify the task exists and is cancellable
- Prompt for confirmation (unless --yes is used)
- Send cancellation request to the provider
- Display cancellation status

Note:
    Only tasks in 'pending' or 'running' state can be cancelled.
    Completed or failed tasks cannot be cancelled.
"""

import click
import fnmatch
import re

from flow import Flow
from flow.api.models import Task, TaskStatus
from flow.errors import AuthenticationError

from ..utils.task_formatter import TaskFormatter
from ..utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from .base import BaseCommand, console


class CancelCommand(BaseCommand, TaskOperationCommand):
    """Cancel a running task."""

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "cancel"

    @property
    def help(self) -> str:
        return "Cancel GPU tasks - use quotes for wildcards: flow cancel -n 'task-*'"

    def get_command(self) -> click.Command:
        # Import completion function
        from ..utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
        @click.option("--all", is_flag=True, help="Cancel all running tasks")
        @click.option(
            "--name-pattern", "-n", 
            help="Cancel tasks matching pattern. IMPORTANT: Quote wildcards to prevent shell expansion (e.g., 'task-*')"
        )
        @click.option("--regex", is_flag=True, help="Treat pattern as regex instead of wildcard")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and patterns")
        def cancel(
            task_identifier: str | None, yes: bool, all: bool, name_pattern: str | None, regex: bool, verbose: bool
        ):
            """Cancel a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow cancel                       # Interactive task selector
                flow cancel my-training           # Cancel by name
                flow cancel task-abc123           # Cancel by ID
                flow cancel -n 'gpu-test-*' --yes # Cancel pattern (QUOTE THE WILDCARD!)
                flow cancel --all --yes           # Cancel all running tasks

            IMPORTANT: When using wildcards with -n/--name-pattern, you MUST quote them:
                CORRECT:   flow cancel -n 'dev-*'
                WRONG:     flow cancel -n dev-*     (shell will expand * as files)

            Use 'flow cancel --verbose' for advanced pattern matching examples.
            """
            if verbose:
                console.print("\n[bold red]⚠️  CRITICAL: Shell Wildcard Handling[/bold red]\n")
                console.print("[yellow]Wildcards (* and ?) MUST be quoted or escaped to prevent shell expansion:[/yellow]")
                console.print("  [green]✓ CORRECT:[/green]  flow cancel -n 'gpu-test-*'        # Single quotes")
                console.print("  [green]✓ CORRECT:[/green]  flow cancel -n \"gpu-test-*\"       # Double quotes")
                console.print("  [green]✓ CORRECT:[/green]  flow cancel -n gpu-test-\\*        # Backslash escape")
                console.print("  [red]✗ WRONG:[/red]    flow cancel -n gpu-test-*          # Shell tries to match files!\n")
                
                console.print("[bold]Pattern-based cancellation:[/bold]")
                console.print("  flow cancel --name-pattern 'dev-*'      # Cancel all dev tasks")
                console.print("  flow cancel -n 'train-v*' --yes         # Skip confirmation")
                console.print("  flow cancel -n '*-gpu-8x*'              # Match GPU type")
                console.print("  flow cancel -n 'gpu-test-'              # Partial match (no wildcard needed)\n")
                
                console.print("[bold]Regex patterns:[/bold]")
                console.print("  flow cancel -n '.*-v[0-9]+' --regex     # Version pattern")
                console.print("  flow cancel -n '^test-.*-2024' --regex  # Complex matching")
                console.print("  flow cancel -n '^gpu-test-' --regex     # Starts with gpu-test-\n")
                
                console.print("[bold]Batch operations:[/bold]")
                console.print("  flow cancel --all                       # Cancel all (with confirmation)")
                console.print("  flow cancel --all --yes                 # Force cancel all\n")
                
                console.print("[bold]Shell-specific tips:[/bold]")
                console.print("  • zsh/bash: Use single quotes 'pattern*' to prevent expansion")
                console.print("  • If you see 'no matches found', your shell expanded the wildcard")
                console.print("  • Alternative: Disable globbing with 'set -f' before command\n")
                
                console.print("[bold]Common workflows:[/bold]")
                console.print("  • Cancel all GPU test tasks: flow cancel -n 'gpu-test-*' --yes")
                console.print("  • Clean up dev tasks: flow cancel -n 'dev-*' --yes")
                console.print("  • Cancel specific prefix: flow cancel -n 'training-v2-' --yes\n")
                return
                
            self._execute(task_identifier, yes, all, name_pattern, regex)

        return cancel

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show cancellable tasks."""
        return TaskFilter.cancellable

    def get_selection_title(self) -> str:
        return "Select a task to cancel"

    def get_no_tasks_message(self) -> str:
        return "No running tasks to cancel"

    # Command execution
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute cancellation on the selected task."""
        yes = kwargs.get("yes", False)

        # Double-check task is still cancellable
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            status_str = str(task.status).replace("TaskStatus.", "").lower()
            console.print(
                f"[yellow]Task '{task.name or task.task_id}' is already {status_str}[/yellow]"
            )
            return

        # Show beautiful confirmation with task details
        if not yes:
            self._show_cancel_confirmation(task)

            # Simple, focused confirmation prompt
            if not click.confirm("\nProceed with cancellation?", default=False):
                console.print("[dim]Cancellation aborted[/dim]")
                return

        # Show progress
        from ..utils.animated_progress import AnimatedEllipsisProgress

        with AnimatedEllipsisProgress(
            console, "Cancelling task", start_immediately=True
        ) as progress:
            client.cancel(task.task_id)

        # Success message
        console.print(
            f"\n[green]✓[/green] Successfully cancelled [bold]{task.name or task.task_id}[/bold]"
        )

        # Show next actions
        self.show_next_actions(
            [
                "View all tasks: [cyan]flow status[/cyan]",
                "Submit a new task: [cyan]flow run task.yaml[/cyan]",
            ]
        )

    def _show_cancel_confirmation(self, task: Task) -> None:
        """Show a beautiful confirmation panel with task details."""
        from datetime import datetime, timezone

        from rich.panel import Panel
        from rich.table import Table

        from ..utils.time_formatter import TimeFormatter

        time_fmt = TimeFormatter()

        # Create a clean table for task details
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        # Task name
        table.add_row("Task", task.name or "Unnamed task")

        # GPU type
        table.add_row("GPU", task.instance_type)

        # Status
        status_display = self.task_formatter.format_status_with_color(task.status.value)
        table.add_row("Status", status_display)

        # Duration and cost
        duration = time_fmt.calculate_duration(task)
        table.add_row("Duration", duration)

        # Calculate approximate cost if available
        if (
            hasattr(task, "price_per_hour")
            and task.price_per_hour
            and task.status == TaskStatus.RUNNING
        ):
            if task.started_at:
                start = task.started_at
                if hasattr(start, "tzinfo") and start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                hours_run = (now - start).total_seconds() / 3600
                cost_so_far = hours_run * task.price_per_hour

                table.add_row("Cost so far", f"${cost_so_far:.2f}")
                table.add_row("Hourly rate", f"${task.price_per_hour:.2f}/hr")

        # Create panel with warning color
        panel = Panel(
            table,
            title="[bold red]⚠  Cancel Task[/bold red]",
            title_align="center",
            border_style="yellow",
            padding=(1, 2),
        )

        console.print()
        console.print(panel)

    def _execute(
        self,
        task_identifier: str | None,
        yes: bool,
        all: bool,
        name_pattern: str | None,
        regex: bool,
    ) -> None:
        """Execute the cancel command."""
        if all:
            self._execute_cancel_all(yes)
        elif name_pattern:
            self._execute_cancel_pattern(name_pattern, yes, regex)
        else:
            self.execute_with_selection(task_identifier, yes=yes)

    def _execute_cancel_all(self, yes: bool) -> None:
        """Handle --all flag separately as it's a special case."""
        from ..utils.animated_progress import AnimatedEllipsisProgress

        try:
            # Start animation immediately
            with AnimatedEllipsisProgress(
                console, "Finding all cancellable tasks", start_immediately=True
            ) as progress:
                client = Flow()

                # Get cancellable tasks using TaskFetcher for consistent behavior
                from ..utils.task_fetcher import TaskFetcher

                fetcher = TaskFetcher(client)
                all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
                cancellable = TaskFilter.cancellable(all_tasks)

            if not cancellable:
                console.print("[yellow]No running tasks to cancel[/yellow]")
                return

            # Confirm
            if not yes:
                if not click.confirm(f"Cancel {len(cancellable)} running tasks?"):
                    console.print("Cancelled")
                    return

            # Cancel each task with progress
            from ..utils.animated_progress import AnimatedEllipsisProgress

            cancelled_count = 0
            failed_count = 0

            with AnimatedEllipsisProgress(
                console, f"Cancelling {len(cancellable)} tasks", start_immediately=True
            ) as progress:
                for i, task in enumerate(cancellable):
                    task_name = task.name or task.task_id
                    progress.base_message = f"Cancelling {task_name} ({i+1}/{len(cancellable)})"

                    try:
                        client.cancel(task.task_id)
                        cancelled_count += 1
                    except Exception as e:
                        console.print(f"[red]✗[/red] Failed to cancel {task_name}: {e}")
                        failed_count += 1

            # Summary
            console.print()
            if cancelled_count > 0:
                console.print(f"[green]✓[/green] Successfully cancelled {cancelled_count} task(s)")
            if failed_count > 0:
                console.print(f"[red]✗[/red] Failed to cancel {failed_count} task(s)")

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [cyan]flow status[/cyan]",
                    "Submit a new task: [cyan]flow run task.yaml[/cyan]",
                ]
            )

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))

    def _execute_cancel_pattern(self, pattern: str, yes: bool, use_regex: bool) -> None:
        """Cancel tasks matching a name pattern."""
        from ..utils.animated_progress import AnimatedEllipsisProgress

        try:
            # Start animation immediately
            with AnimatedEllipsisProgress(
                console, f"Finding tasks matching: {pattern}", start_immediately=True
            ) as progress:
                client = Flow()

                # Get cancellable tasks
                from ..utils.task_fetcher import TaskFetcher

                fetcher = TaskFetcher(client)
                all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
                cancellable = TaskFilter.cancellable(all_tasks)

            if not cancellable:
                console.print("[yellow]No running tasks to cancel[/yellow]")
                return

            # Filter by pattern
            matching_tasks = []
            for task in cancellable:
                if task.name:
                    if use_regex:
                        try:
                            if re.search(pattern, task.name):
                                matching_tasks.append(task)
                        except re.error as e:
                            console.print(f"[red]Invalid regex pattern: {e}[/red]")
                            return
                    else:
                        # Use fnmatch for wildcard matching
                        if fnmatch.fnmatch(task.name, pattern):
                            matching_tasks.append(task)

            if not matching_tasks:
                console.print(f"[yellow]No running tasks match pattern '{pattern}'[/yellow]")
                
                # Help users debug common issues
                if '*' in pattern or '?' in pattern:
                    console.print("\n[dim]Tip: If you're seeing this after shell expansion failed,")
                    console.print("     make sure to quote your pattern: flow cancel -n 'pattern*'[/dim]")
                
                # Show what tasks ARE available
                sample_names = [t.name for t in cancellable[:5] if t.name]
                if sample_names:
                    console.print(f"\n[dim]Available task names: {', '.join(sample_names)}"
                                f"{' ...' if len(cancellable) > 5 else ''}[/dim]")
                return

            # Show matching tasks
            console.print(
                f"\n[bold]Found {len(matching_tasks)} task(s) matching pattern '[cyan]{pattern}[/cyan]':[/bold]\n"
            )
            from rich.table import Table

            table = Table(show_header=True, box=None)
            table.add_column("Task Name", style="cyan")
            table.add_column("Task ID", style="dim")
            table.add_column("Status")
            table.add_column("GPU Type")

            for task in matching_tasks:
                status_display = self.task_formatter.format_status_with_color(task.status.value)
                table.add_row(
                    task.name or "Unnamed",
                    task.task_id[:12] + "...",
                    status_display,
                    task.instance_type,
                )

            console.print(table)
            console.print()

            # Confirm
            if not yes:
                if not click.confirm(f"Cancel {len(matching_tasks)} matching task(s)?"):
                    console.print("[dim]Cancellation aborted[/dim]")
                    return

            # Cancel each task with progress
            from ..utils.animated_progress import AnimatedEllipsisProgress

            cancelled_count = 0
            failed_count = 0

            with AnimatedEllipsisProgress(
                console, f"Cancelling {len(matching_tasks)} matching tasks", start_immediately=True
            ) as progress:
                for i, task in enumerate(matching_tasks):
                    task_name = task.name or task.task_id
                    progress.base_message = f"Cancelling {task_name} ({i+1}/{len(matching_tasks)})"

                    try:
                        client.cancel(task.task_id)
                        cancelled_count += 1
                    except Exception as e:
                        console.print(f"[red]✗[/red] Failed to cancel {task_name}: {e}")
                        failed_count += 1

            # Summary
            console.print()
            if cancelled_count > 0:
                console.print(f"[green]✓[/green] Successfully cancelled {cancelled_count} task(s)")
            if failed_count > 0:
                console.print(f"[red]✗[/red] Failed to cancel {failed_count} task(s)")

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [cyan]flow status[/cyan]",
                    "Submit a new task: [cyan]flow run task.yaml[/cyan]",
                ]
            )

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))


# Export command instance
command = CancelCommand()
