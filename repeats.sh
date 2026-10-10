#!/bin/bash
export PATH=$HOME/.temporalio/bin:$PATH
cd ~/temporallab
for seed in 2 3 4; do
  .venv/bin/python chaos.py "to-s$seed" 8 10 $seed 0
  .venv/bin/python chaos.py "hb-s$seed" 8 10 $seed 2
done
echo ALL_DONE
