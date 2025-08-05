import subprocess
import sys


def main():
    result = subprocess.run([sys.executable, "-m", "ctfsolver.find_usage"], check=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
