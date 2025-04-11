#!/bin/bash

case $1 in
    -t|--test)
        python3.12 test.py
        ;;
    -w|--watch)
        declare -i count
        while true; do
            count+=1
            clear
            echo "[$count] Watching test.py"
            python3.12 test.py
            echo "Done..."
            read input
            if [[ $input == [qQ] ]]; then
                break
            fi
        done
        ;;
    "")
        python3.12 main.py
        ;;
    *)
        echo "Usage: run [-t|--test]"
        exit 1
        ;;
esac
