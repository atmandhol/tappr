import subprocess
import sys
import os

from tappr.modules.utils import commit_parser, enums

dir_name = os.path.dirname(__file__)
PRPath = enums.PRPATH


class ReleaseNotes:
    def __init__(self, logger):
        self.logger = logger

    # noinspection PyUnresolvedReferences
    def generate_releasenotes(
        self,
        since_ver,
        release_ver,
        template_file,
        pr_path,
        ignore_dependabot_commits,
        ignore_docs_commits,
        output,
    ):
        if since_ver == "init":
            cmd = "git log " + release_ver + ' --pretty=format:"%cs|%s|%d|%an"'
        else:
            cmd = "git log " + since_ver + ".." + release_ver + ' --pretty=format:"%cs|%s|%d|%an"'
        # Format is Timestamp:Message:Description:Author

        self.logger.debug("* Running: %s\n" % cmd)

        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        git_log_op = sp.stdout.read().decode()
        if git_log_op == "":
            self.logger.error("* No Git log found using the following command: %s" % cmd)
            sys.exit(-1)

        git_log_op = git_log_op.split("\n")

        added_list = list()
        changes_list = list()
        deprecated_list = list()
        removed_list = list()
        fixes_list = list()
        docs_list = list()
        unknown_list = list()
        dependabot_list = list()

        rl_format = open(template_file).read()
        rl_format = rl_format.replace("$$semver", release_ver)
        rl_format = rl_format.replace("$$pre-semver", since_ver)

        for msg in git_log_op:
            msg = msg.split("|")
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

        features_str, bug_str, doc_str, dep_str = self.generate_feature_release_description(
            added_list=added_list,
            changes_list=changes_list,
            deprecated_list=deprecated_list,
            removed_list=removed_list,
            fixes_list=fixes_list,
            docs_list=docs_list,
            unknown_list=unknown_list,
            dependabot_list=dependabot_list,
        )

        rl_format = rl_format.replace("$$features", features_str)
        rl_format = rl_format.replace("$$bugs", bug_str)
        rl_format = rl_format.replace("$$docs", doc_str) if not ignore_docs_commits else rl_format.replace("$$docs", "")
        rl_format = rl_format.replace("$$deps", dep_str) if not ignore_dependabot_commits else rl_format.replace("$$deps", "")

        rl_format = rl_format.replace("(#", "(" + pr_path)

        if output == "stdout":
            print(rl_format)
        else:
            open(output, "w").write(rl_format)

    def generate_feature_release_description(
        self, added_list, changes_list, deprecated_list, removed_list, fixes_list, docs_list, unknown_list, dependabot_list
    ):
        # TODO: Add support for Docs changes and Dependency changes in release notes
        features_str = str()
        bug_str = str()
        doc_str = str()
        dependabot_str = str()

        features_str += self.list_to_text(added_list, "[Added]")
        features_str += self.list_to_text(changes_list, "[Changed]")
        features_str += self.list_to_text(deprecated_list, "[Deprecated]")
        features_str += self.list_to_text(removed_list, "[Removed]")
        features_str += self.list_to_text(unknown_list, "[Unknown]")

        bug_str += self.list_to_text(fixes_list, "[Fixed]")

        doc_str += self.list_to_text(docs_list, "[Doc Update]")

        dependabot_str += self.list_to_text(dependabot_list, "[Dependency Update]")

        return features_str, bug_str, doc_str, dependabot_str

    @staticmethod
    def list_to_text(lst, label):
        op = str()
        for item in lst:
            # Cleanup extra spaces here just in case
            item = item.strip()
            op += "- **" + label + "** " + item.capitalize() + "\n"
        return op
