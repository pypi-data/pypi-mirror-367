import tkinter as tk
from tkinter import messagebox
import random

def whomadethis():
    messagebox.showinfo("Creator Info", "This was created by Dev Dubey - 17-M - 2025/08/07")


items = ["🍎", "🍍", "7️⃣", "🍒", "🥕"]
initial_balance = 10000

class CasinoApp:
    def __init__(self):
        self.balance = initial_balance
        
        self.window = tk.Tk()
        self.window.title("🍒 DevsCasino Slot Machine 🎰")
        self.window.geometry("410x340")
        self.window.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.window, text="🎰 WELCOME TO DEVS CASINO 🎰", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        self.balance_label = tk.Label(self.window, text=f"Current Balance: ₹{self.balance}", font=("Arial", 13))
        self.balance_label.pack(pady=5)

        bet_frame = tk.Frame(self.window)
        bet_frame.pack(pady=6)
        bet_label = tk.Label(bet_frame, text="Enter Bet:", font=("Arial", 11))
        bet_label.pack(side="left")
        self.bet_entry = tk.Entry(bet_frame, width=10, font=("Arial", 11))
        self.bet_entry.pack(side="left", padx=4)

        slots_frame = tk.Frame(self.window)
        slots_frame.pack(pady=12)
        self.slot_labels = []
        for i in range(3):
            lbl = tk.Label(slots_frame, text=items[i], font=("Arial", 36))
            lbl.pack(side="left", padx=15)
            self.slot_labels.append(lbl)

        buttons_frame = tk.Frame(self.window)
        buttons_frame.pack(pady=16)
        spin_btn = tk.Button(buttons_frame, text="Spin!", command=self.spin, font=("Arial", 12), width=10, bg="gold")
        spin_btn.pack(side="left", padx=10)
        quit_btn = tk.Button(buttons_frame, text="Quit", command=self.quit_game, font=("Arial", 12), width=10)
        quit_btn.pack(side="left", padx=10)

        self.spin_button = spin_btn

    def spin(self):
        try:
            bet = int(self.bet_entry.get())
            if bet <= 0:
                messagebox.showwarning("Invalid Bet", "Bet must be more than zero.")
                return
            if bet > self.balance:
                messagebox.showwarning("Not enough balance", "You don't have enough money for that bet.")
                return
        except ValueError:
            messagebox.showwarning("Invalid input", "Please enter a valid number.")
            return

        # Random slot picks
        results = [random.choice(items) for _ in range(3)]
        for i, lbl in enumerate(self.slot_labels):
            lbl.config(text=results[i])

        # Game logic
        if results[0] == results[1] == results[2]:
            winnings = bet * 10
            self.balance += winnings
            self.balance_label.config(text=f"💰 JACKPOT! You win 10x your bet!\nBalance: ₹{self.balance}", fg="green")
        elif results[0] == results[1] or results[1] == results[2] or results[0] == results[2]:
            winnings = bet * 2
            self.balance += winnings
            self.balance_label.config(text=f"✨ Two matched! You win 2x your bet.\nBalance: ₹{self.balance}", fg="green")
        else:
            self.balance -= bet
            self.balance_label.config(text=f"💸 You lost your bet. Better luck next time!\nBalance: ₹{self.balance}", fg="red")

        if self.balance <= 0:
            self.balance_label.config(text="❌ You're broke. Game over!")
            self.spin_button.config(state="disabled")
            return

        self.bet_entry.delete(0, tk.END)

    def quit_game(self):
        messagebox.showinfo("Game Over", f"Thanks for playing!\nYour final balance: ₹{self.balance}")
        self.window.destroy()

def play():
    app = CasinoApp()
    app.window.mainloop()
