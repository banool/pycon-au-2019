# Pycon AU 2019
## No time to idle about: Profiling import time in Python

**YouTube recording:** TBA

This repo holds all the code snippets (and much more) from my presentation at Pycon AU 2019.

This time around I'm using [pipenv](https://github.com/pypa/pipenv) to specify requirements, Python version, etc. Before playing with these snippets, run `pipenv install` from this directory and source the environment with `pipenv shell`.

See the summary for my presentation here: https://2019.pycon-au.org/talks/no-time-to-idle-about-profiling-import-time-in-python 

There is also a PDF of the presentation. I haven't included the source itself in case FB doesn't want other people using their slide deck, but later on I might migrate the speech to a non-fb slide deck and upload it here 😀😀🐍🐍.

To generate all of the output and have a look, try something like this:
```
echo 0_simple/ 1_simple_36/ 2_simple_faster/ 3_shared_import/ 4_unclear/ 5_demandimport/ | tr ' ' '\n' | xargs -n 1 python generate.py
python3 -m http.server
```

Btw to copy code snippets into Keynote, you can do the following:
- Open Terminal (Terminal.app, not iTerm 2).
- Open your code in vim. Get yourself a nice theme with a black background.
- Increase the size of the text. I got it to where it would paste into Keynote as size 48 Menlo font.
- Copy the code into a text box in Keynote. Put a black box behind the text.
