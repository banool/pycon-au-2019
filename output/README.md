This directory holds all the sigma js stuff for all of the programs. I do this so I don't have to dump the sigma js deps everywhere. Use it like this:

```
cd 0_sigmajs_all  # (if you haven't already)
python3 -m http.server
```

The general process for adding something here is this, as an example:

```
cd 2_simple_faster
pydeps main.py --nodot --no-output --sigmajs --import-times-file /Users/dport/github/pycon-au-2019/2_simple_faster/stderr > 2.json
cp 2.json ../0_sigmajs_all/static/
cd 0_sigmajs_all
cp template.html 2.html
```

Other important notes:
- You **must** set x and y for each node.
- You **don't** need to do any relative scaling of the size values, sigma js will figure it out.

I got the sigma js stuff in the first place by following the readme at https://github.com/jacomyal/sigma.js/ and copy the contents of the build folder into this one.
