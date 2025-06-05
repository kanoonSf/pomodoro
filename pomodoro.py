#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox


class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        master.title("ポモドーロタイマー")
        master.geometry("250x150")  # ウィンドウサイズを調整
        master.resizable(False, False)  # ウィンドウサイズ変更不可

        # --- タイマー設定 ---
        self.pomodoro_duration_sec = 25 * 60  # 25分（秒単位）
        self.short_break_duration_sec = 5 * 60  # 5分（秒単位）
        self.long_break_duration_sec = 30 * 60  # 30分（秒単位）

        self.current_phase_time_left_sec = (
            self.pomodoro_duration_sec
        )  # 現在フェーズの残り時間（秒）
        self.is_timer_running = False  # タイマーが実行中かどうかのフラグ
        self.current_cycle_index = 0
        # 0:ポモドーロ1, 1:短休憩1, 2:ポモドーロ2, ... 7:長休憩 (0から始まるインデックス)
        self.total_pomodoro_in_cycle = 4  # 長休憩までのポモドーロ回数 (4回)

        # ★★★ここが修正点★★★
        self.timer_id = None  # master.afterのIDを保持する変数。ここで初期化する。

        # --- カラー設定 ---
        self.pomodoro_bg_color = "#ADD8E6"  # パステルブルー (LightBlue)
        self.break_bg_color = "#90EE90"  # パステルグリーン (LightGreen)
        self.text_color = "#333333"  # 文字色（濃いグレー）

        # --- GUIコンponentの配置 ---
        # ルートウィンドウをgridレイアウトとして設定
        self.master.grid_rowconfigure(0, weight=1)  # 時間表示行
        self.master.grid_rowconfigure(1, weight=1)  # ステータス・ボタン行
        self.master.grid_rowconfigure(2, weight=1)  # メインボタン行
        self.master.grid_columnconfigure(
            0, weight=1
        )  # 列を一つだけ使用し、伸縮可能にする

        # 時間表示ラベル
        self.time_display_label = tk.Label(
            master,
            text=self._format_time(self.current_phase_time_left_sec),
            font=("Arial", 40, "bold"),
            fg=self.text_color,
            bg=self.pomodoro_bg_color,
        )
        self.time_display_label.grid(row=0, column=0, pady=(10, 0))

        # --- ステータス表示と前後ボタンを配置するフレーム ---
        self.status_navigation_frame = tk.Frame(master, bg=master.cget("bg"))
        self.status_navigation_frame.grid(row=1, column=0, pady=(0, 0))

        # status_navigation_frame内のカラム設定
        self.status_navigation_frame.grid_columnconfigure(
            0, weight=0
        )  # Prevボタンのカラムは固定
        self.status_navigation_frame.grid_columnconfigure(
            1, weight=1
        )  # ステータスラベルのカラムは伸縮
        self.status_navigation_frame.grid_columnconfigure(
            2, weight=0
        )  # Nextボタンのカラムは固定

        # 前のステップへ戻るボタン
        self.prev_phase_button = tk.Button(
            self.status_navigation_frame,
            text="<",
            command=self._go_to_prev_phase,
            width=2,
            height=1,
            font=("Arial", 8),
        )
        self.prev_phase_button.grid(row=0, column=0, padx=(5, 0), sticky="e")

        # ステータス表示ラベル
        self.status_message_label = tk.Label(
            self.status_navigation_frame,
            text="作業時間 (25分)",
            font=("Arial", 10),
            fg=self.text_color,
            bg=master.cget("bg"),
            width=20,
            anchor="center",
        )
        self.status_message_label.grid(row=0, column=1, padx=5, sticky="ew")

        # 次のステップへ進むボタン
        self.next_phase_button = tk.Button(
            self.status_navigation_frame,
            text=">",
            command=self._go_to_next_phase,
            width=2,
            height=1,
            font=("Arial", 8),
        )
        self.next_phase_button.grid(row=0, column=2, padx=(0, 5), sticky="w")
        # --- ここまで ---

        # メインボタンフレーム
        self.control_buttons_frame = tk.Frame(master, bg=self.master.cget("bg"))
        self.control_buttons_frame.grid(row=2, column=0, pady=(5, 0))

        self.start_button = tk.Button(
            self.control_buttons_frame,
            text="開始",
            command=self._start_timer,
            width=6,
            height=1,
            font=("Arial", 8),
        )
        self.start_button.pack(side=tk.LEFT, padx=3)

        self.pause_button = tk.Button(
            self.control_buttons_frame,
            text="一時停止",
            command=self._pause_timer,
            width=6,
            height=1,
            font=("Arial", 8),
            state=tk.DISABLED,
        )
        self.pause_button.pack(side=tk.LEFT, padx=3)

        self.reset_button = tk.Button(
            self.control_buttons_frame,
            text="リセット",
            command=self._reset_timer,
            width=6,
            height=1,
            font=("Arial", 8),
        )
        self.reset_button.pack(side=tk.LEFT, padx=3)

        self._update_ui_for_current_phase(
            start_immediately=False
        )  # 初期表示の更新と色設定

    def _format_time(self, seconds):
        """秒数を MM:SS 形式にフォーマットする"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:00"  # 1分ごとの更新なので、秒は常に00を表示

    def _update_colors(self):
        """現在のタイマー状態に基づいて背景色と文字色を更新する"""
        if self.current_cycle_index % 2 == 0:  # 偶数インデックスはポモドーロ (作業)
            new_bg_color = self.pomodoro_bg_color
        else:  # 奇数インデックスは休憩
            new_bg_color = self.break_bg_color

        self.master.config(bg=new_bg_color)
        self.time_display_label.config(bg=new_bg_color, fg=self.text_color)
        self.status_message_label.config(bg=new_bg_color, fg=self.text_color)
        self.status_navigation_frame.config(bg=new_bg_color)
        self.control_buttons_frame.config(bg=new_bg_color)

    def _get_phase_info(self, cycle_index):
        """指定されたサイクルインデックスのフェーズ情報（時間、ステータス文字列）を返す"""
        if cycle_index % 2 == 0:  # 偶数インデックスはポモドーロ
            display_text = (
                f"作業時間 (25分) - {cycle_index // 2 + 1}回目"
                if cycle_index > 0
                else "作業時間 (25分)"
            )
            duration = self.pomodoro_duration_sec
        elif cycle_index == (self.total_pomodoro_in_cycle * 2) - 1:  # 最後の長休憩
            display_text = "長休憩 (30分)"
            duration = self.long_break_duration_sec
        else:  # 短休憩
            display_text = f"短休憩 (5分) - {cycle_index // 2 + 1}回目"
            duration = self.short_break_duration_sec
        return duration, display_text

    def _update_ui_for_current_phase(self, start_immediately=False):
        """現在のフェーズに合わせてUI表示を更新し、タイマーの状態を制御する"""
        # ここでmaster.afterで設定されている次のupdate_timer_display_logicの呼び出しをキャンセルする
        if self.timer_id is not None:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None  # キャンセル後、IDをリセット

        self.is_timer_running = False  # 必ず一時停止状態にリセット
        self.pause_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        duration, display_text = self._get_phase_info(self.current_cycle_index)
        self.current_phase_time_left_sec = duration
        self.status_message_label.config(text=display_text)
        self.time_display_label.config(
            text=self._format_time(self.current_phase_time_left_sec)
        )
        self._update_colors()

        if start_immediately:
            self._start_timer()

    def _go_to_next_phase(self):
        """次のタイマーフェーズに進む (手動操作)"""
        self.current_cycle_index = (self.current_cycle_index + 1) % (
            self.total_pomodoro_in_cycle * 2
        )
        self._update_ui_for_current_phase(start_immediately=False)

    def _go_to_prev_phase(self):
        """前のタイマーフェーズに戻る (手動操作)"""
        self.current_cycle_index = (
            self.current_cycle_index - 1 + self.total_pomodoro_in_cycle * 2
        ) % (self.total_pomodoro_in_cycle * 2)
        self._update_ui_for_current_phase(start_immediately=False)

    def _update_timer_display_logic(self):
        """タイマーを1分ごとに更新する（ただし、最後の1分は1秒ごとに）"""
        if not self.is_timer_running:
            return

        self._schedule_next_decrement()  # ここから実際の減算処理をキックする

    def _start_timer(self):
        """タイマーを開始（または再開）する"""
        if not self.is_timer_running:
            self.is_timer_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self._schedule_next_decrement()

    def _pause_timer(self):
        """タイマーを一時停止する"""
        if self.is_timer_running:
            self.is_timer_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            if self.timer_id is not None:
                self.master.after_cancel(self.timer_id)
                self.timer_id = None  # キャンセル後、IDをリセット

    def _reset_timer(self):
        """タイマーをリセットする"""
        self._pause_timer()
        self.current_cycle_index = 0
        self._update_ui_for_current_phase(start_immediately=False)

    def _schedule_next_decrement(self):
        """次のタイマー減算をスケジュールするヘルパー関数"""
        if not self.is_timer_running:
            return

        if (
            self.current_phase_time_left_sec <= 60
            and self.current_phase_time_left_sec > 0
        ):
            self.timer_id = self.master.after(1000, self._perform_decrement)
        elif self.current_phase_time_left_sec > 60:
            self.timer_id = self.master.after(60000, self._perform_decrement)
        # else: 時間が0の場合は何もしない（フェーズ終了処理へ行くため）

    def _perform_decrement(self):
        """実際にタイマーの値を減らし、UIを更新し、次の減算をスケジュールする"""
        if not self.is_timer_running:
            return

        if self.current_phase_time_left_sec > 0:
            if self.current_phase_time_left_sec <= 60:
                self.current_phase_time_left_sec -= 1
            else:
                self.current_phase_time_left_sec -= 60
                if self.current_phase_time_left_sec < 0:
                    self.current_phase_time_left_sec = 0

            if self.current_phase_time_left_sec < 60:
                self.time_display_label.config(
                    text=self._format_time_with_seconds(
                        self.current_phase_time_left_sec
                    )
                )
            else:
                self.time_display_label.config(
                    text=self._format_time(self.current_phase_time_left_sec)
                )

            if self.current_phase_time_left_sec <= 0:
                self.is_timer_running = False
                self.pause_button.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL)

                self.master.attributes("-topmost", True)
                self.master.lift()
                self.master.attributes("-topmost", False)

                messagebox.showinfo("ポモドーロ", "時間になりました！")
                self.current_cycle_index = (self.current_cycle_index + 1) % (
                    self.total_pomodoro_in_cycle * 2
                )
                self._update_ui_for_current_phase(start_immediately=True)
            else:
                self._schedule_next_decrement()
        # else: current_phase_time_left_sec <= 0 の場合、上記のif-elseブロックが処理済み

    def _format_time_with_seconds(self, seconds):
        """秒数を MM:SS 形式にフォーマットする (秒も表示)"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"


# アプリケーションの実行
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
