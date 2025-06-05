#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox


class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        master.title("ポモドーロタイマー")
        master.geometry("250x180")  # ウィンドウサイズを調整
        master.resizable(False, False)  # ウィンドウサイズ変更不可

        # --- タイマー設定 ---
        self.pomodoro_time = 25 * 60  # 25分
        self.short_break_time = 5 * 60  # 5分
        self.long_break_time = 30 * 60  # 30分

        self.current_time_left = self.pomodoro_time
        self.total_phase_time = self.pomodoro_time  # 現在のフェーズの合計時間
        self.is_running = False
        self.current_cycle_step = (
            0  # 0:ポモドーロ1, 1:短休憩1, 2:ポモドーロ2, ... 7:長休憩
        )
        self.total_pomodoro_cycles = 4  # 長休憩までのポモドーロ回数

        # --- カラー設定 ---
        self.pomodoro_color = "#ADD8E6"  # パステルブルー (LightBlue)
        self.break_color = "#90EE90"  # パステルグリーン (LightGreen)
        self.fill_color = "gray"  # 円グラフの進捗部分の色
        self.empty_color = "lightgray"  # 円グラフの残り時間部分の色

        # --- GUIコンポーネント ---
        self.canvas = tk.Canvas(
            master, width=120, height=120, bg=master.cget("bg"), highlightthickness=0
        )
        self.canvas.pack(pady=(5, 0))

        # 進捗バー描画の初期化
        # まず背景の円を描画
        self.oval_id = self.canvas.create_oval(  # ★このブロックをarc_idの前に移動★
            10,
            10,
            110,
            110,  # 背景の円 (塗りつぶされていない部分)
            outline="",
            fill=self.empty_color,
        )
        # 次に進捗の弧を描画
        self.arc_id = self.canvas.create_arc(
            10,
            10,
            110,
            110,  # x1, y1, x2, y2 (円のbounding box)
            start=90,  # 12時の位置から開始
            extent=0,  # 角度
            fill=self.fill_color,
            outline="",  # 枠線なし
        )
        # ドーナツの穴を表現する中心の円
        self.inner_oval_id = self.canvas.create_oval(
            30,
            30,
            90,
            90,  # x1, y1, x2, y2 (内側の円のbounding box)
            outline="",
            fill=master.cget("bg"),  # ウィンドウの背景色と同じにして穴を開ける
        )

        # 時間表示ラベル（円グラフの上に重ねる）
        self.time_label = tk.Label(
            self.canvas,
            text=self._format_time(self.current_time_left),
            font=("Arial", 18),
            bg=master.cget("bg"),
        )
        self.canvas.create_window(
            60, 60, window=self.time_label
        )  # キャンバスの中心に配置

        # ステータスラベル
        self.status_label = tk.Label(master, text="作業時間 (25分)", font=("Arial", 9))
        self.status_label.pack(pady=(0, 0))

        # ボタンフレーム
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=(0, 0))  # 余白を調整

        self.start_button = tk.Button(
            self.button_frame,
            text="開始",
            command=self.start_timer,
            width=6,
            height=1,
            font=("Arial", 8),
        )
        self.start_button.pack(side=tk.LEFT, padx=3)

        self.pause_button = tk.Button(
            self.button_frame,
            text="一時停止",
            command=self.pause_timer,
            width=6,
            height=1,
            font=("Arial", 8),
            state=tk.DISABLED,
        )
        self.pause_button.pack(side=tk.LEFT, padx=3)

        self.reset_button = tk.Button(
            self.button_frame,
            text="リセット",
            command=self.reset_timer,
            width=6,
            height=1,
            font=("Arial", 8),
        )
        self.reset_button.pack(side=tk.LEFT, padx=3)

        self._update_background_color()  # 初期背景色設定

    def _format_time(self, seconds):
        """秒数を MM:SS 形式にフォーマットする"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def _update_background_color(self):
        """現在のタイマー状態に基づいて背景色と円グラフの色を更新する"""
        current_bg_color = self.master.cget("bg")  # 現在のウィンドウの背景色を取得

        if self.current_cycle_step % 2 == 0:  # 偶数ステップはポモドーロ
            new_bg_color = self.pomodoro_color
        else:  # 奇数ステップは休憩
            new_bg_color = self.break_color

        if current_bg_color != new_bg_color:  # 色が変わる場合のみ更新
            self.master.config(bg=new_bg_color)
            self.canvas.config(bg=new_bg_color)
            self.inner_oval_id = self.canvas.create_oval(
                30, 30, 90, 90, outline="", fill=new_bg_color  # 穴の色も更新
            )
            # time_labelの背景色も更新
            self.time_label.config(bg=new_bg_color)

    def _set_next_phase(self):
        """次のタイマーフェーズ（作業 or 休憩）を設定する"""
        self.current_cycle_step = (self.current_cycle_step + 1) % (
            self.total_pomodoro_cycles * 2
        )

        if self.current_cycle_step == 0:
            self.current_time_left = self.pomodoro_time
            self.total_phase_time = self.pomodoro_time
            self.status_label.config(text="作業時間 (25分)")
        elif self.current_cycle_step % 2 == 0:
            self.current_time_left = self.pomodoro_time
            self.total_phase_time = self.pomodoro_time
            self.status_label.config(
                text=f"作業時間 (25分) - {self.current_cycle_step // 2 + 1}回目"
            )
        elif self.current_cycle_step == (self.total_pomodoro_cycles * 2) - 1:
            self.current_time_left = self.long_break_time
            self.total_phase_time = self.long_break_time
            self.status_label.config(text="長休憩 (30分)")
        else:
            self.current_time_left = self.short_break_time
            self.total_phase_time = self.short_break_time
            self.status_label.config(
                text=f"短休憩 (5分) - {self.current_cycle_step // 2 + 1}回目"
            )

        self._update_background_color()
        self.time_label.config(text=self._format_time(self.current_time_left))
        self.start_timer()

    def _draw_pie_chart(self):
        """円グラフの進捗を描画する"""
        if self.total_phase_time == 0:  # ゼロ除算を避ける
            angle = 0
        else:
            # 残り時間に基づいて角度を計算
            # 360度 = 100%
            # extentは時計回りに増加。残り時間が減るとextentは90度(12時)から反時計回りに減っていく
            # Tkinterのarcはextentがマイナスだと反時計回りになる
            percentage_left = self.current_time_left / self.total_phase_time
            angle = -360 * percentage_left  # マイナスにすることで反時計回りに描画される

        self.canvas.itemconfig(self.arc_id, extent=angle)  # 円グラフの描画を更新
        self.time_label.config(
            text=self._format_time(self.current_time_left)
        )  # 数字も更新

    def update_timer(self):
        """タイマーを1秒ごとに更新する"""
        if self.is_running:
            if self.current_time_left > 0:
                self.current_time_left -= 1
                self._draw_pie_chart()  # 円グラフと数字を更新
                self.master.after(1000, self.update_timer)
            else:
                self.is_running = False
                self.pause_button.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL)
                messagebox.showinfo("ポモドーロ", "時間になりました！")
                self._set_next_phase()

    def start_timer(self):
        """タイマーを開始（または再開）する"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.update_timer()

    def pause_timer(self):
        """タイマーを一時停止する"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)

    def reset_timer(self):
        """タイマーをリセットする"""
        self.pause_timer()
        self.current_cycle_step = 0
        self.current_time_left = self.pomodoro_time
        self.total_phase_time = self.pomodoro_time  # 合計時間もリセット
        self.status_label.config(text="作業時間 (25分)")
        self._update_background_color()
        self._draw_pie_chart()  # 円グラフと数字を初期状態に戻す


# アプリケーションの実行
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
