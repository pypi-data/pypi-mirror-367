#!/bin/sh

# Default values
queue="gpu-general"
memory=20

# Parse arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        -q|--queue) queue="$2"; shift 2;;
        -m|--memory) memory="$2"; shift 2;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Construct and execute the command
command="srun --partition=$queue --nodes=1 --ntasks=1 --cpus-per-task=1 --time=100
0 --mem=${memory}G --gres=gpu:1 --pty bash"
eval $command