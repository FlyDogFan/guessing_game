from tkinter import *
import tkinter as tk
from tkinter import font
from random import randint
from timer_thread import TimerThread
from database import LeaderBoard
import os


class CustomDialog(tk.Toplevel):
    def __init__(self, parent, prompt):
        tk.Toplevel.__init__(self, parent)
        self.var = tk.StringVar()
        self.label_1 = tk.Label(self, text="Congratulations!!")
        self.label_2 = tk.Label(self, text=prompt)
        self.entry = tk.Entry(self, textvariable=self.var)
        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)

        self.label_1.pack(side="top", fill="x")
        self.label_2.pack(side="top", fill="x")
        self.entry.pack(side="top", fill="x")
        self.ok_button.pack(side="top")
        self.entry.bind("<Return>", self.on_ok)
        self.lift()

    def on_ok(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.entry.focus_force()
        self.wait_window()
        return self.var.get()


class MyDialog():
    game = None
    # 建立UI 介面
    def __init__(self, parent, guess_game, message, leader_board, round, time):
        top = self.top = Toplevel(parent)
        self.game = guess_game
        self.l = Listbox(top, height=12, width=50)
        Label(top, text=message).pack()
        Label(top, text='leader board').pack()
        leader_board.open()
        new_score = leader_board.is_new_score(time)
        leaderboard_score = leader_board.get_score()
        if message == "You win!" and new_score:
            name = CustomDialog(top, "Enter your name: ").show()
            entry = leader_board.create_entry(time, name, round)
            leader_board.insert_and_sort(entry)

        leader_board.close()
        print(leaderboard_score)
        self.fill_leader_board_score(leaderboard_score)
        self.l.pack()
        Button(top, text="New Game", command=self.new_game).pack()
        Button(top, text="EXIT", command=self.exit).pack()


    def exit(self):
        self.top.destroy()
        self.game.top.destroy()

    def new_game(self):
        self.game.new_game()
        self.top.destroy()

    def fill_leader_board_score(self,scores):
        '''
            將過去結果以相對應的結果顯示出來
        '''
        self.l.insert('end', "{: <5s} {: <15s}  {:12s}  {}".format('rank','name', 'finish time', 'rounds'))
        for rank, entry in enumerate(scores):
            time_str = "{:%H:%M:%S}".format(entry['time'])
            self.l.insert('end', "{: <5d} {: <15s}  {:12s}  {}".format(rank+1,entry['name'],time_str,entry['rounds']))

class GuessGame():
    top = tk.Tk()
    btn_width = 5
    btn_borderwidth = 5
    ft = font.Font(size=15)
    element_column = 5
    l = None
    input = None
    answer_number = None
    round_number = 0
    guess_history = []
    timer_label = None
    timer_text = StringVar()
    timer_thread = None
    end_round = 10
    leader_board = LeaderBoard()
    current_second = 0

    def __init__(self):
        self.answer_number = self.create_number()
        # 開始Timer thread 物件
        self.timer_thread = TimerThread(self.update_time)
        self.current_second = 0
        self.input_number = StringVar()

    # 產生隨機不重複的4位數
    def create_number(self):
        num = str(randint(0, 9))
        while num == "0":
            num = str(randint(0, 9))
        while True:
            number = str(randint(0, 9))
            if str(number) not in num:
                num += number
            if len(num) == 4:
                return num

    def show_number_window(self):
        self.l.insert('end', "Answer: {}".format(self.answer_number))
        self.l.yview(END)

    def exit_game(self):
        self.top.destroy()
    '''
        新遊戲開始會重設所有必要參數
        如果遊戲輸了，則顯示信息。
    '''
    def new_game(self):
        self.timer_thread.stop_thread()
        self.timer_text.set("time: 00:00")
        self.round_number = 0
        self.guess_history = []
        self.l.delete(0, END)
        self.answer_number = self.create_number()
        del self.timer_thread
        self.timer_thread = TimerThread(self.update_time)
        self.timer_thread.start()
        self.input_number.set('')

    def lose_game(self, time=0, rounds=0, message="You lose!"):
        d = MyDialog(self.top, self, message, self.leader_board, rounds, time)
        self.top.wait_window(d.top)

    # 將秒數轉換為分鐘與秒，並更新計時器的label 
    def update_time(self, time):
        second = time % 60
        minute = int(time / 60)
        self.current_second = time
        self.timer_text.set("time: {:02d}:{:02d}".format(minute, second))

    def run_game(self):
        guess_num = str(self.input.get())
        if guess_num == "":
            return
        has_error = False
        '''
            檢測error 並推送到List 上
        '''
        if len(guess_num) != 4:
            self.l.insert('end', "{}   Invalid input!!! (length error) ".format(guess_num))
            has_error = True
        if len(set(guess_num)) != len(guess_num):
            self.l.insert('end', "{}   Invalid input!!! (character repeat) ".format(guess_num))
            has_error = True
        if guess_num.isdigit() is False:
            self.l.insert('end', "{}   Invalid input!!! (character error) ".format(guess_num))
            has_error = True
        if guess_num in self.guess_history:
            self.l.insert('end', "{}   You guess this number before try again!!!".format(guess_num))
            has_error = True
        '''
            如果沒有錯誤就執行這一小段
        '''
        if has_error is False:
            self.round_number += 1
            count = [0, 0]
            if guess_num == self.answer_number:
                self.l.insert('end', "{}   You guess it right!!".format(guess_num))
                self.l.insert('end', "{}".format(self.timer_text.get()))
                self.l.yview(END)
                self.timer_thread.stop_thread()
                self.lose_game(self.current_second, self.round_number, message="You win!")
                return
            '''
                 計算判斷數字的重複與重疊數
            '''
            for c, character in enumerate(list(guess_num)):
                for g, character2 in enumerate(list(self.answer_number)):
                    if g == c and character == character2:
                        count[0] += 1
                    elif character == character2:
                        count[1] += 1
            self.l.insert('end', "Round{} {} {}A{}B".format(self.round_number, guess_num, count[0], count[1]))
            self.guess_history.append(guess_num)
            if self.round_number >= self.end_round:
                self.l.insert('end', "You lose! Answer: {}".format(self.answer_number))
                self.timer_thread.stop_thread()
                self.lose_game()
        self.input.delete(0, END)
        self.l.yview(END)
    '''

    '''
    def create_ui(self):
        frame = Frame(self.top)
        frame.pack()
        self.timer_label = Label(frame, text="time: 00:00", textvariable=self.timer_text)
        self.timer_label.pack()
        title = Label(frame, text="Welcome to Number Game")
        title.pack()
        self.input = Entry(frame, textvariable=self.input_number,bd=1)
        self.input.pack()
        Button(frame, text="Run", font=self.ft,
               command=self.run_game).pack()
        self.l = Listbox(frame, height=20, width=100)
        self.l.pack()
        Button(frame, text="Show Answer", borderwidth=self.btn_borderwidth, font=self.ft,
               command=self.show_number_window).pack()
        Button(frame, text="New Game", borderwidth=self.btn_borderwidth, font=self.ft,
               command=self.new_game).pack()
        Button(frame, text="Exit", borderwidth=self.btn_borderwidth, font=self.ft,
               command=self.exit_game).pack()

        self.l.yview(END)

        self.timer_thread.start()
        return self.top


if __name__ == '__main__':
    guess = GuessGame()
    guess.create_ui().mainloop()
# thread = TimerThread(print_time)
# thread.run()
