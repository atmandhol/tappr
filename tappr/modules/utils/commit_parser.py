# noinspection PyUnresolvedReferences
def parse(
    commit_msg: str,
    added_list,
    changes_list,
    deprecated_list,
    removed_list,
    fixes_list,
    docs_list,
    unknown_list,
):
    """
    Commit messages should follow the following format:

    type: <short-summary>

    Add ! after type if it's a breaking change
    type!: <short-summary>

    type: can be one of the following:
        build: Changes that affect the build system (example: Makefile)
        chore: Housekeeping tasks, grunt tasks etc; no production code change
        ci: Changes to our CI configuration files and scripts
        docs: Documentation only changes
        deprecate: A code change that deprecates a feature
        feat: A new feature
        fix: A bug fix
        perf: A code change that improves performance
        refactor: A code change that neither fixes a bug nor adds a feature, includes updates to a feature.
        removed: Removed a feature that was previously deprecated
        test: Adding missing tests or correcting existing tests
    """
    # Clean msg
    commit_msg = commit_msg.strip()

    if len(commit_msg.split(":")) == 1:
        unknown_list.append(commit_msg.split(":")[0])
        return

    # Bin it
    if "!" in commit_msg.lower().split(":")[0]:
        commit_msg = commit_msg.split(":")[0] + "BREAKING CHANGE - " + commit_msg.split(":")[1]

    if commit_msg.lower().startswith("feat") or commit_msg.lower().startswith("feature"):
        added_list.append(commit_msg.split(":")[1])
    elif (
        commit_msg.lower().startswith("refactor")
        or commit_msg.lower().startswith("perf")
        or commit_msg.lower().startswith("build")
        or commit_msg.lower().startswith("ci")
        or commit_msg.lower().startswith("test")
        or commit_msg.lower().startswith("chore")
    ):
        changes_list.append(commit_msg.split(":")[1])
    elif commit_msg.lower().startswith("deprecate"):
        deprecated_list.append(commit_msg.split(":")[1])
    elif commit_msg.lower().startswith("removed"):
        removed_list.append(commit_msg.split(":")[1])
    elif commit_msg.lower().startswith("fix"):
        fixes_list.append(commit_msg.split(":")[1])
    elif commit_msg.lower().startswith("doc"):
        docs_list.append(commit_msg.split(":")[1])
    else:
        unknown_list.append(commit_msg.split(":")[1])

    return
