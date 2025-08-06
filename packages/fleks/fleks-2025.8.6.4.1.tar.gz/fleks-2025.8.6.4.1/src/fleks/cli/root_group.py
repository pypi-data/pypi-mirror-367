""" """

import collections
from gettext import gettext as _

import click


class RootGroup(click.Group):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        # NB: this is needed, otherwise main help is messy
        kwargs.update(help="")
        super().__init__(*args, **kwargs)

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """"""
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue
            commands.append((subcommand, cmd))
        commands = dict(commands)
        if len(commands):
            # allow for 3 times the default spacing
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)
            plugin_subs = {
                name: obj
                for name, obj in commands.items()
                if obj.__class__.__name__ == "Group"
            }
            toplevel = dict(
                core=[],
                meta=collections.defaultdict(collections.defaultdict),
                plugins=collections.defaultdict(list),
            )
            for subcommand, cmd in commands.items():
                help = cmd.get_short_help_str(limit)
                is_plugin = cmd in list(plugin_subs.values())
                label = ""
                if is_plugin:
                    subcom_obj = plugin_subs[subcommand]
                    plugin_class = getattr(subcom_obj, "plugin_class", None)
                    # if issubclass(plugin_kls, (fleks.Plugin,)):
                    cli_label = getattr(plugin_class, "cli_label", None)
                    cli_description = getattr(
                        plugin_class,
                        "cli_description",
                        getattr(
                            plugin_class.__class__,
                            "cli_description",
                            plugin_class.__doc__,
                        ),
                    )
                    if cli_label:
                        toplevel["plugins"][cli_label].append(
                            (f"{subcommand}:", f"{cmd.help}")
                        )
                        toplevel["meta"][cli_label]["description"] = cli_description
                        continue
                toplevel["core"].append((f"{subcommand}:", f"{cmd.help}"))

            if toplevel["core"]:
                order = ["plan", "apply", "config", "config-raw"]
                ordering = []
                for o in order:
                    for subc, subh in toplevel["core"]:
                        if subc == o:
                            ordering.append((subc, subh))
                            toplevel["core"].remove((subc, subh))
                toplevel["core"] = ordering + toplevel["core"]
                with formatter.section(_(click.style("Top-level", bold=True))):
                    formatter.write_text(
                        click.style(
                            "Core functionality (these names are forbid to plugins)",
                            dim=True,
                        )
                    )
                    formatter.write_dl(toplevel["core"])
            for label in toplevel["plugins"]:
                cli_description = toplevel["meta"][label]["description"]
                with formatter.section(_(click.style(f"{label.title()}", bold=True))):
                    if cli_description:
                        formatter.write_text(
                            click.style(f"{cli_description.lstrip()}", dim=True)
                        )
                    formatter.write_dl(toplevel["plugins"][label])

    def format_usage(self, ctx, formatter):
        """
        :param ctx: param formatter:
        """
        # terminal_width, _ = click.get_terminal_size()
        terminal_width = 30
        click.echo("-" * terminal_width)
        super().format_usage(ctx, formatter)

    def parse_args(self, ctx, args):
        default = self.default
        originals = [args.copy(), ctx.__dict__.copy()]
        copy = [x for x in args.copy() if x != "--help"]
        ctx2 = default.make_context("default", copy)
        with ctx2:
            default.invoke(ctx2)
        return super(click.Group, self).parse_args(ctx, args)
