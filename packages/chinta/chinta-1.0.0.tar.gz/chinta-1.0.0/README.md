# Pupil
Tracks the word count of a TeX project in a git repository with respect to time
# Instructions
1. Download code and install `pupil` via pip
```bash
git clone git@github.com:hughsonm/tex-repo-word-counter.git
python3 -m pip install -e ./tex-repo-word-counter
```

1. Run `pupil` and tell it where to find the repo you want to analyze, as well as the name of the default branch.
The name of the default branch is probably either `"master"` or `"main"`
```bash
pupil "path/to/repo" "main"
```

1. Look at the cool graph!
