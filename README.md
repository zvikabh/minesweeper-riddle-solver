# minesweeper-riddle-solver

This is a program for solving Minesweeper riddles - riddles where you are given
a Minesweeper board with some of the pixels exposed, and you must figure out
exactly where all the mines are.

## Example usage

```
python minesweeper.py input-filename.txt
```

The program will display progress information and finally show the solution.

## Input file format

The input file is a text file with one Minesweeper row per line. Each row
should contain one character per pixel. The character can be '.' for an unknown
pixel, or a digit (0-9) indicating that this pixel was revealed, in which case
the digit indicates the number of neighboring mines.

Several example riddles (all solvable using the program) are included.

