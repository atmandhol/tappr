import subprocess
import os
import re

from datetime import datetime
from tappr.modules.utils import commit_parser

dir_name = os.path.dirname(__file__)


class ChangeLog:
    def __init__(self, logger):
        self.logger = logger

    # noinspection PyUnresolvedReferences
    def generate_changelog(self, log_range, ignore_dependabot_commits, ignore_docs_commits, output):
        """
        The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
        and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

        Great resource for customizing git logs: https://git-scm.com/docs/pretty-formats
        """

        if log_range == "all":
            log_range = ""

        # Format is Timestamp:Message:Description:Author
        cmd = "git log " + log_range + ' --pretty=format:"%cs|%s|%d|%an"'

        self.logger.debug("* Running: %s" % cmd)
        self.logger.debug("* Changelog format is based on: https://keepachangelog.com/en/1.0.0/\n")

        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        git_log_op = sp.stdout.read().decode()
        git_log_op = git_log_op.split("\n")

        final_log = str()

        added_list = list()
        changes_list = list()
        deprecated_list = list()
        removed_list = list()
        fixes_list = list()
        docs_list = list()
        unknown_list = list()
        dependabot_list = list()

        tag = "untagged"
        tag_date = datetime.today().strftime("%Y-%m-%d")

        for msg in git_log_op:
            msg = msg.split("|")
            if "tag:" in msg[2]:
                final_log += self.generate_changelog_for_tag(
                    tag,
                    tag_date,
                    added_list,
                    changes_list,
                    deprecated_list,
                    removed_list,
                    fixes_list,
                    docs_list,
                    unknown_list,
                    dependabot_list,
                    ignore_dependabot_commits,
                    ignore_docs_commits,
                )
                tag = msg[2].split("tag:")[1].split(",")[0].split(")")[0].strip()
                tag_date = msg[0]
                added_list = list()
                changes_list = list()
                deprecated_list = list()
                removed_list = list()
                fixes_list = list()
                docs_list = list()
                unknown_list = list()
                dependabot_list = list()

            if msg[3] == "dependabot[bot]":
                dependabot_list.append(msg[1])
            else:
                commit_parser.parse(
                    msg[1],
                    added_list,
                    changes_list,
                    deprecated_list,
                    removed_list,
                    fixes_list,
                    docs_list,
                    unknown_list,
                )

        final_log += self.generate_changelog_for_tag(
            tag,
            tag_date,
            added_list,
            changes_list,
            deprecated_list,
            removed_list,
            fixes_list,
            docs_list,
            unknown_list,
            dependabot_list,
            ignore_dependabot_commits,
            ignore_docs_commits,
        )
        final_log = re.sub(r"\(#[0-9]*\)", "", final_log)
        if output == "stdout":
            print(final_log)
        else:
            open(output, "w").write(final_log)

    def generate_changelog_for_tag(
        self,
        tag,
        date,
        added_list,
        changes_list,
        deprecated_list,
        removed_list,
        fixes_list,
        docs_list,
        unknown_list,
        dependabot_list,
        ignore_dependabot_commits,
        ignore_docs_commits,
    ):
        if (
            len(added_list) == 0
            and len(changes_list) == 0
            and len(deprecated_list) == 0
            and len(removed_list) == 0
            and len(fixes_list) == 0
            and len(dependabot_list) == 0
            and len(docs_list) == 0
            and len(unknown_list) == 0
        ):
            return ""
        change_log_format = open(os.path.join(dir_name, "changelog_format.md"), "r").read()
        change_log_format = change_log_format.replace("$$tag", tag)
        change_log_format = change_log_format.replace("$$date", date)
        change_log_format = change_log_format.replace("$$added_list", self.list_to_text(added_list))
        change_log_format = change_log_format.replace("$$changes_list", self.list_to_text(changes_list))
        change_log_format = change_log_format.replace("$$deprecated_list", self.list_to_text(deprecated_list))
        change_log_format = change_log_format.replace("$$removed_list", self.list_to_text(removed_list))
        change_log_format = change_log_format.replace("$$fixes_list", self.list_to_text(fixes_list))
        if not ignore_dependabot_commits:
            change_log_format = change_log_format.replace(
                "$$dependencies_list",
                "### Dependency Changes\n" + self.list_to_text(dependabot_list),
            )
        else:
            change_log_format = change_log_format.replace("$$dependencies_list", "")
        if not ignore_docs_commits:
            change_log_format = change_log_format.replace("$$docs_list", "### Documentation Changes\n" + self.list_to_text(docs_list))
        else:
            change_log_format = change_log_format.replace("$$docs_list", "")
        change_log_format = change_log_format.replace("$$unknown_list", self.list_to_text(unknown_list))
        return change_log_format

    @staticmethod
    def list_to_text(lst):
        op = str()
        for item in lst:
            # Cleanup extra spaces here just in case
            item = item.strip()
            op += "- " + item.capitalize() + "\n"
        return op
