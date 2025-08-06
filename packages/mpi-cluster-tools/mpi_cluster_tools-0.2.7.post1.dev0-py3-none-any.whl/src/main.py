import typer
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header

from .config import Config
from .htcondor.htcondor import HTCondorClient
from .ssh.cluster import SSHClient
from .widgets.cancel_confirm import ConfirmCancelScreen
from .widgets.job_file_viewer import JobFileViewer
from .widgets.sidebar import JobsSidebar

cli = typer.Typer()


@cli.callback(invoke_without_command=True)
def cluster_command(
    ctx: typer.Context,
    hostname: str = typer.Option(help="The hostname of the cluster"),
    port: int = typer.Option(22, help="The port to connect to the cluster"),
    username: str = typer.Option(help="The username to connect to the cluster"),
    private_key_path: str | None = typer.Option(
        None, help="The path to the private key to connect to the cluster"
    ),
):
    """Run the cluster monitoring tool."""
    if ctx.invoked_subcommand is None:
        config = Config(hostname, port, username, private_key_path)
        app = ClusterApp(config)
        app.run()


class StatusFooter(Footer):
    """Custom footer that shows refresh status."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_refreshing = False

    def update_refresh_status(self, refreshing: bool) -> None:
        """Update the refresh status display."""
        self.app_refreshing = refreshing
        self.refresh(layout=False)

    def render(self):
        """Render the footer with refresh status."""
        from rich.align import Align
        from rich.columns import Columns
        from rich.text import Text

        # Create the key bindings text (similar to normal Footer)
        bindings_text = Text()
        if self.app:
            for binding in self.app.BINDINGS:
                key, action, description = binding
                bindings_text.append(f"{key}", style="bold white")
                bindings_text.append(f" {description} ", style="dim white")

        # Create refresh status if refreshing
        if self.app_refreshing:
            status_text = Text("🔄 Refreshing...", style="cyan bold")
            # Combine bindings and status
            return Columns([bindings_text, Align.right(status_text)], expand=True)
        else:
            return bindings_text


class ClusterApp(App):
    """Original cluster monitoring app (kept for backwards compatibility)."""

    CSS_PATH = "styles/cluster_tool.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "refresh_data_async", "Refresh data"),
        ("c", "cancel_job", "Cancel selected job"),
        ("s", "ssh_to_job", "SSH to selected job node"),
        ("q", "quit", "Quit"),
    ]

    refreshing = reactive(False)

    def __init__(self, config: Config | None = None):
        super().__init__()
        self.config = config or Config(
            hostname="login.cluster.is.localnet",
            username="barmstrong",
            port=22,
        )
        self.ssh_client = None
        self.htcondor_client = None
        self.title = "Condor Client"
        self.auto_refresh_timer = None

    def compose(self):
        """Simple layout for cluster monitoring."""
        yield Header()
        with Horizontal():
            yield JobsSidebar(id="sidebar", classes="container")
            with Vertical(id="main-content"):
                yield JobFileViewer(ssh_client=None, classes="job-file-viewer")
        yield StatusFooter(id="status-footer")

    async def on_mount(self) -> None:
        """Initialize SSH and HTCondor clients when the app starts."""
        self._initialize_clients()
        self._start_auto_refresh()

    def watch_refreshing(self, refreshing: bool) -> None:
        """Update footer when refresh status changes."""
        try:
            footer = self.query_one("#status-footer", StatusFooter)
            footer.update_refresh_status(refreshing)
        except Exception:
            # Footer might not be mounted yet
            pass

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        """An action to quit the application."""
        self.exit()

    def action_refresh_data(self) -> None:
        """An action to refresh all data (synchronous version)."""
        try:
            self.refreshing = True

            # Refresh the job list in the sidebar
            sidebar = self.query_one("#sidebar", JobsSidebar)
            sidebar.refresh_jobs()

            # Refresh the file viewers
            job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)
            job_file_viewer.refresh_all()

            print("Data refreshed successfully")
        except Exception as e:
            print(f"Error refreshing data: {e}")
        finally:
            self.refreshing = False

    async def action_refresh_data_async(self) -> None:
        """An action to refresh all data asynchronously."""
        try:
            self.refreshing = True

            # Refresh the job list in the sidebar
            sidebar = self.query_one("#sidebar", JobsSidebar)

            # Refresh the file viewers
            job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)

            # Run both refreshes concurrently
            import asyncio

            await asyncio.gather(
                sidebar.refresh_jobs_async(),
                job_file_viewer.refresh_all_async(),
                return_exceptions=True,
            )

            print("Data refreshed successfully (async)")
        except Exception as e:
            print(f"Error refreshing data: {e}")
        finally:
            self.refreshing = False

    def action_cancel_job(self) -> None:
        """An action to cancel the currently selected job."""
        try:
            # Get the currently selected job
            job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)
            current_job = job_file_viewer.current_job

            if not current_job:
                print("No job selected for cancellation")
                return

            if not self.htcondor_client:
                print("HTCondor client not available")
                return

            # Confirm the job can be canceled (not already completed/removed)
            if current_job.is_completed:
                print(f"Job {current_job.job_id} is already completed")
                return

            # Show confirmation dialog
            self.push_screen(
                ConfirmCancelScreen(current_job.job_id),
                callback=self._handle_cancel_confirmation,
            )

        except Exception as e:
            print(f"Error preparing to cancel job: {e}")

    def _handle_cancel_confirmation(self, confirmed: bool) -> None:
        """Handle the result of the cancellation confirmation dialog."""
        if not confirmed:
            print("Job cancellation canceled by user")
            return

        try:
            # Get the currently selected job again
            job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)
            current_job = job_file_viewer.current_job

            if not current_job:
                print("No job selected for cancellation")
                return

            print(f"Attempting to cancel job {current_job.job_id}...")
            success = self.htcondor_client.cancel_job(current_job.job_id)

            if success:
                print(f"✓ Job {current_job.job_id} canceled successfully")
                # Refresh the job list to show updated status
                self.action_refresh_data()
            else:
                print(f"✗ Failed to cancel job {current_job.job_id}")

        except Exception as e:
            print(f"Error canceling job: {e}")

    def action_ssh_to_job(self) -> None:
        """An action to SSH to the execution node of the currently selected job."""
        try:
            # Get the currently selected job
            job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)
            current_job = job_file_viewer.current_job

            if not current_job:
                print("No job selected for SSH connection")
                return

            if not self.htcondor_client:
                print("HTCondor client not available")
                return

            # Check if job is in a state where SSH is possible
            if not current_job.is_running:
                print(
                    f"Cannot SSH to job {current_job.job_id}: job is {current_job.job_status_name}"
                )
                return

            if not current_job.remote_host:
                print(
                    f"Cannot SSH to job {current_job.job_id}: no remote host information"
                )
                return

            print(
                f"Opening condor_ssh_to_job connection to job {current_job.job_id}..."
            )

            # Open condor_ssh_to_job in a separate terminal
            self.htcondor_client.ssh_to_job(current_job)

        except Exception as e:
            print(f"Error establishing SSH connection: {e}")

    def _start_auto_refresh(self) -> None:
        """Start the auto-refresh timer to update data every 5 seconds."""
        print("Starting auto-refresh timer...")
        if self.auto_refresh_timer is not None:
            # Stop existing timer if it exists
            self.auto_refresh_timer.stop()
            print("Stopped existing timer")

        # Set up a timer to refresh data every 5 seconds
        self.auto_refresh_timer = self.set_interval(5.0, self._auto_refresh)

    def _auto_refresh(self) -> None:
        """Auto-refresh callback that updates all data asynchronously."""
        try:
            print("Auto-refreshing data...")
            # Only refresh if clients are initialized
            if self.ssh_client and self.htcondor_client:
                # Schedule the async refresh to run as soon as possible
                self.call_later(self.action_refresh_data_async)
        except Exception as e:
            # Silently handle errors to avoid spamming the console
            print(f"Auto-refresh error: {e}")

    def _initialize_clients(self) -> None:
        """Initialize SSH and HTCondor clients."""
        try:
            # Initialize SSH client
            self.ssh_client = SSHClient(self.config)

            # Connect to the cluster
            self.ssh_client.connect()
            print(f"Connected to cluster at {self.config.hostname}")

            # Initialize HTCondor client
            self.htcondor_client = HTCondorClient(self.ssh_client)

            # Set up the sidebar with the HTCondor client
            sidebar = self.query_one("#sidebar", JobsSidebar)
            sidebar.set_htcondor_client(self.htcondor_client, self.config.username)

            # Set up the job file viewer with the SSH client
            job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)
            job_file_viewer.set_ssh_client(self.ssh_client)

        except Exception as e:
            print(f"Failed to initialize clients: {e}")
            # Could show an error message to the user here

    def on_jobs_sidebar_job_selected(self, event: JobsSidebar.JobSelected) -> None:
        """Handle job selection from the sidebar."""
        print(f"Selected job: {event.job.job_id} ({event.job.job_status_name})")
        # Update the job file viewer with the selected job
        job_file_viewer = self.query_one("JobFileViewer", JobFileViewer)
        job_file_viewer.set_job(event.job)

    def on_unmount(self) -> None:
        """Clean up connections when the app shuts down."""
        # Stop auto-refresh timer
        if self.auto_refresh_timer is not None:
            self.auto_refresh_timer.stop()
            self.auto_refresh_timer = None

        # Clean up SSH connection
        if self.ssh_client:
            try:
                self.ssh_client.disconnect()
                print("Disconnected from cluster")
            except Exception as e:
                print(f"Error disconnecting from cluster: {e}")


def main():
    """Main entry point for the CLI tool."""
    cli()


if __name__ == "__main__":
    main()
