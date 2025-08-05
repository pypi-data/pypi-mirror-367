from rich import box
from rich.console import Console
from rich.panel import Panel

from .themes import THEME

console = Console(theme=THEME, width=80)


def welcome_screen():
    # display welcome screen and banner
    logo = r"""
     █████╗ ███████╗██████╗ 
    ██╔══██╗██╔════╝██╔══██╗
    ███████║███████╗██║  ██║
    ██╔══██║╚════██║██║  ██║
    ██║  ██║███████║██████╔╝
    ╚═╝  ╚═╝╚══════╝╚═════╝ 
    """
    console.clear()
    console.print(
        Panel(logo, box=box.MINIMAL, style="header", width=100),
        justify="center",
    )
    console.print(
        "[accent]a simpler way to understand git[/accent]\n", justify="center"
    )
    console.print(
        "press [educational]h[/educational] for help, [educational]m[/educational] to select model, [educational]q[/educational] to quit",
        justify="center",
    )
    console.print()  # print a new line


def display_git_status(status):
    # display repository status panel
    body = f"branch: {status.current_branch or 'none'}\n"
    body += f"staged: {len(status.staged)}  modified: {len(status.modified)}  untracked: {len(status.untracked)}\n"

    if status.has_remote:
        sync = f"↑{status.ahead}" if status.ahead > 0 else ""
        sync += f"↓{status.behind}" if status.behind > 0 else ""
        sync = sync or "synced"
        body += f"remote: {status.remote_name} ({sync})\n"

    if status.conflicts:
        body += "\n[destructive]! conflicts detected[/destructive]"
    if status.uncommitted_changes > 0:
        body += (
            f"\n[warning]> {status.uncommitted_changes} uncommitted changes[/warning]"
        )

    panel = Panel(
        body, title="[header]status[/header]", box=box.ROUNDED, style="info", width=40
    )
    console.print(panel)


def display_execution_plan(plan):
    # display execution plan with safety indicators
    body = f"[{plan.overall_safety.lower()}]safety: {plan.overall_safety.lower()}[/{plan.overall_safety.lower()}]\n\n"

    for i, step in enumerate(plan.steps, 1):
        safety_icon = {"safe": "+", "caution": "!", "risky": "!", "dangerous": "x"}.get(
            step.safety_level.lower(), "+"
        )
        body += f"[accent]{safety_icon} {i}.[/accent] [command]{step.command}[/]\n"
        body += f"  {step.description}\n"

        if (
            step.safety_level.lower() in ["risky", "dangerous"]
            and step.potential_issues
        ):
            body += f"  [warning]! {step.potential_issues[0]}[/warning]\n"
        body += "\n"

    if plan.warnings:
        body += "[warning]warnings:[/warning]\n"
        for warning in plan.warnings[:1]:
            body += f"[warning]! {warning.message}[/warning]\n"
            if warning.safer_alternatives:
                body += f"  [info]> {warning.safer_alternatives[0]}[/info]\n"

    panel = Panel(
        body,
        title="[header]plan[/header]",
        subtitle=f"[info]{plan.summary}[/info]",
        box=box.ROUNDED,
        style="accent",
        width=60,
    )
    console.print(panel)


def display_results(state):
    # display results panel and lessons learned
    if state.operation_success:
        icon, style = "+", "success"
    elif state.recovery_needed:
        icon, style = "!", "warning"
    else:
        icon, style = "x", "failure"

    console.print(
        Panel(
            f"[{style}]{icon} {state.final_message}[/{style}]",
            title="[header]results[/header]",
            box=box.ROUNDED,
            style=style,
        )
    )

    for result in state.step_results:
        status_icon = (
            "[success]+[/success]" if result.success else "[failure]x[/failure]"
        )
        console.print(f"{status_icon} [command]{result.command}[/]")

        if result.success and result.output:
            output = (
                result.output[:100] + "..."
                if len(result.output) > 100
                else result.output
            )
            console.print(f"  [info]{output}[/info]")
        elif not result.success and result.error:
            console.print(f"  [failure]{result.error}[/failure]")

    if state.lessons_learned:
        console.print("\n[accent]learned:[/accent]")
        for lesson in list(set(state.lessons_learned))[:2]:
            console.print(f"[info]> {lesson}[/info]")
    console.print()


def show_help():
    # display help instructions
    body = (
        "[accent]h[/accent]  - help\n"
        "[accent]m[/accent]  - select model\n"
        "[accent]q[/accent]  - quit\n\n"
        "[header]example git tasks:[/header]\n"
        "undo my last commit but keep changes\n"
        "safely merge main into my branch\n"
        "clean up my commit history\n"
        "help me resolve merge conflicts\n"
        "push my changes without breaking things\n"
        "what would happen if i reset --hard?\n\n"
        "[info]asd focuses on git safety and education[/info]"
    )
    panel = Panel(
        body,
        title="[header]git assistant help[/header]",
        box=box.ROUNDED,
        style="info",
        width=50,
    )
    console.print(panel)
