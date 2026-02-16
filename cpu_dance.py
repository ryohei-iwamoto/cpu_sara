"""
CPU使用率に応じてダンスの速度が変わるデスクトップマスコット
右下に背景透過で常に表示され、CPU使用率が高いほど速く踊る
"""

import tkinter as tk
import psutil
from PIL import Image, ImageTk
import os
import sys
import glob


TRANSPARENT_COLOR = "#010101"


class CpuDancer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CPU Sara")
        self.root.overrideredirect(True)  # タイトルバーなし
        self.root.attributes("-topmost", True)  # 常に最前面
        self.root.attributes("-transparentcolor", TRANSPARENT_COLOR)  # 透過色

        # 背景除去済みフレームを読み込み
        self.frames = []
        self.display_height = 100
        self.fps = 30
        self._load_frames()

        if not self.frames:
            print("Error: No frames loaded")
            sys.exit(1)

        self.frame_index = 0.0  # 小数で管理し、速度に応じて進める
        self.cpu_percent = 0.0

        # ウィンドウサイズ設定
        sample = self.frames[0]
        self.win_w = sample.width()
        self.win_h = sample.height()

        # 画面右下に配置
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - self.win_w - 10
        y = screen_h - self.win_h - 50  # タスクバー分余白
        self.root.geometry(f"{self.win_w}x{self.win_h}+{x}+{y}")

        # キャンバス（背景を透過色に）
        self.canvas = tk.Canvas(
            self.root, width=self.win_w, height=self.win_h,
            bg=TRANSPARENT_COLOR, highlightthickness=0
        )
        self.canvas.pack()
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW)

        # ドラッグ移動対応
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # 右クリックで終了
        self.canvas.bind("<ButtonPress-3>", lambda e: self.root.destroy())

        # CPU使用率の定期取得開始
        self._update_cpu()

        # アニメーション開始
        self._animate()

    def _load_frames(self):
        """背景除去済みPNGフレームを読み込み、透過部分を透過色に変換"""
        frames_dir = os.path.join(os.path.dirname(__file__), "frames_nobg")
        frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))

        if not frame_files:
            print(f"Error: No frames found in {frames_dir}")
            return

        for i, path in enumerate(frame_files):
            img = Image.open(path).convert("RGBA")

            # アスペクト比を維持してリサイズ
            ratio = self.display_height / img.height
            new_w = int(img.width * ratio)
            img = img.resize((new_w, self.display_height), Image.LANCZOS)

            # 透過部分を透過色で塗りつぶしたRGB画像を作成
            bg = Image.new("RGB", img.size, TRANSPARENT_COLOR)
            bg.paste(img, mask=img.split()[3])  # アルファチャンネルをマスクに使用

            self.frames.append(ImageTk.PhotoImage(bg))

            if (i + 1) % 50 == 0:
                print(f"Loading frames... {i + 1}/{len(frame_files)}")

        print(f"Loaded {len(self.frames)} frames")

    def _get_speed_multiplier(self):
        """CPU使用率に応じた速度倍率を返す
        0%   -> 0.3x (ゆっくり)
        25%  -> 1.0x (通常)
        100% -> 3.0x (超高速)
        """
        cpu = self.cpu_percent
        if cpu <= 25:
            return 0.3 + (cpu / 25) * 0.7  # 0.3 ~ 1.0
        else:
            return 1.0 + ((cpu - 25) / 75) * 3.0  # 1.0 ~ 3.0

    def _update_cpu(self):
        """CPU使用率をリアルタイムで更新"""
        self.cpu_percent = psutil.cpu_percent(interval=None)
        self.root.after(200, self._update_cpu)

    def _animate(self):
        """固定間隔で呼び出し、速度に応じてフレームを進める"""
        TICK_MS = 16  # ~60Hz固定でチェック

        frame_idx = int(self.frame_index) % len(self.frames)
        self.canvas.itemconfig(self.image_id, image=self.frames[frame_idx])

        # 速度に応じて進めるフレーム数（小数で蓄積）
        speed = self._get_speed_multiplier()
        self.frame_index += speed * (self.fps * TICK_MS / 1000)
        if self.frame_index >= len(self.frames):
            self.frame_index -= len(self.frames)

        self.root.after(TICK_MS, self._animate)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # CPU計測を初期化（最初の呼び出しは0を返すため）
    psutil.cpu_percent(interval=None)
    app = CpuDancer()
    app.run()
