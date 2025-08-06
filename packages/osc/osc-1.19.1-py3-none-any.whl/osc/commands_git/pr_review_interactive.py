import os
import subprocess
import sys
from typing import Generator
from typing import Optional

import osc.commandline_git


NEW_COMMENT_TEMPLATE = """

#
# Lines starting with '#' will be ignored.
#
# Adding a comment to pull request {owner}/{repo}#{number}
#
"""


DECLINE_REVIEW_TEMPLATE = """

#
# Lines starting with '#' will be ignored.
#
# Requesting changes for pull request {owner}/{repo}#{number}
#
"""


class PullRequestReviewInteractiveCommand(osc.commandline_git.GitObsCommand):
    """
    Interactive review of pull requests

    Since this is an interactive command, the program return code indicates the user choice:
    - 0:   default return code
    - 1-9: reserved for error states
    - 10:  user selected "exit"
    - 11:  user selected "skip"

    This might be useful when wrapping the command in any external review tooling,
    handling one review at a time.
    """

    name = "interactive"
    parent = "PullRequestReviewCommand"

    def init_arguments(self):
        self.add_argument(
            "id",
            nargs="*",
            help="Pull request ID in <owner>/<repo>#<number> format",
        )
        self.add_argument(
            "--reviewer",
            help="Review on behalf of the specified reviewer that is associated to group review bot",
        )

    def run(self, args):
        from osc import gitea_api
        from osc.output import get_user_input

        if args.reviewer:
            try:
                gitea_api.User.get(self.gitea_conn, args.reviewer)
            except gitea_api.UserDoesNotExist as e:
                self.parser.error(f"Invalid reviewer: {e}")

        if args.id:
            # TODO: deduplicate, skip those that do not require a review (print to stderr)
            pull_request_ids = args.id
        else:
            # keep only the list of pull request IDs, throw search results away
            # because the search returns issues instead of pull requests
            pr_obj_list = gitea_api.PullRequest.search(self.gitea_conn, review_requested=True)
            pr_obj_list.sort()
            pull_request_ids = [pr_obj.id for pr_obj in pr_obj_list]
            del pr_obj_list

        skipped_drafts = 0
        return_code = 0

        for pr_index, pr_id in enumerate(pull_request_ids):
            self.print_gitea_settings()

            owner, repo, number = gitea_api.PullRequest.split_id(pr_id)
            pr_obj = gitea_api.PullRequest.get(self.gitea_conn, owner, repo, number)

            if pr_obj.draft:
                # we don't want to review drafts, they will change
                skipped_drafts += 1
                continue

            self.clone_git(owner, repo, number)
            self.view(owner, repo, number, pr_index=pr_index, pr_count=len(pull_request_ids), pr_obj=pr_obj)

            while True:
                # TODO: print at least some context because the PR details disappear after closing less
                reply = get_user_input(
                    f"Select a review action for '{pr_id}':",
                    answers={
                        "a": "approve",
                        "A": "approve and schedule for merging",
                        "d": "decline",
                        "m": "comment",
                        "v": "view again",
                        "s": "skip",
                        "x": "exit",
                    },
                    default_answer="s",
                )
                if reply == "a":
                    self.approve(owner, repo, number, commit=pr_obj.head_commit)
                    break
                if reply == "A":
                    self.approve(owner, repo, number, commit=pr_obj.head_commit)
                    gitea_api.PullRequest.merge(self.gitea_conn, owner, repo, number, merge_when_checks_succeed=True)
                    break
                elif reply == "d":
                    self.decline(owner, repo, number)
                    break
                elif reply == "m":
                    self.comment(owner, repo, number)
                    break
                elif reply == "v":
                    self.view(owner, repo, number, pr_index=pr_index, pr_count=len(pull_request_ids), pr_obj=pr_obj)
                elif reply == "s":
                    return_code = 11
                    break
                elif reply == "x":
                    return_code = 10
                    sys.exit(return_code)
                else:
                    raise RuntimeError(f"Unhandled reply: {reply}")

        if skipped_drafts:
            print(file=sys.stderr)
            print(f"Skipped drafts: {skipped_drafts}", file=sys.stderr)

        sys.exit(return_code)

    def approve(self, owner: str, repo: str, number: int, *, commit: str, reviewer: Optional[str] = None):
        from osc import gitea_api

        gitea_api.PullRequest.approve_review(self.gitea_conn, owner, repo, number, commit=commit, reviewer=reviewer)

    def decline(self, owner: str, repo: str, number: int, reviewer: Optional[str] = None):
        from osc import gitea_api

        message = gitea_api.edit_message(template=DECLINE_REVIEW_TEMPLATE.format(**locals()))

        # remove comments
        message = "\n".join([i for i in message.splitlines() if not i.startswith("#")])

        # strip leading and trailing spaces
        message = message.strip()

        gitea_api.PullRequest.decline_review(self.gitea_conn, owner, repo, number, msg=message, reviewer=reviewer)

    def comment(self, owner: str, repo: str, number: int):
        from osc import gitea_api

        message = gitea_api.edit_message(template=NEW_COMMENT_TEMPLATE.format(**locals()))

        # remove comments
        message = "\n".join([i for i in message.splitlines() if not i.startswith("#")])

        # strip leading and trailing spaces
        message = message.strip()

        gitea_api.PullRequest.add_comment(self.gitea_conn, owner, repo, number, msg=message)

    def get_git_repo_path(self, owner: str, repo: str, number: int):
        path = os.path.join("~", ".cache", "git-obs", "reviews", self.gitea_login.name, f"{owner}_{repo}_{number}")
        path = os.path.expanduser(path)
        return path

    def clone_git(self, owner: str, repo: str, number: int):
        from osc import gitea_api

        repo_obj = gitea_api.Repo.get(self.gitea_conn, owner, repo)
        clone_url = repo_obj.ssh_url

        # TODO: it might be good to have a central cache for the git repos to speed cloning up
        path = self.get_git_repo_path(owner, repo, number)
        git = gitea_api.Git(path)
        if os.path.isdir(path):
            git.fetch()
        else:
            os.makedirs(path, exist_ok=True)
            git.clone(clone_url, directory=path, quiet=False)
        git.fetch_pull_request(number, force=True)

    def view(
        self,
        owner: str,
        repo: str,
        number: int,
        *,
        pr_index: int,
        pr_count: int,
        pr_obj: Optional["PullRequest"] = None,
    ):
        from osc import gitea_api
        from osc.core import highlight_diff
        from osc.output import sanitize_text
        from osc.output import tty

        if pr_obj is None:
            pr_obj = gitea_api.PullRequest.get(self.gitea_conn, owner, repo, number)

        # the process works with bytes rather than with strings
        # because the diffs may contain character sequences that cannot be decoded as utf-8 strings
        proc = subprocess.Popen(["less"], stdin=subprocess.PIPE)
        assert proc.stdin is not None

        # heading
        heading = tty.colorize(f"[{pr_index + 1}/{pr_count}] Reviewing pull request '{owner}/{repo}#{number}'...\n", "yellow,bold")
        proc.stdin.write(heading.encode("utf-8"))
        proc.stdin.write(b"\n")

        # pr details
        proc.stdin.write(pr_obj.to_human_readable_string().encode("utf-8"))
        proc.stdin.write(b"\n")
        proc.stdin.write(b"\n")

        # timeline
        timeline = gitea_api.IssueTimelineEntry.list(self.gitea_conn, owner, repo, number)
        timeline_lines = []
        timeline_lines.append(tty.colorize("Timeline:", "bold"))
        for entry in timeline:
            text, body = entry.format()
            if text is None:
                continue
            timeline_lines.append(f"{gitea_api.dt_sanitize(entry.created_at)} {entry.user} {text}")
            for line in (body or "").strip().splitlines():
                timeline_lines.append(f"    | {line}")
        proc.stdin.write(b"\n".join((line.encode("utf-8") for line in timeline_lines)))
        proc.stdin.write(b"\n")
        proc.stdin.write(b"\n")

        # patch
        proc.stdin.write(tty.colorize("Patch:\n", "bold").encode("utf-8"))
        patch = gitea_api.PullRequest.get_patch(self.gitea_conn, owner, repo, number)
        patch = sanitize_text(patch)
        patch = highlight_diff(patch)
        proc.stdin.write(patch)
        proc.stdin.write(b"\n")

        # tardiff
        proc.stdin.write(tty.colorize("Archive diffs:\n", "bold").encode("utf-8"))
        tardiff_chunks = self.tardiff(owner, repo, number, pr_obj=pr_obj)
        for chunk in tardiff_chunks:
            chunk = sanitize_text(chunk)
            chunk = highlight_diff(chunk)
            try:
                proc.stdin.write(chunk)
            except BrokenPipeError:
                # user exits less before all data is written
                break

        proc.communicate()

    def get_tardiff_path(self):
        path = os.path.join("~", ".cache", "git-obs", "tardiff")
        path = os.path.expanduser(path)
        return path

    def tardiff(self, owner: str, repo: str, number: int, *, pr_obj: ".PullRequest") -> Generator[bytes, None, None]:
        from osc import gitea_api

        path = self.get_git_repo_path(owner, repo, number)
        git = gitea_api.Git(path)

        # the repo might be outdated, make sure the commits are available
        git.fetch()

        src_archives = git.lfs_ls_files(ref=pr_obj.head_commit)
        dst_archives = git.lfs_ls_files(ref=pr_obj.base_commit)

        def map_archives_by_name(archives: list):
            result = {}
            for fn, sha in archives:
                name = fn.rsplit("-", 1)[0]
                assert name not in result
                result[name] = (fn, sha)
            return result

        src_archives_by_name = map_archives_by_name(src_archives)
        dst_archives_by_name = map_archives_by_name(dst_archives)
        all_names = sorted(set(src_archives_by_name) | set(dst_archives_by_name))

        path = self.get_tardiff_path()
        td = gitea_api.TarDiff(path)

        for name in all_names:
            src_archive = src_archives_by_name.get(name, (None, None))
            dst_archive = dst_archives_by_name.get(name, (None, None))

            if src_archive[0]:
                td.add_archive(src_archive[0], src_archive[1], git.lfs_cat_file(src_archive[0], ref=pr_obj.head_commit))

            if dst_archive[0]:
                td.add_archive(dst_archive[0], dst_archive[1], git.lfs_cat_file(dst_archive[0], ref=pr_obj.base_commit))

            # TODO: max output length / max lines; in such case, it would be great to list all the changed files at least
            yield from td.diff_archives(*dst_archive, *src_archive)
