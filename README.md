# WordChainSolver

Word Chain Solver computes the minimal number of changes from one word to another by changing only one letter at a time. It will also generate a DOT file for analysis. See [This Video](https://youtu.be/6GuqNrV8LsQ) for a full overview.

## Using The Solver

There is a default dictionary included sourced from http://wordlist.aspell.net/12dicts/
However, you may use any dictionary by replacing the word list file `WORD_LIST` with your own.
By default, word lengths are 3 letters, but you can change `WORD_LEN` to any number.
Once the dictionary and word length are set, just run `python WordChainSolver.py` to begin. You can choose 2 words and the program will print the optimal path to get there. It will also generate the **graph.dot** file.

**WARNING:** The word list included here is completely unfiltered and may include slurs and other offensive words. You should consider using a different dictionary if you need everything clean.

## Viewing The Graphs

If you'd like to make graphs like the video, follow these steps.

1. Download and install [Gephi](https://gephi.org/)
2. Open Gephi and load the DOT file 'graph.dot'.
3. In the layout tab, select **ForceAtlas 2**
4. In the ForceAtlas 2 settings, Enable the option "Stronger Gravity" and set the "Gravity" to 0.02
5. Press **Run** and watch the graph form.
6. Once the graph has mostly stopped moving, enable the "Prevent Overlap" option.
7. Press **Stop** to end the layout changes.
8. In appearance, under "Ranking", choose "Degree" and then choose a color palette. Then press **Apply**
9. In the Graph window press the icon that looks like a T to Show Node Labels.
10. Adjust the size of the labels with the slider until they fit in the nodes.
11. Adjust the color of the labels so they contrast well with the node colors.
