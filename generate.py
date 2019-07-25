import argparse
import logging
import os
import shutil
import subprocess
import tempfile


old_run = subprocess.run


def new_run(*args, **kwargs):
    print("Running: {}".format(" ".join(list(*args))))
    return old_run(*args, **kwargs)


subprocess.run = new_run


OUTPUT_DIR = "output"
STATIC_DIR = "static"
MAIN_FILE = "main.py"
STDERR_FILE_TEMPLATE = "{}.stderr"
PYDEPS_CONNECTEDNESS_FILE_TEMPLATE = "{}.connectedness"
PYDEPS_CONNECTEDNESS_SVG_FILE_TEMPLATE = "{}_connectedness.svg"
PYDEPS_SVG_FILE_TEMPLATE = "{}.svg"
PYDEPS_SIGMA_FILE_TEMPLATE = "{}.json"
PYDEPS_SIGMA_HTML_FILE_TEMPLATE = "{}.html"
PYPEPS_SIGMA_ACTUAL_TEMPLATE = "template.html"
FLAMEGRAPH_FILE_TEMPLATE = "{}.svg"
TREE_SCRIPT = "tree.py"
FLAMEGRAPH_SCRIPT = "flamegraph.pl"


LOG = logging.getLogger(__name__)
LOG.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)


# Note: None of these generate functions should leave anything in the target
# directories, only in the OUTPUT_DIR directory.
# Also, they should all be able to function from within the target directory.
# They should all return the path of the file they generated.


def generate_stderr(program_name, careful=False):
    # Should be run from within the target directory.
    stderr_location = STDERR_FILE_TEMPLATE.format(program_name)
    if os.path.exists(stderr_location) and careful:
        return stderr_location
    env = os.environ.copy()
    env["PYTHONPROFILEIMPORTTIME"] = "🐍"
    with open(stderr_location, "w") as f:
        subprocess.run(["python", MAIN_FILE], env=env, stderr=f)
    return stderr_location


def generate_pydeps(
    program_name,
    stderr_location=None,
    careful=False,
    png=False,
    sigma=False,
    connectedness=False,
):
    if sigma:
        program_name = PYDEPS_SIGMA_FILE_TEMPLATE.format(program_name)
    elif png:
        if not stderr_location:
            program_name = "{}_no_times".format(program_name)
        program_name = PYDEPS_SVG_FILE_TEMPLATE.format(program_name)
    elif connectedness:
        stdout_location = PYDEPS_CONNECTEDNESS_FILE_TEMPLATE.format(program_name)
        stdout_location = os.path.join("../", OUTPUT_DIR, STATIC_DIR, stdout_location)
        program_name = PYDEPS_CONNECTEDNESS_SVG_FILE_TEMPLATE.format(program_name)
    else:
        raise RuntimeError("sigma or png must be True")
    location = os.path.join("../", OUTPUT_DIR, STATIC_DIR, program_name)
    if os.path.exists(location) and careful:
        return location
    args = [
        "pydeps",
        MAIN_FILE,
        "--noshow",
        "--max-bacon",
        "0",
        "--reverse",
        "-o",
        location,
    ]
    if stderr_location:
        abs_stderr_location = os.path.abspath(stderr_location)
        args += ["--import-times-file", abs_stderr_location]
    if sigma:
        args += ["--nodot", "--sigmajs"]
    if connectedness:
        args += ["--connectedness"]
        with open(stdout_location, "w") as f:
            subprocess.run(args, stdout=f)
        return [location, stdout_location]
    else:
        subprocess.run(args)
    return location


def generate_sigma_html(program_name, careful=False):
    template_location = os.path.join("../", OUTPUT_DIR, PYPEPS_SIGMA_ACTUAL_TEMPLATE)
    copy_location = os.path.join(
        "../", OUTPUT_DIR, PYDEPS_SIGMA_HTML_FILE_TEMPLATE.format(program_name)
    )
    shutil.copy(template_location, copy_location)
    return copy_location


def generate_flamegraph(program_name, stderr_location, careful=False):
    svg_location = os.path.join(
        "../", OUTPUT_DIR, FLAMEGRAPH_FILE_TEMPLATE.format(program_name)
    )
    if os.path.exists(svg_location) and careful:
        return svg_location
    with tempfile.NamedTemporaryFile(mode="w") as temp_f:
        with open(stderr_location, "r") as stderr_f:
            script = os.path.join("../", TREE_SCRIPT)
            subprocess.run(["python", script], stdin=stderr_f, stdout=temp_f)
        script = os.path.join("../", FLAMEGRAPH_SCRIPT)
        with open(svg_location, "wb") as svg_f:
            subprocess.run(
                [
                    script,
                    "--width",
                    "1200",
                    "--height",
                    "32",
                    "--flamechart",
                    temp_f.name,
                ],
                stdout=svg_f,
            )
    return svg_location


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory to generate output for")
    parser.add_argument(
        "--careful", help="Do not generate if output files already exist"
    )
    args = parser.parse_args()

    os.chdir(args.directory)
    program_name = os.path.basename(os.path.normpath(args.directory))

    stderr_location = generate_stderr(program_name)
    png_no_times_location = generate_pydeps(
        program_name, None, careful=args.careful, png=True
    )
    png_location = generate_pydeps(
        program_name, stderr_location, careful=args.careful, png=True
    )
    sigma_location = generate_pydeps(
        program_name, stderr_location, careful=args.careful, sigma=True
    )
    sigma_html_location = generate_sigma_html(program_name, careful=args.careful)
    flamegraph_location = generate_flamegraph(
        program_name, stderr_location, careful=args.careful
    )
    connectedness_location, connectedness_stdout_location = generate_pydeps(
        program_name, stderr_location, careful=args.careful, connectedness=True
    )

    new_stderr_location = os.path.join("../", OUTPUT_DIR, stderr_location)
    shutil.move(stderr_location, new_stderr_location)

    LOG.info("Generated these files (relative to {})".format(args.directory))
    for i in [
        new_stderr_location,
        png_no_times_location,
        png_location,
        sigma_location,
        sigma_html_location,
        flamegraph_location,
        connectedness_location,
        connectedness_stdout_location,
    ]:
        LOG.info(f"Generated {i}")
