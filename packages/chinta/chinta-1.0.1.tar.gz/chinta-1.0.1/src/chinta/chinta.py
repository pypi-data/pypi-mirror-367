from git import Repo
import argparse
import matplotlib.pyplot as plt
import os
import datetime

def countTexWordsInFile(filename):
    count = 0
    with open(filename, "r") as fid:
        lines = fid.readlines()
        for line in lines:
            words = line.split(" ")
            count += len(words)
    return(count)

def countTexWordsInDirectory(directory):
    total_tex_words = 0
    for entry in os.scandir(directory):
        if entry.is_file() and (entry.path.endswith(".tex")):
            file_word_count = countTexWordsInFile(entry.path)
            total_tex_words += file_word_count
        elif entry.is_dir():
            total_tex_words += countTexWordsInDirectory(entry.path)
    return(total_tex_words)

def trackTexWordsInRepository(repo,name_of_main_branch):
    counts = []
    dates = []
    for commit in repo.iter_commits(name_of_main_branch):
        print(f'looking at commit {commit.hexsha}')
        repo.git.checkout(commit.hexsha)
        counts.append(countTexWordsInDirectory(repo.working_tree_dir))
        dates.append(datetime.datetime.fromtimestamp(commit.committed_date))

    repo.git.checkout(name_of_main_branch)
    return(counts,dates)

def main():
    parser = argparse.ArgumentParser(
        prog='chinta',
        description='Tracks word count in a tex repo over time and plots the result')
    parser.add_argument('path', type=str, help='path to the repository whose words you wish to count. Example: /Users/you/thesis')
    parser.add_argument('-b', '--branch', default='main', help='branch whose history you wish to inspect')
    args = parser.parse_args()

    repo = Repo(args.path)
    print(f'Counting words in {repo.working_tree_dir}')
    counts,dates = trackTexWordsInRepository(repo,args.branch)

    plt.figure()
    plt.plot(dates,counts)
    plt.xlabel("Date")
    plt.ylabel("Number of Words")
    plt.title("Word Count")
    plt.show()


if __name__=='__main__':
    main()