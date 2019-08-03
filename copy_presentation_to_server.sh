#!/bin/bash
cd "$(dirname "$0")"
rsync -av "../Pycon AU 2019 Profiling Import Time Talk Presentation Slides.pdf" daniel@dport.me:/var/www/dport/writing/pycon-au-2019.pdf
