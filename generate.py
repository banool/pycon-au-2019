import argparse
import logging
import os
import shutil
import subprocess
import tempfile


OUTPUT_DIR = "output"
STATIC_DIR = "static"
MAIN_FILE = "main.py"
STDERR_FILE_TEMPLATE = "{}.stderr"
SIGMA_FILE_TEMPLATE = "{}.json"
SIGMA_HTML_FILE_TEMPLATE = "{}.html"
SIGMA_ACTUAL_TEMPLATE = "template.html"
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


def generate_sigma(program_name, stderr_location, careful=False):
    json_location = os.path.join("../", OUTPUT_DIR, STATIC_DIR, SIGMA_FILE_TEMPLATE.format(program_name))
    if os.path.exists(json_location) and careful:
        return json_location
    abs_stderr_location = os.path.abspath(stderr_location)
    with open(json_location, "w") as f:
        subprocess.run(
            [
                "pydeps",
                MAIN_FILE,
                "--nodot",
                "--no-output",
                "--sigmajs",
                "--import-times-file",
                abs_stderr_location,
            ],
            stdout=f,
        )
    return json_location


def generate_sigma_html(program_name, careful=False):
    template_location = os.path.join("../", OUTPUT_DIR, SIGMA_ACTUAL_TEMPLATE)
    copy_location = os.path.join("../", OUTPUT_DIR, SIGMA_HTML_FILE_TEMPLATE.format(program_name))
    shutil.copy(template_location, copy_location)
    return copy_location


def generate_flamegraph(program_name, stderr_location, careful=False):
    svg_location = os.path.join("../", OUTPUT_DIR, FLAMEGRAPH_FILE_TEMPLATE.format(program_name))
    if os.path.exists(svg_location) and careful:
        return svg_location
    with tempfile.NamedTemporaryFile(mode="w") as temp_f:
        with open(stderr_location, "r") as stderr_f:
            script = os.path.join("../", TREE_SCRIPT)
            subprocess.run(["python", script], stdin=stderr_f, stdout=temp_f)
        script = os.path.join("../", FLAMEGRAPH_SCRIPT)
        with open(svg_location, "wb") as svg_f:
            subprocess.run(
                [script, "--width", "1200", "--height", "32", "--flamechart", temp_f.name],
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
    sigma_location = generate_sigma(program_name, stderr_location, careful=args.careful)
    sigma_html_location = generate_sigma_html(program_name, careful=args.careful)
    flamegraph_location = generate_flamegraph(
        program_name, stderr_location, careful=args.careful
    )

    new_stderr_location = os.path.join("../", OUTPUT_DIR, stderr_location)
    shutil.move(stderr_location, new_stderr_location)

    LOG.info("Generated these files (relative to {})".format(args.directory))
    for i in [new_stderr_location, sigma_location, sigma_html_location, flamegraph_location]:
        LOG.info(f"Generated {i}")
