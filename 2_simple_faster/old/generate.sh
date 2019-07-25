PYTHONPROFILEIMPORTTIME=1 python main.py |&
python ../tree.py > /tmp/profile &&
../scripts/flamegraph.pl --width 1400 --height 32 --flamechart /tmp/profile > main.svg &&
open -a Firefox main.svg
