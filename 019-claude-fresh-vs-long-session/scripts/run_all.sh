#!/bin/bash
# Two chains in parallel: one long resumed session vs fresh session per task, 10 SUITE14 packages, rep $1
H=/workspace/work/tig/_harness; E=/workspace/work/tig/019-claude-fresh-vs-long-session; R=${1:-1}
$H/chain_cc.sh $E long $R 10 >> $E/results/driver.log 2>&1 &
FRESH=1 $H/chain_cc.sh $E fresh $R 10 >> $E/results/driver.log 2>&1 &
wait
