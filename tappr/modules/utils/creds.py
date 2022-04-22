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
        default_registry_server,
        default_registry_repo,
        default_tap_install_registry,
        default_registry_username,
        default_registry_password,
        vmware_username,
        vmware_password,
    ):
        configs = None
        if os.path.isfile(f'{os.environ.get("HOME")}/.config/tappr/config'):
            configs = json.loads(open(f'{os.environ.get("HOME")}/.config/tappr/config', "r").read())

        if tanzunet_username is None:
            tanzunet_username = str(
                Prompt.ask(
                    f":person_raising_hand_light_skin_tone: Tanzu Network Username", default=configs["tanzunet_username"] if configs else None
                )
            )
        if tanzunet_password is None:
            tanzunet_password = str(
                Prompt.ask(
                    f":see-no-evil_monkey: Tanzu Network Password [bold][cyan]({'**' + configs['tanzunet_password'][-4:] if configs else None})[/cyan]",
                    default=configs["tanzunet_password"] if configs else None,
                    show_default=False,
                )
            )
        if pivnet_uaa_token is None:
            pivnet_uaa_token = str(
                Prompt.ask(
                    f":speak-no-evil_monkey: Pivnet UAA Token [bold][cyan]({'**' + configs['pivnet_uaa_token'][-4:] if configs else None})[/cyan]",
                    default=configs["pivnet_uaa_token"] if configs else None,
                    show_default=False,
                )
            )
        if default_registry_server is None:
            default_registry_server = str(
                Prompt.ask(
                    f":convenience_store: Default Registry Server (e.g. gcr.io, index.docker.com)",
                    default=configs["default_registry_server"] if configs else None,
                )
            )
        if default_registry_repo is None:
            default_registry_repo = str(
                Prompt.ask(
                    f":convenience_store: Default Registry Repo (Don't include the registry server or starting /)",
                    default=configs["default_registry_repo"] if configs else None,
                )
            )
        if default_tap_install_registry is None:
            default_tap_install_registry = str(
                Prompt.ask(
                    f":convenience_store: Default TAP install registry", default=configs["default_tap_install_registry"] if configs else None
                )
            )
        if default_registry_username is None:
            default_registry_username = str(
                Prompt.ask(
                    f":convenience_store: Default Registry Username (use _json_key for gcr.io)",
                    default=configs["default_registry_username"] if configs else None,
                )
            )
        if default_registry_password is None:
            default_registry_password = str(
                Prompt.ask(
                    f":speak-no-evil_monkey: Default Registry Password (Use absolute path to json key file path for gcr.io) [bold][cyan]({'**' + configs['default_registry_password'][-8:] if configs else None})[/cyan]",
                    default=configs["default_registry_password"] if configs else None,
                    show_default=False,
                )
            )
        if vmware_username is None:
            vmware_username = str(
                Prompt.ask(
                    f":person_raising_hand_light_skin_tone: VMWare Username",
                    default=configs["vmware_username"] if configs else None,
                )
            )
        if vmware_password is None:
            vmware_password = str(
                Prompt.ask(
                    f":see-no-evil_monkey: VMWare Password [bold][cyan]({'**' + configs['vmware_password'][-4:] if configs else None})[/cyan]",
                    default=configs["vmware_password"] if configs else None,
                    show_default=False,
                )
            )

        try:
            self.sh.run_proc("mkdir -p ~/.config")
            self.sh.run_proc("mkdir -p ~/.config/tappr")
            open(f'{os.environ.get("HOME")}/.config/tappr/config', "w").write(
                json.dumps(
                    {
                        "tanzunet_username": tanzunet_username,
                        "tanzunet_password": tanzunet_password,
                        "pivnet_uaa_token": pivnet_uaa_token,
                        "default_registry_server": default_registry_server,
                        "default_registry_repo": default_registry_repo,
                        "default_tap_install_registry": default_tap_install_registry,
                        "default_registry_username": default_registry_username,
                        "default_registry_password": default_registry_password,
                        "vmware_username": vmware_username,
                        "vmware_password": vmware_password,
                    }
                )
            )
            self.logger.msg(":notebook: Config initialized at [green]~/.config/tappr/config[/green]", bold=True)
        except Exception as ex:
            self.logger.msg(f":person_shrugging: Error setting config.\n[red]Error: {ex}[/red]", bold=True)

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
                    bold=True,
                )
                raise typer.Exit(-1)
