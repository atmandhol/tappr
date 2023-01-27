import os
import typer
import json
from rich.prompt import Prompt


class CredsHelper:
    def __init__(self, logger, subprocess_helper):
        self.sh = subprocess_helper
        self.logger = logger

    def set_config(
        self,
        tanzunet_username,
        tanzunet_password,
        pivnet_uaa_token,
        registry_server,
        registry_username,
        registry_password,
        registry_tbs_repo,
        registry_tap_package_repo,
        install_registry_server="registry.tanzu.vmware.com",
    ):
        configs = None
        if os.path.isfile(f'{os.environ.get("HOME")}/.config/tappr/config'):
            configs = json.loads(open(f'{os.environ.get("HOME")}/.config/tappr/config', "r").read())

        if tanzunet_username is None:
            self.logger.msg("[bold][yellow]Enter your Tanzu Network email[/yellow][/bold]")
            tanzunet_username = str(Prompt.ask(f":person_raising_hand: Tanzu Network Username", default=configs["tanzunet_username"] if configs else None))
        if tanzunet_password is None:
            self.logger.msg("\n[bold][yellow]Enter your Tanzu Network password[/yellow][/bold]")
            tanzunet_password = str(
                Prompt.ask(
                    f":see-no-evil_monkey: Tanzu Network Password [bold][cyan]({'**' + configs['tanzunet_password'][-4:] if configs else None})[/cyan]",
                    default=configs["tanzunet_password"] if configs else None,
                    show_default=False,
                    password=True,
                )
            )
        if pivnet_uaa_token is None:
            self.logger.msg(
                "\n[bold][yellow]Enter your Pivnet UAA token. If you don't have one, you can get one by following these steps:\n"
                "- Go to https://network.tanzu.vmware.com/\n"
                "- Sign In\n"
                "- Click on your username on the top right\n"
                "- Click Edit Profile\n"
                '- Scroll all the way down and click on "Request New Refresh Token"[/yellow][/bold]'
            )
            pivnet_uaa_token = str(
                Prompt.ask(
                    f":speak-no-evil_monkey: Pivnet UAA Token [bold][cyan]({'**' + configs['pivnet_uaa_token'][-4:] if configs else None})[/cyan]",
                    default=configs.get("pivnet_uaa_token") if configs else None,
                    show_default=False,
                    password=True,
                )
            )
        if install_registry_server is None:
            self.logger.msg("\n[bold][yellow]Enter your Registry URL without http/https where your TAP packages are located. If not sure, use registry.tanzu.vmware.com[/yellow][/bold]")
            install_registry_server = str(
                Prompt.ask(
                    f":convenience_store: Install Registry Server (e.g. registry.tanzu.vmware.com)",
                    default=configs.get("install_registry_server") if configs and "install_registry_server" in configs else None,
                )
            )

        if registry_server is None:
            self.logger.msg(
                "\n[bold][yellow]Default registry server is your own Registry that you have access and credentials to. This is the registry where Build service and supply chain outputs will go. "
                "Enter Registry URL without http/https where your TAP packages are located.\n"
                "- gcr.io for Google Container registry\n"
                "- index.docker.com for Docker Hub\n"
                "- Custom Harbor or any other registry URL[/yellow][/bold]"
            )
            registry_server = str(
                Prompt.ask(
                    f":convenience_store: Default Registry Server (e.g. gcr.io, index.docker.com)",
                    default=configs["registry_server"] if "registry_server" in configs else None,
                )
            )
        if registry_username is None:
            self.logger.msg("\n[bold][yellow]Enter your Default registry username.\n" '- Use "_json_key" if you are using Service account key for Google Container Registry[/yellow][/bold]')
            registry_username = str(
                Prompt.ask(
                    f":convenience_store: Registry Username",
                    default=configs["registry_username"] if "registry_username" in configs else None,
                )
            )
        if registry_password is None:
            self.logger.msg(
                "\n[bold][yellow]Enter your Default registry password.\n"
                "- You can enter the password in clear text or\n"
                "- You can enter an ABSOLUTE url to a file (relative paths starting with ~/ are not accepted) that contains the password and tappr will read the password from that file. Do this if you are using a Service account key for Google container registry[/yellow][/bold]"
            )
            registry_password = str(
                Prompt.ask(
                    f":speak-no-evil_monkey: Registry Password (Use absolute path to json key file path for gcr.io) [bold][cyan]({'**' + configs['registry_password'][-8:] if configs else None})[/cyan]",
                    default=configs["registry_password"] if "registry_password" in configs else None,
                    show_default=False,
                    password=True,
                )
            )
        if registry_tbs_repo is None:
            self.logger.msg(
                "\n[bold][yellow]Enter the repository path in your registry where Build service dependencies will go.\n"
                "- For Google Container registry, it should be gcp-project-name/repo-name (e.g. my-gcp-project/tbs-repo)\n"
                "- For Harbor, it should be project/repo-name\n"
                "- For Docker Hub, it should be username/repo-name\n"
                "[red]NOTE: Do not put your registry server name in the prefix[/red][/yellow][/bold]"
            )
            registry_tbs_repo = str(
                Prompt.ask(
                    f":convenience_store: Build service repo",
                    default=configs["registry_tbs_repo"] if configs else None,
                )
            )
        if registry_tap_package_repo is None:
            self.logger.msg(
                "\n[bold][yellow]Enter the repository path in your registry where TAP packages will go.\n"
                "- For Google Container registry, it should be gcp-project-name/repo-name (e.g. my-gcp-project/tap-packages)\n"
                "- For Harbor, it should be project/repo-name\n"
                "- For Docker Hub, it should be username/repo-name\n"
                "[red]NOTE: Do not put your registry server name in the prefix[/red][/yellow][/bold]"
            )
            registry_tap_package_repo = str(Prompt.ask(f":convenience_store: TAP package repo", default=configs["registry_tap_package_repo"] if configs else None))

        try:
            self.sh.run_proc("mkdir -p ~/.config")
            self.sh.run_proc("mkdir -p ~/.config/tappr")
            open(f'{os.environ.get("HOME")}/.config/tappr/config', "w").write(
                json.dumps(
                    {
                        "tanzunet_username": tanzunet_username,
                        "tanzunet_password": tanzunet_password,
                        "pivnet_uaa_token": pivnet_uaa_token,
                        "install_registry_server": install_registry_server,
                        "registry_server": registry_server,
                        "registry_username": registry_username,
                        "registry_password": registry_password,
                        "registry_tbs_repo": registry_tbs_repo,
                        "registry_tap_package_repo": registry_tap_package_repo,
                    }
                )
            )
            self.logger.msg(":notebook: Config initialized at [green]~/.config/tappr/config[/green]", bold=False)
        except Exception as ex:
            self.logger.msg(f":person_shrugging: Error setting config.\n[red]Error: {ex}[/red]", bold=False)

    @staticmethod
    def get_config():
        if os.path.isfile(f'{os.environ.get("HOME")}/.config/tappr/config'):
            return json.loads(open(f'{os.environ.get("HOME")}/.config/tappr/config', "r").read())
        else:
            return None

    def get(self, key, env_var):
        config = self.get_config()
        if not config or key not in config:
            self.check_if_present_in_env([env_var])
            return os.environ.get(env_var)
        else:
            os.environ[env_var] = config[key]
            return config[key]

    def check_if_present_in_env(self, envs: list):
        for env in envs:
            if env not in dict(os.environ):
                self.logger.msg(
                    f":crying_cat_face: Environment variable [yellow]{env}[/yellow] not found. Please set that and retry or try setting up tappr using tappr init.",
                    bold=False,
                )
                raise typer.Exit(-1)
