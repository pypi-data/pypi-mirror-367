#!/bin/sh

# Default values
queue="engineering"
memory=5

# Parse arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        -q|--queue) queue="$2"; shift 2;;
        -m|--memory) memory="$2"; shift 2;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Construct and execute the command
command="srun --partition=$queue --nodes=1 --ntasks=1 --cpus-per-task=1 --time=17000 --mem=${memory}G --pty bash"
eval $command
