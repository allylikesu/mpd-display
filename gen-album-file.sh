#!/usr/bin/env bash
kill-instances() {
    kill $(pgrep -f "bash -e gen-album-file.sh")
    exit 0
}
while getopts 'k' flag; do
    case "${flag}" in
        k) kill-instances ;;
        *) ;;
    esac
done

running="running"
outfile="art"
songpath=$(mpc -f "%file%" current)
mpc readpicture "$songpath" > "$outfile"
echo "Art file generator subprocess started."
while [ -f "$running" ]; do
    mpc current --wait
    songpath=$(mpc -f "%file%" current)
    mpc readpicture "$songpath" > "$outfile"
    echo "Done writing image to file: $songpath"
done
echo "Art file generator subprocess stopped."
