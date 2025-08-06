import argparse
import canvasapi
import canvaslms.cli.courses as courses
import canvaslms.hacks.canvasapi
import csv
import json
import os
import pypandoc
import re
import rich.console
import rich.markdown
import sys


def add_assignment_option(parser, ungraded=True, required=False):
    try:
        courses.add_course_option(parser, required=required)
    except argparse.ArgumentError:
        pass

    if ungraded:
        parser.add_argument(
            "-U",
            "--ungraded",
            action="store_true",
            help="Filter only assignments with ungraded submissions.",
        )

    parser = parser.add_mutually_exclusive_group(required=required)

    parser.add_argument(
        "-a",
        "--assignment",
        required=False,
        default=".*",
        help="Regex matching assignment title or Canvas identifier, " "default: '.*'",
    )

    parser.add_argument(
        "-A",
        "--assignment-group",
        required=False,
        default="",
        help="Regex matching assignment group title or Canvas identifier.",
    )


def process_assignment_option(canvas, args):
    course_list = courses.process_course_option(canvas, args)
    assignments_list = []

    for course in course_list:
        try:
            ungraded = args.ungraded
        except AttributeError:
            ungraded = False

        all_assignments = list(
            filter_assignments([course], args.assignment, ungraded=ungraded)
        )

        try:
            assignm_grp_regex = args.assignment_group
        except AttributeError:
            print("default to .* for group")
            assignm_grp_regex = ".*"

        assignment_groups = filter_assignment_groups(course, assignm_grp_regex)

        for assignment_group in assignment_groups:
            assignments_list += list(
                filter_assignments_by_group(assignment_group, all_assignments)
            )
    return list(assignments_list)


def assignments_command(config, canvas, args):
    output = csv.writer(sys.stdout, delimiter=args.delimiter)
    assignment_list = process_assignment_option(canvas, args)
    for assignment in assignment_list:
        output.writerow(
            [
                assignment.course.course_code,
                assignment.assignment_group.name,
                assignment.name,
                assignment.due_at,
                assignment.unlock_at,
                assignment.lock_at,
            ]
        )


def filter_assignment_groups(course, regex):
    """Returns all assignment groups of course whose name matches regex"""
    name = re.compile(regex)
    return filter(lambda group: name.search(group.name), course.get_assignment_groups())


def filter_assignments_by_group(assignment_group, assignments):
    """Returns elements in assignments that are part of assignment_group"""
    for assignment in assignments:
        if assignment.assignment_group_id == assignment_group.id:
            assignment.assignment_group = assignment_group
            yield assignment


def assignment_command(config, canvas, args):
    console = rich.console.Console()

    assignment_list = process_assignment_option(canvas, args)
    for assignment in assignment_list:
        output = format_assignment(assignment)

        if sys.stdout.isatty():
            pager = ""
            if "MANPAGER" in os.environ:
                pager = os.environ["MANPAGER"]
            elif "PAGER" in os.environ:
                pager = os.environ["PAGER"]

            styles = False
            if "less" in pager and ("-R" in pager or "-r" in pager):
                styles = True
            with console.pager(styles=styles, links=True):
                console.print(rich.markdown.Markdown(output, code_theme="manni"))
        else:
            print(output)


def format_assignment(assignment):
    """Returns an assignment formatted for the terminal"""
    text = f"""
# {assignment.name}

## Metadata

- Unlocks: {assignment.unlock_at if assignment.unlock_at else None}
- Due:     {assignment.due_at if assignment.due_at else None}
- Locks:   {assignment.lock_at if assignment.lock_at else None}
- Ungraded submissions: {assignment.needs_grading_count}
- Submission type: {assignment.submission_types}
- URL: {assignment.html_url}
- Submissions: {assignment.submissions_download_url}

"""

    if assignment.description:
        instruction = pypandoc.convert_text(assignment.description, "md", format="html")
        text += f"## Instruction\n\n{instruction}\n\n"
        try:
            text += f"## Rubric\n\n{format_rubric(assignment.rubric)}\n\n"
        except AttributeError:
            pass
    else:
        try:
            text += f"## Rubric\n\n{format_rubric(assignment.rubric)}\n\n"
        except AttributeError:
            pass
        text += f"## Assignment data\n\n```json\n{format_json(assignment)}\n```\n"

    return text


def format_rubric(rubric):
    """
    Returns a markdown representation of the rubric
    """
    if not rubric:
        return "No rubric set."

    text = ""
    for criterion in rubric:
        text += f"- {criterion['description']}\n"
        text += f"  - Points: {criterion['points']}\n"
        text += f"  - Ratings: "
        text += (
            "; ".join(
                [
                    f"{rating['description'].strip()} ({rating['points']})"
                    for rating in criterion["ratings"]
                ]
            )
            + "\n"
        )
        text += f"\n```\n{criterion['long_description']}\n```\n\n"

    return text


def format_json(assignment):
    """Returns a JSON representation of the assignment"""
    return json.dumps(
        {
            key: str(value)
            for key, value in assignment.__dict__.items()
            if not key.startswith("_")
        },
        indent=2,
    )


def list_assignments(assignments_containers, ungraded=False):
    """Lists all assignments in all assignments containers (courses or
    assignement groups)"""
    for container in assignments_containers:
        if isinstance(container, canvasapi.course.Course):
            course = container
        elif isinstance(container, canvasapi.assignment.AssignmentGroup):
            assignment_group = container
            course = assignment_group.course

        if ungraded:
            assignments = container.get_assignments(bucket="ungraded")
        else:
            assignments = container.get_assignments()

        for assignment in assignments:
            try:
                assignment.course = course
            except NameError:
                pass

            try:
                assignment.assignment_group = assignment_group
            except NameError:
                pass

            yield assignment


def list_ungraded_assignments(assignments_containers):
    return list_assignments(assignments_containers, ungraded=True)


def filter_assignments(assignments_containers, regex, ungraded=False):
    """Returns all assignments from assignments_container whose
    title matches regex"""
    p = re.compile(regex)
    for assignment in list_assignments(assignments_containers, ungraded=ungraded):
        if p.search(assignment.name):
            yield assignment
        elif p.search(str(assignment.id)):
            yield assignment


def add_command(subp):
    """Adds the subcommands assignments and assignment to argparse parser subp"""
    add_assignments_command(subp)
    add_assignment_command(subp)


def add_assignments_command(subp):
    """Adds the assignments subcommand to argparse parser subp"""
    assignments_parser = subp.add_parser(
        "assignments",
        help="Lists assignments of a course",
        description="Lists assignments of a course. "
        "Output, CSV-format: "
        "<course> <assignment group> <assignment name> "
        "<due date> <unlock at> <lock at>",
    )
    assignments_parser.set_defaults(func=assignments_command)
    add_assignment_option(assignments_parser)


def add_assignment_command(subp):
    """Adds the assignment subcommand to argparse parser subp"""
    assignment_parser = subp.add_parser(
        "assignment",
        help="Lists assignment details",
        description="Lists assignment details",
    )
    assignment_parser.set_defaults(func=assignment_command)
    add_assignment_option(assignment_parser)
