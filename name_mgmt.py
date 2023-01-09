from unicurses import *
import sqlite3


def main() -> None:
    con = sqlite3.connect("store.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY AUTOINCREMENT, data STRING)")

    def get_data() -> list:
        return cur.execute("SELECT * FROM entries").fetchall()

    l: list = get_data()
    highlight: int = 0
    stdscr = initscr()
    keypad(stdscr, True)
    clear()
    noecho()
    cbreak()
    curs_set(0)

    def print_menu(highlight: int) -> None:
        for i in range(0, len(l)):
            if highlight == i:
                attron(A_REVERSE)
                mvaddstr(i, 0, f"{i}. {l[i]['data']}")
                attroff(A_REVERSE)
            else:
                mvaddstr(i, 0, f"{i}. {l[i]['data']}")
        refresh()

    def recvstr() -> str:
        s: str = ""
        while True:
            c: int = getch()
            if c == KEY_ENTER or c == CCHAR('\n'):
                clear()
                break
            elif (c == KEY_BACKSPACE or c == CCHAR("\u0008")) and len(s) > 0:
                s = s[:-1]
                y, x = getyx(stdscr)
                mvdelch(y, x-1)
                refresh()
                continue
            s += chr(c)
            addch(c)
            refresh()
        return s

    print_menu(highlight)

    while True:
        c: int = getch()
        if c == KEY_UP:
            if highlight == 0:
                highlight == len(l) - 1
            else:
                highlight -= 1
        elif c == KEY_DOWN:
            if highlight == len(l) - 1:
                highlight = 0
            else:
                highlight += 1
        elif c == CCHAR('e') or c == KEY_ENTER or c == CCHAR('\n'):
            if highlight != len(l):
                mvaddstr(23, 0, f"Edit {highlight}: ")
                s = recvstr()

                cur.execute(
                    "UPDATE entries SET data = ? WHERE entries.id = ?", (s, l[highlight]["id"]))
                con.commit()
                l: list = get_data()
                refresh()
        elif c == CCHAR('a'):
            mvaddstr(23, 0, f"New entry: ")
            v = recvstr()
            cur.execute("INSERT INTO entries (data) VALUES (?)", (v, ))
            con.commit()
            l: list = get_data()
            refresh()
        elif c == KEY_BACKSPACE or c == CCHAR('\u0008'):
            if highlight != len(l):
                clear()
                mvaddstr(23, 0, f"Removed entry {highlight}")
                old: dict = l[highlight]
                cur.execute("DELETE FROM entries WHERE id = ?", (old["id"],))
                con.commit()
                l: list = get_data()
                refresh()
        elif c == CCHAR('x'):
            break
        print_menu(highlight)

    refresh()
    endwin()


if __name__ == "__main__":
    main()
