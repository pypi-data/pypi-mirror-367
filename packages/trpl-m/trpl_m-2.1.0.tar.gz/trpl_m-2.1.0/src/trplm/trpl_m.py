import time
import random
import sqlite3
import sys
from rich.console import Console

DB_FILE = "trplm.db"
console = Console()


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            timestamp REAL,
            operations TEXT,
            num_questions TEXT,
            r1_min INTEGER,
            r1_max INTEGER,
            r2_min INTEGER,
            r2_max INTEGER,
            qtype TEXT,
            score INTEGER,
            duration REAL
        )
        """
    )
    conn.commit()
    conn.close()


def get_last_settings():
    """Fetch the most recent game settings from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT operations, num_questions, r1_min, r1_max, r2_min, r2_max, qtype
        FROM sessions
        ORDER BY timestamp DESC
        LIMIT 1
        """
    )
    row = c.fetchone()
    conn.close()
    if row:
        ops_str, num_q, r1_min, r1_max, r2_min, r2_max, qtype = row
        return {
            "ops": list(ops_str),
            "num_q": num_q,
            "r1_min": r1_min,
            "r1_max": r1_max,
            "r2_min": r2_min,
            "r2_max": r2_max,
            "qtype": qtype,
        }
    else:
        console.print("No previous settings found.", style="bold red")
        return None


def record_session(settings, score, duration):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO sessions (
            timestamp, operations, num_questions,
            r1_min, r1_max, r2_min, r2_max,
            qtype, score, duration
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            time.time(),
            "".join(settings["ops"]),
            settings["num_q"],
            settings["r1_min"],
            settings["r1_max"],
            settings["r2_min"],
            settings["r2_max"],
            settings["qtype"],
            score,
            duration,
        ),
    )
    conn.commit()
    conn.close()


def get_settings():
    console.clear()
    console.print("[red]TRPL-M SETTINGS[/red]")

    # Operations
    ops = []
    while not ops:
        console.print(
            "Operations ([red][M][/red]ultiply, [red][D][/red]ivide, [red][A][/red]dd, [red][S][/red]ubtract [red][L][/red]oad last setting, e.g. MDAS):"
        )
        inp = input().strip().lower()
        if inp in ("q", "quit"):
            console.clear()
            return None
        if inp == "l" or inp == "L":
            last = get_last_settings()
            if last:
                return last
            else:
                continue
        for ch in inp.upper():
            if ch in "MDAS":
                ops.append(ch)
        if not ops:
            console.print("Invalid. Pick at least one.", style="bold red")

    # Question count
    console.print("Number of Questions ([red]int[/red] or [red][L][/red]imitless):")
    num_q = input().strip().lower()
    if num_q in ("q", "quit"):
        console.clear()
        return None
    if num_q.isdigit():
        num_q = num_q
    else:
        num_q = "L"

    # Ranges
    console.print(
        "Enter Range1 and Range2 as: [red]min1 max1 min2 max2[/red] (e.g. [red]2 10 2 10[/red]):"
    )
    while True:
        parts_input = input().strip().lower()
        if parts_input in ("q", "quit"):
            console.clear()
            return None
        parts = parts_input.split()
        if len(parts) == 4 and all(p.isdigit() for p in parts):
            r1_min, r1_max, r2_min, r2_max = map(int, parts)
            break
        console.print("Please enter four numbers.", style="bold red")

    # Question type
    console.print("Type ([red][R][/red]andom or [red][S][/red]equential):")
    qtype = input().strip().lower()
    if qtype in ("q", "quit"):
        console.clear()
        return None
    if qtype not in ("r", "s"):
        qtype = "r"

    return {
        "ops": ops,
        "num_q": num_q.upper(),
        "r1_min": r1_min,
        "r1_max": r1_max,
        "r2_min": r2_min,
        "r2_max": r2_max,
        "qtype": "Random" if qtype == "r" else "Sequential",
    }


def generate_questions(settings):
    ops_map = {
        "M": ("*", lambda a, b: a * b),
        "D": ("/", lambda a, b: a // b if b and a % b == 0 else None),
        "A": ("+", lambda a, b: a + b),
        "S": ("-", lambda a, b: a - b),
    }
    items = []
    for op in settings["ops"]:
        sym, fn = ops_map[op]
        for a in range(settings["r1_min"], settings["r1_max"] + 1):
            for b in range(settings["r2_min"], settings["r2_max"] + 1):
                ans = fn(a, b)
                if ans is not None:
                    items.append((a, b, sym, ans))
    if settings["qtype"] == "Random":
        random.shuffle(items)
    if settings["num_q"] not in ("L",):
        return items[: int(settings["num_q"])]
    return items


def play_game(settings):
    questions = generate_questions(settings)
    score = 0
    total = len(questions)
    start = time.time()
    idx = 0

    while idx < total:
        a, b, sym, ans = questions[idx]
        console.clear()
        console.print("[red]TRPL-M[/red]")
        console.print(
            f"Question: [red]{idx+1}[/red]/[red]{total if settings['num_q'] != 'L' else '∞'}[/red]  |  Score: [red]{score}[/red]"
        )
        console.print(f"[red]{a}[/red] {sym} [red]{b}[/red]")
        resp = input().strip().lower()
        if resp in ("q", "quit"):
            console.clear()
            break
        if resp.isdigit() and int(resp) == ans:
            score += 1
            idx += 1
        else:
            console.print(f"{resp}", style="bold white on red")
            time.sleep(0.5)
            score -= 1

    duration = time.time() - start
    console.clear()
    console.print(
        f"Score: [red]{score}[/red]  |  Time: [red]{int(duration//60)}m {int(duration%60)}s[/red]"
    )
    record_session(settings, score, duration)
    input("Press Enter to return to menu.")


def main():
    init_db()
    while True:
        console.clear()
        console.print("[red]TRPL-M[/red]\n[red][P][/red]lay  [red][Q][/red]uit")
        choice = input("").strip().lower()
        if choice in ("q", "quit"):
            console.clear()
            break
        if choice == "p":
            settings = get_settings()
            if settings:
                play_game(settings)
        else:
            console.print("Invalid choice.", style="bold red")
            time.sleep(1)


if __name__ == "__main__":
    main()
