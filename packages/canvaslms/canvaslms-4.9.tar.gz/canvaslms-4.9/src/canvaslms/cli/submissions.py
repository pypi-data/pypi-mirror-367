import canvasapi.exceptions
import canvasapi.file
import canvasapi.submission

import canvaslms.cli
import canvaslms.cli.assignments as assignments
import canvaslms.cli.users as users
import canvaslms.hacks.canvasapi

import argparse
import csv
import json
import os
import pathlib
import subprocess
import pypandoc
import re
import rich.console
import rich.markdown
import rich.json
import shlex
import sys
import tempfile
import textwrap
import urllib.request

choices_for_shells = ["shell", "docker"]


def submissions_command(config, canvas, args):
    assignment_list = assignments.process_assignment_option(canvas, args)
    to_include = []
    if args.history:
        to_include += ["submission_history"]

    if args.ungraded:
        submissions = list_ungraded_submissions(assignment_list, include=to_include)
    else:
        submissions = list_submissions(assignment_list, include=to_include)
    if args.user or args.category or args.group:
        user_list = users.process_user_or_group_option(canvas, args)
        submissions = filter_submissions(submissions, user_list)
    if args.history:
        submissions = list(submissions)
        historical_submissions = []
        for submission in submissions:
            for prev_submission in submission.submission_history:
                prev_submission = canvasapi.submission.Submission(
                    submission._requester, prev_submission
                )
                prev_submission.assignment = submission.assignment
                prev_submission.user = submission.user
                historical_submissions.append(prev_submission)

        submissions = historical_submissions
    output = csv.writer(sys.stdout, delimiter=args.delimiter)

    for submission in submissions:
        if args.login_id:
            output.writerow(format_submission_short_unique(submission))
        else:
            output.writerow(format_submission_short(submission))


def speedgrader(submission):
    """Returns the SpeedGrader URL of the submission"""
    try:
        speedgrader_url = submission.preview_url
    except AttributeError:
        return None

    speedgrader_url = re.sub(
        "assignments/", "gradebook/speed_grader?assignment_id=", speedgrader_url
    )

    speedgrader_url = re.sub("/submissions/", "&student_id=", speedgrader_url)

    speedgrader_url = re.sub(r"\?preview.*$", "", speedgrader_url)

    return speedgrader_url


def submission_command(config, canvas, args):
    submission_list = process_submission_options(canvas, args)
    console = rich.console.Console()
    if args.output_dir:
        tmpdir = pathlib.Path(args.output_dir)
    else:
        tmpdir = pathlib.Path(tempfile.mkdtemp())
    for submission in submission_list:
        if args.sort_order == "student":
            subdir = (
                f"{submission.user.login_id}"
                f"/{submission.assignment.course.course_code}"
                f"/{submission.assignment.name}"
            )
        else:
            subdir = (
                f"{submission.assignment.course.course_code}"
                f"/{submission.assignment.name}"
                f"/{submission.user.login_id}"
            )

        (tmpdir / subdir).mkdir(parents=True, exist_ok=True)
        output = format_submission(
            submission,
            history=args.history,
            tmpdir=tmpdir / subdir,
            json_format=args.json,
        )

        if args.json:
            filename = "metadata.json"
            output = json.dumps(output, indent=2)
        else:
            filename = "metadata.md"
        with open(tmpdir / subdir / filename, "w") as f:
            f.write(output)

        if args.open == "open":
            subprocess.run(["open", tmpdir / subdir])
        elif args.open == "all":
            for file in (tmpdir / subdir).iterdir():
                subprocess.run(["open", file])

        if args.open in choices_for_shells:
            if args.open == "shell":
                print(
                    f"---> Spawning a shell ({os.environ['SHELL']}) in {tmpdir/subdir}"
                )

                subprocess.run(
                    ["sh", "-c", f"cd '{tmpdir/subdir}' && exec {os.environ['SHELL']}"]
                )

                print(
                    f"<--- canvaslms submission shell terminated.\n"
                    f"---- Files left in {tmpdir/subdir}."
                )
            elif args.open == "docker":
                print(f"---> Running a Docker container, files mounted in /mnt.")

                cmd = ["docker", "run", "-it", "--rm"]
                if args.docker_args:
                    cmd += args.docker_args
                cmd += [
                    "-v",
                    f"{tmpdir/subdir}:/mnt",
                    args.docker_image,
                    args.docker_cmd,
                ]

                subprocess.run(cmd)

                print(
                    f"<--- canvaslms submission Docker container terminated.\n"
                    f"---- Files left in {tmpdir/subdir}.\n"
                    f"---- To rerun the container, run:\n"
                    f"`{' '.join(map(shlex.quote, cmd))}`"
                )
        elif args.output_dir:
            pass
        elif sys.stdout.isatty():
            pager = ""
            if "MANPAGER" in os.environ:
                pager = os.environ["MANPAGER"]
            elif "PAGER" in os.environ:
                pager = os.environ["PAGER"]

            styles = False
            if "less" in pager and ("-R" in pager or "-r" in pager):
                styles = True
            with console.pager(styles=styles):
                if args.json:
                    console.print(rich.json.JSON(output))
                else:
                    console.print(rich.markdown.Markdown(output, code_theme="manni"))
        else:
            print(output)


def add_submission_options(parser, required=False):
    try:
        assignments.add_assignment_option(parser, required=required)
    except argparse.ArgumentError:
        pass

    try:
        users.add_user_or_group_option(parser, required=required)
    except argparse.ArgumentError:
        pass

    submissions_parser = parser.add_argument_group("filter submissions")
    try:  # to protect from this option already existing in add_assignment_option
        submissions_parser.add_argument(
            "-U", "--ungraded", action="store_true", help="Only ungraded submissions."
        )
    except argparse.ArgumentError:
        pass


def process_submission_options(canvas, args):
    assignment_list = assignments.process_assignment_option(canvas, args)
    user_list = users.process_user_or_group_option(canvas, args)

    if args.ungraded:
        submissions = list_ungraded_submissions(
            assignment_list,
            include=["submission_history", "submission_comments", "rubric_assessment"],
        )
    else:
        submissions = list_submissions(
            assignment_list,
            include=["submission_history", "submission_comments", "rubric_assessment"],
        )

    return list(filter_submissions(submissions, user_list))


def list_submissions(assignments, include=["submission_comments"]):
    for assignment in assignments:
        submissions = assignment.get_submissions(include=include)
        for submission in submissions:
            submission.assignment = assignment
            yield submission


def list_ungraded_submissions(assignments, include=["submisson_comments"]):
    for assignment in assignments:
        submissions = assignment.get_submissions(bucket="ungraded", include=include)
        for submission in submissions:
            if submission.submitted_at and (
                submission.graded_at is None
                or not submission.grade_matches_current_submission
            ):
                submission.assignment = assignment
                yield submission


def filter_submissions(submission_list, user_list):
    user_list = set(user_list)

    for submission in submission_list:
        for user in user_list:
            if submission.user_id == user.id:
                submission.user = user
                yield submission
                break


def format_submission_short(submission):
    return [
        submission.assignment.course.course_code,
        submission.assignment.name,
        submission.user.name,
        submission.grade,
        submission.submitted_at,
        submission.graded_at,
    ]


def format_submission_short_unique(submission):
    uid = users.get_uid(submission.user)

    return [
        submission.assignment.course.course_code,
        submission.assignment.name,
        uid,
        submission.grade,
        submission.submitted_at,
        submission.graded_at,
    ]


def format_submission(
    submission,
    history=False,
    json_format=False,
    md_title_level="#",
    tmpdir=None,
):
    """
    Formats submission for printing to stdout. Returns a string.

    If history is True, include all submission versions from history.

    If json_format is True, return a JSON string, otherwise Markdown.

    `md_title_level` is the level of the title in Markdown, by default `#`. This
    is used to create a hierarchy of sections in the output.

    `tmpdir` is the directory to store all the submission files. Defaults to None,
    which creates a temporary directory.
    """
    student = submission.assignment.course.get_user(submission.user_id)

    if json_format:
        formatted_submission = {}
    else:
        formatted_submission = ""

    metadata = {
        "course": submission.assignment.course.course_code,
        "assignment": submission.assignment.name,
        "student": str(student),
        "submission_id": submission.id,
        "submitted_at": submission.submitted_at,
        "graded_at": submission.graded_at,
        "grade": submission.grade,
        "graded_by": str(resolve_grader(submission)),
        "speedgrader": speedgrader(submission),
    }

    if json_format:
        formatted_submission.update(
            format_section(
                "metadata", metadata, json_format=True, md_title_level=md_title_level
            )
        )
    else:
        formatted_submission += format_section(
            "Metadata", metadata, md_title_level=md_title_level
        )
    try:
        if submission.rubric_assessment:
            if json_format:
                formatted_submission.update(
                    format_section(
                        "rubric_assessment", format_rubric(submission, json_format=True)
                    ),
                    json_format=True,
                )
            else:
                formatted_submission += format_section(
                    "Rubric assessment", format_rubric(submission)
                )
    except AttributeError:
        pass
    try:
        if submission.submission_comments:
            if json_format:
                formatted_submission.update(
                    format_section(
                        "comments", submission.submission_comments, json_format=True
                    )
                )
            else:
                body = ""
                for comment in submission.submission_comments:
                    body += f"{comment['author_name']} ({comment['created_at']}):\n\n"
                    body += comment["comment"] + "\n\n"
                formatted_submission += format_section("Comments", body)
    except AttributeError:
        pass
    if history:
        try:
            submission_history = submission.submission_history
        except AttributeError:
            pass
        else:
            if submission_history:
                versions = {}
                for version, prev_submission in enumerate(
                    submission.submission_history
                ):
                    version = str(version)
                    version_dir = tmpdir / f"version-{version}"

                    prev_submission = canvasapi.submission.Submission(
                        submission._requester, prev_submission
                    )
                    prev_submission.assignment = submission.assignment

                    prev_metadata = format_submission(
                        prev_submission,
                        tmpdir=version_dir,
                        json_format=json_format,
                        md_title_level=md_title_level + "#",
                    )

                    versions[version] = prev_metadata
                    if json_format:
                        with open(version_dir / "metadata.json", "w") as f:
                            json.dump(prev_metadata, f, indent=2)
                    else:
                        with open(version_dir / "metadata.md", "w") as f:
                            f.write(prev_metadata)

                if json_format:
                    formatted_submission.update(
                        format_section(
                            "submission_history",
                            versions,
                            json_format=True,
                            md_title_level=md_title_level,
                        )
                    )
                else:
                    formatted_versions = ""
                    for version, prev_metadata in versions.items():
                        formatted_versions += format_section(
                            f"Version {version}",
                            prev_metadata,
                            md_title_level=md_title_level + "#",
                        )
                    formatted_submission += format_section(
                        "Submission history",
                        formatted_versions,
                        md_title_level=md_title_level,
                    )
    else:
        try:
            if submission.body:
                if json_format:
                    formatted_submission.update(
                        format_section(
                            "body",
                            submission.body,
                            json_format=True,
                            md_title_level=md_title_level,
                        )
                    )
                else:
                    formatted_submission += format_section(
                        "Body", submission.body, md_title_level=md_title_level
                    )
        except AttributeError:
            pass
        try:
            if submission.submission_data:
                if json_format:
                    formatted_submission.update(
                        format_section(
                            "quiz_answers",
                            submission.submission_data,
                            json_format=True,
                            md_title_level=md_title_level,
                        )
                    )
                else:
                    formatted_submission += format_section(
                        "Quiz answers",
                        json.dumps(submission.submission_data, indent=2),
                        md_title_level=md_title_level,
                    )
        except AttributeError:
            pass
        try:
            tmpdir = pathlib.Path(tmpdir or tempfile.mkdtemp())
            tmpdir.mkdir(parents=True, exist_ok=True)
            if json_format:
                attachments = {}
            for attachment in submission.attachments:
                contents = convert_to_md(attachment, tmpdir)
                formatted_attachment = format_section(
                    attachment.filename,
                    contents,
                    json_format=json_format,
                    md_title_level=md_title_level + "#",
                )

                if json_format:
                    attachments.update(formatted_attachment)
                else:
                    formatted_submission += formatted_attachment

            if json_format and attachments:
                formatted_submission.update(
                    format_section(
                        "attachments",
                        attachments,
                        json_format=True,
                        md_title_level=md_title_level,
                    )
                )
        except AttributeError:
            pass

    return formatted_submission


def format_section(title, body, json_format=False, md_title_level="#"):
    """
    In the case of Markdown (default), we format the title as a header and the body
    as a paragraph. If we don't do JSON, but receive a dictionary as the body, we
    format it as a list of key-value pairs.

    `md_title_level` is the level of the title in Markdown, by default `#`.
    We'll use this to create a hierarchy of sections in the output.

    In the case of JSON, we return a dictionary with the title as the key and the
    body as the value.
    """
    if json_format:
        return {title: body}

    if isinstance(body, dict):
        return "\n".join(
            [
                f" - {key.capitalize().replace('_', ' ')}: {value}"
                for key, value in body.items()
            ]
        )

    return f"\n{md_title_level} {title}\n\n{body}\n\n"


def resolve_grader(submission):
    """
    Returns a user object if the submission was graded by a human.
    Otherwise returns None if ungraded or a descriptive string.
    """
    try:
        if submission.grader_id is None:
            return None
    except AttributeError:
        return None

    if submission.grader_id < 0:
        return "autograded"

    try:
        return submission.assignment.course.get_user(submission.grader_id)
    except canvasapi.exceptions.ResourceDoesNotExist:
        return f"unknown grader {submission.grader_id}"


def convert_to_md(attachment: canvasapi.file.File, tmpdir: pathlib.Path) -> str:
    """
    Converts `attachment` to Markdown. Returns the Markdown string.

    Store a file version in `tmpdir`.
    """
    outfile = tmpdir / attachment.filename
    attachment.download(outfile)
    content_type = getattr(attachment, "content-type")
    try:
        md_type = text_to_md(content_type)
        with open(outfile, "r") as f:
            contents = f.read()
        return f"```{md_type}\n{contents}\n```"
    except ValueError:
        pass
    if content_type.endswith("pdf"):
        try:
            return subprocess.check_output(["pdf2txt", str(outfile)], text=True)
        except subprocess.CalledProcessError:
            pass
    try:
        return pypandoc.convert_file(outfile, "markdown")
    except Exception as err:
        return (
            f"Cannot convert this file. " f"The file is located at\n\n  {outfile}\n\n"
        )


def text_to_md(content_type):
    """
    Takes a text-based content type, returns Markdown code block type.
    Raises ValueError if not possible.
    """
    if content_type.startswith("text/"):
        content_type = content_type[len("text/") :]
    else:
        raise ValueError(f"Not text-based content type: {content_type}")

    if content_type.startswith("x-"):
        content_type = content_type[2:]
    if content_type == "python-script":
        content_type = "python"

    return content_type


def format_rubric(submission, json_format=False):
    """
    Format the rubric assessment of the `submission` in readable form.

    If `json_format` is True, return a JSON string, otherwise Markdown.
    """

    if json_format:
        result = {}
    else:
        result = ""

    for crit_id, rating_data in submission.rubric_assessment.items():
        criterion = get_criterion(crit_id, submission.assignment.rubric)
        rating = get_rating(rating_data["rating_id"], criterion)
        try:
            comments = rating_data["comments"]
        except KeyError:
            comments = ""

        if json_format:
            result[criterion["description"]] = {
                "rating": rating["description"] if rating else None,
                "points": rating["points"] if rating else None,
                "comments": comments,
            }
        else:
            result += f"- {criterion['description']}: "
            if rating:
                result += f"{rating['description']} ({rating['points']})"
            else:
                result += "-"
            result += "\n"
            if comments:
                result += textwrap.indent(textwrap.fill(f"- Comment: {comments}"), "  ")
                result += "\n"

        if not json_format:
            result += "\n"

    return result.strip()


def get_criterion(criterion_id, rubric):
    """Returns criterion with ID `criterion_id` from rubric `rubric`"""
    for criterion in rubric:
        if criterion["id"] == criterion_id:
            return criterion

    return None


def get_rating(rating_id, criterion):
    """Returns rating with ID `rating_id` from rubric criterion `criterion`"""
    for rating in criterion["ratings"]:
        if rating["id"] == rating_id:
            return rating

    return None


def add_command(subp):
    """Adds the submissions and submission commands to argparse parser subp"""
    add_submissions_command(subp)
    add_submission_command(subp)


def add_submissions_command(subp):
    """Adds submissions command to argparse parser subp"""
    submissions_parser = subp.add_parser(
        "submissions",
        help="Lists submissions of an assignment",
        description="Lists submissions of assignment(s). Output format: "
        "<course code> <assignment name> <user> <grade> "
        "<submission date> <grade date>",
    )
    submissions_parser.set_defaults(func=submissions_command)
    assignments.add_assignment_option(submissions_parser)
    add_submission_options(submissions_parser)
    submissions_parser.add_argument(
        "-H", "--history", action="store_true", help="Include submission history."
    )
    submissions_parser.add_argument(
        "-l",
        "--login-id",
        help="Print login ID instead of name.",
        default=False,
        action="store_true",
    )


def add_submission_command(subp):
    """Adds submission command to argparse parser subp"""
    submission_parser = subp.add_parser(
        "submission",
        help="Prints information about a submission",
        description="""
  Prints data about matching submissions, including submission and grading time, 
  and any text-based attachments.

  Uses MANPAGER or PAGER environment variables for the pager to page output. If 
  the `-r` or `-R` flag is passed to `less`, it uses colours in the output. That 
  is, set `PAGER=less -r` or `PAGER=less -R` to get coloured output from this 
  command.

  """,
    )
    submission_parser.set_defaults(func=submission_command)
    add_submission_options(submission_parser)
    submission_parser.add_argument(
        "-o",
        "--output-dir",
        required=False,
        default=None,
        help="Write output to files in directory the given directory. "
        "If not specified, print to stdout. "
        "If specified, do not print to stdout.",
    )
    submission_parser.add_argument(
        "--json",
        required=False,
        action="store_true",
        default=False,
        help="Print output as JSON, otherwise Markdown.",
    )
    submission_parser.add_argument(
        "-H", "--history", action="store_true", help="Include submission history."
    )
    submission_parser.add_argument(
        "--open",
        required=False,
        nargs="?",
        default=None,
        const="open",
        choices=["open", "all"] + choices_for_shells,
        help="Open the directory containing the files using "
        "the default file manager (`open`). "
        "With `open`, the pager will be used to display the output as usual. "
        "With `all`, all files (not the directory containing them) will be "
        "opened in the default application for the file type. "
        "With `shell`, we just drop into the shell (as set by $SHELL), "
        "the output can be found in the metadata.{json,md} file in "
        "the shell's working directory. "
        "With `docker`, we run a Docker container with the "
        "directory mounted in the container. "
        "This way we can run the code in the submission in a "
        "controlled environment. "
        "Note that this requires Docker to be installed and running. "
        "Default: %(const)s",
    )
    submission_parser.add_argument(
        "--sort-order",
        required=False,
        choices=["student", "course"],
        default="student",
        help="Determines the order in which directories are created "
        "in `output_dir`. `student` results in `student/course/assignment` "
        "and `course` results in `course/assignment/student`. "
        "Default: %(default)s",
    )
    submission_parser.add_argument(
        "--docker-image",
        required=False,
        default="ubuntu",
        help="The Docker image to use when running a Docker container. "
        "This is used with the `docker` option for `--open`. "
        "Default: %(default)s",
    )
    submission_parser.add_argument(
        "--docker-cmd",
        required=False,
        default="bash",
        help="The command to run in the Docker container. "
        "This is used with the `docker` option for `--open`. "
        "Default: %(default)s",
    )
    submission_parser.add_argument(
        "--docker-args",
        required=False,
        default=[],
        nargs=argparse.REMAINDER,
        help="Any additional arguments to pass to the Docker command. "
        "This is used with the `docker` option for `--open`. "
        "Note that this must be the last option on the command line, it takes "
        "the rest of the line as arguments for Docker.",
    )
