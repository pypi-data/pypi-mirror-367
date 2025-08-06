#!/bin/bash

# Claude ASCII animation for tmux
# Press 'q' to quit

# Hide cursor
tput civis

# Trap to restore cursor on exit
trap 'tput cnorm; exit' INT TERM

frames=(
"      .  *  .
    \\   |   /
  *   \\ | /   *
 ─ ─ ─ ─●─ ─ ─ ─
  *   / | \\   *
    /   |   \\
      .  *  ."

"      *  .  *
    /   |   \\
  .   / | \\   .
 ─ ─ ─ ─●─ ─ ─ ─
  .   \\ | /   .
    \\   |   /
      *  .  *"

"      .  *  .
    /   |   \\
  *   / | \\   *
 ─ ─ ─ ─●─ ─ ─ ─
  *   \\ | /   *
    \\   |   /
      .  *  ."

"      *  .  *
    \\   |   /
  .   \\ | /   .
 ─ ─ ─ ─●─ ─ ─ ─
  .   / | \\   .
    /   |   \\
      *  .  *"
)

frame_count=0

while true; do
    clear
    echo
    echo "${frames[$frame_count]}"
    echo
    echo "    ∿⟨:♡⟩∿ claude ∿⟨:♡⟩∿"
    echo "        (q to quit)"
    
    frame_count=$(((frame_count + 1) % 4))
    
    # Check for quit key (non-blocking)
    read -t 0.6 -n 1 key
    if [[ $key == "q" ]]; then
        break
    fi
done

# Restore cursor
tput cnorm
clear