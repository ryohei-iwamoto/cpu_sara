"""CPU負荷テスト用スクリプト - 数字キーで負荷レベルを切り替え"""

import multiprocessing
import time
import psutil


def burn_cpu():
    """1コアを100%使い切る"""
    while True:
        pass


def main():
    workers = []
    max_cores = multiprocessing.cpu_count()

    print(f"CPU cores: {max_cores}")
    print(f"0: 負荷なし")
    for i in range(1, max_cores + 1):
        print(f"{i}: {i}コア全力 (~{int(i/max_cores*100)}%)")
    print(f"q: 終了")
    print("-" * 30)

    while True:
        cpu = psutil.cpu_percent(interval=0.5)
        key = input(f"[CPU: {cpu:.0f}%] レベル> ").strip()

        if key == "q":
            break

        try:
            n = int(key)
        except ValueError:
            continue

        # 既存ワーカーを停止
        for w in workers:
            w.terminate()
        workers.clear()

        # n個のワーカーを起動
        n = max(0, min(n, max_cores))
        for _ in range(n):
            w = multiprocessing.Process(target=burn_cpu, daemon=True)
            w.start()
            workers.append(w)

        print(f"  -> {n}コア稼働中")

    for w in workers:
        w.terminate()
    print("終了")


if __name__ == "__main__":
    main()
