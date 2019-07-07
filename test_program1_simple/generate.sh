PYTHONPROFILEIMPORTTIME=1 python main.py |&
python ../tree.py > /tmp/profile &&
../scripts/flamegraph.pl --width 1400 --height 32 --flamechart /tmp/profile > test_program.svg &&
open -a Firefox test_program.svg
