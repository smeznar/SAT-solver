import sys, os, random

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: " + sys.argv[0] + " <input folder> <final number of files>")
        sys.exit(1)
    folder = sys.argv[1]
    chosen = int(sys.argv[2])
    allFiles = os.listdir(folder)
    remove = random.sample(allFiles, k = len(allFiles) - chosen)
    for i in remove:
        os.remove(os.path.join(folder, i))