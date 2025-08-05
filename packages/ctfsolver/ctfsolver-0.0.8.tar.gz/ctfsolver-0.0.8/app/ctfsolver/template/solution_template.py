from ctfsolver import CTFSolver


class Solution(CTFSolver):
    def main(self):
        pass


if __name__ == "__main__":
    conn = "local"
    file = None
    url = None
    port = None
    solution = Solution(conn=conn, file=file, url=url, port=port)
    solution.main()
