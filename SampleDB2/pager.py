#/usr/bin/env python
import curses
import termios, sys, readline

class Pager(object):
    def __init__(self, prompt, inputs, per_page = None, empty_text = "Empty!"):
        self.inputs = inputs
        self.empty = False
        if len(self.inputs) == 0:
            self.inputs = [empty_text]
            self.empty = True
        self.cur_page = 0
        self.per_page = 10
        self.max = len(self.inputs)
        self.page_count = 1
        self.sel_idx = 0
        self.start_idx = 0
        self.end_idx = 0
        self._dirty = True
        self.prompt = prompt

        attsorig = termios.tcgetattr(sys.stdin.fileno())
        try:
            curses.wrapper(self.main)
        finally:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, attsorig)

    def previous(self):
        if self.sel_idx > self.start_idx:
            self.sel_idx -=1
            self._dirty = True
        else:
            if self.cur_page > 0:
                self.sel_idx = self.start_idx + self.per_page - 1
                self.previous_page()

    def next(self):
        if self.sel_idx < self.end_idx -1:
            self.sel_idx += 1
            self._dirty = True
        else:
            if self.cur_page < self.page_count-1:
                self.sel_idx = self.start_idx
                self.next_page()

    def next_page(self):
        if self.cur_page < self.page_count - 1:
            offset = self.sel_idx - self.start_idx
            self.cur_page += 1
            self.calc_pages()
            self.sel_idx = self.start_idx + offset
            if self.sel_idx > self.max:
                self.sel_idx = self.max - 1
            self._dirty = True

    def previous_page(self):
        if self.cur_page > 0:
            offset = self.sel_idx - self.start_idx
            self.cur_page -= 1
            self.calc_pages()
            self.sel_idx = self.start_idx + offset
            if self.sel_idx > self.max:
                self.sel_idx = self.max - 1
            self._dirty = True

    def repaint(self):
          self._screen.clear()
          self._screen.hline(2, 1, curses.ACS_HLINE,
                           self._screen.getmaxyx()[1])
          self._screen.hline(self._screen.getmaxyx()[0]-3, 1,
                           curses.ACS_HLINE, self._screen.getmaxyx()[1])
          self._screen.addstr(1, 4, self.prompt, curses.A_BOLD)
          self._screen.addstr(self._screen.getmaxyx()[0]-2, 4,
                              "Selected %d out of %d (Page %d of %d)" %
                              (self.sel_idx+1,
                              self.max,
                              self.cur_page+1,
                              self.page_count))
          for idx,i in enumerate(self.page()):
              if self.start_idx + idx == self.sel_idx:
                  attrs = curses.A_STANDOUT
              else:
                  attrs = 0
              s = str(i)
              if len(s) > self._screen.getmaxyx()[1] -12:
                  s = s[: self._screen.getmaxyx()[1] - 12 -3]+"..."
              self._screen.addstr(3+idx*1, 4, s, attrs)
          self._screen.refresh()

    def main(self, stdscr):
        self._screen = stdscr.subwin(0, 0)
#        curses.curs_set(0)
        curses.noecho()
        self._screen.keypad(1)
        while True:
            if self._dirty:
                self.repaint()
                self._dirty = False
            key = self._screen.getch()
            if key == ord("q"):
                self.sel_idx = -1
                break
            elif key == 258:
                self.next()
            elif key == 259:
                self.previous()
            elif key == curses.KEY_NPAGE:
                self.next_page()
            elif key == curses.KEY_PPAGE:
                self.previous_page()
            elif key == 10:
                if self.empty:
                    self.sel_idx = -1
                break
            else:
                pass


    def calc_pages(self):
        self.per_page = self._screen.getmaxyx()[0]-2 -2 -2
        self.page_count = self.max/self.per_page

        if self.page_count == 0 or self.max % self.page_count != 0:
            self.page_count +=1
        self.start_idx = self.cur_page * self.per_page
        self.end_idx = self.start_idx + self.per_page
        if self.end_idx > self.max:
            self.end_idx = self.max


    def page(self):
        self.calc_pages()
        return self.inputs[self.start_idx:self.end_idx]


