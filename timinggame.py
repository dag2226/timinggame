import tkinter as tk
from random import randint
from math import pi, cos, sin

class GameRing(object):
	def __init__(self, canvas, x0, y0, x1, y1, width, color):
		self.canvas = canvas
		self.x0, self.y0, self.x1, self.y1 = x0 + width, y0 + width, x1 - width, y1 - width
		self.width = width
		self.color = color

		w2 = self.width / 2

		self.outer_circle = self.canvas.create_oval(self.x0 - w2, self.y0 - w2, self.x1 + w2, self.y1 + w2, outline=self.color)
		self.inner_circle = self.canvas.create_oval(self.x0 + w2, self.y0 + w2, self.x1 - w2, self.y1 - w2, outline=self.color)

		self.target_ang = None
		self.target_extent = 30
		self.target = None

		self.score = 0

		self.generate_target()

	def generate_target(self):
		# Generate random target_ang from target_distance_tolerance to 360
		self.target_ang = randint(0, 360)
		# Generate arc from target_ang to target_ang + target_extent
		self.target = self.canvas.create_arc(self.x0, self.y0, self.x1, self.y1, start=self.target_ang, extent=self.target_extent, width=self.width, style='arc', outline=self.color)
		# Lower z-index of target below cursor
		self.canvas.tag_lower(self.target)


class Cursor(object):
	def __init__(self, canvas, top_left, lower_right, width):
		self.canvas = canvas

		self.cursor_ang = 0
		self.width = width

		self.center_x = self.center_y = (lower_right + top_left) / 2
		self.length = (lower_right - top_left - self.width) / 2
		
		rad_ang = -1 * self.get_angle_in_rad(self.cursor_ang)
		start_x, start_y = self.center_x + self.width * cos(rad_ang), self.center_y + self.width * sin(rad_ang)
		end_x, end_y = self.center_x + self.length * cos(rad_ang), self.center_y + self.length * sin(rad_ang)

		self.cursor = self.canvas.create_line(start_x, start_y, end_x, end_y, width = 1, fill = 'white')

		self.running = False

	def get_angle_in_rad(self, angle_in_deg):
		return angle_in_deg * pi / 180

	def start(self):
		if not self.running:
			self.running = True
			self.canvas.after(10, self.step)

	def step(self):
		if self.running:
			self.cursor_ang = (self.cursor_ang + 2) % 360
			
			rad_ang = -1 * self.get_angle_in_rad(self.cursor_ang)
			start_x, start_y = self.center_x + self.width * cos(rad_ang), self.center_y + self.width * sin(rad_ang)
			end_x, end_y = self.center_x + self.length * cos(rad_ang), self.center_y + self.length * sin(rad_ang)
			
			self.canvas.coords(self.cursor, start_x, start_y, end_x, end_y)
			self.canvas.after(10, self.step)

	def toggle_pause(self):
		if self.running:
			self.running = not self.running

class Application(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid()

		self.canvas = tk.Canvas(self, width=300, height=300, bg='black', borderwidth=0, highlightthickness=0)
		self.canvas.grid(row=0, column=0, columnspan=4)
		
		self.top_left = 10
		self.lower_right = 290
		self.width = 25
		
		# Create cursor
		self.cursor = Cursor(self.canvas, self.top_left, self.lower_right, self.width)
		
		# Create game rings
		self.colors = ['green', 'lightblue', 'yellow', 'red']
		self.keys = ['a', 's', 'd', 'f']
		self.binds = []

		self.circles = []

		for i in range(0, 4):
			def make_lambda(x):
				return lambda event: self.cursor_activated(event)
			self.circles.append(GameRing(self.canvas, self.top_left, self.top_left, self.lower_right, self.lower_right, self.width, self.colors[i]))
			self.master.bind(self.keys[i], make_lambda(i))

			self.top_left += self.width
			self.lower_right -= self.width

		# Create score text variables
		self.total_score = tk.IntVar()
		self.g_score = tk.IntVar()
		self.b_score = tk.IntVar()
		self.y_score = tk.IntVar()
		self.r_score = tk.IntVar()

		# Create score display
		self.total_score_display = tk.Label(self, textvariable=self.total_score, bg='black', fg='white')
		self.total_score_display.grid(row=0, column=0, columnspan=4)

		self.g_score_display = tk.Label(self, textvariable=self.g_score, bg='black', fg='green')
		self.g_score_display.place(in_=self.canvas, relx=.1, rely=.1, anchor=tk.NW)
		self.b_score_display = tk.Label(self, textvariable=self.b_score, bg='black', fg='lightblue')
		self.b_score_display.place(in_=self.canvas, relx=.9, rely=.1, anchor=tk.NE)
		self.y_score_display = tk.Label(self, textvariable=self.y_score, bg='black', fg='yellow')
		self.y_score_display.place(in_=self.canvas, relx=.1, rely=.9, anchor=tk.SW)
		self.r_score_display = tk.Label(self, textvariable=self.r_score, bg='black', fg='red')
		self.r_score_display.place(in_=self.canvas, relx=.9, rely=.9, anchor=tk.SE)
		
		# Create control buttons
		self.start_button = tk.Button(self, text='Start', command=self.start, bg='green')
		self.start_button.grid(row=1, column=0, sticky='sewn')
		self.pause_button = tk.Button(self, text='Pause', command=self.pause, bg='lightblue')
		self.pause_button.grid(row=1, column=1, sticky='sewn')
		self.reset_button = tk.Button(self, text='Reset', command=self.reset, bg='yellow')
		self.reset_button.grid(row=1, column=2, sticky='sewn')
		self.quit_button = tk.Button(self, text='Quit', command=self.quit, bg='red')
		self.quit_button.grid(row=1, column=3, sticky='sewn')

	def start(self):
		self.cursor.start()
		self.canvas.after(10, self.step)

	def step(self):
		self.total_score.set(sum(circle.score for circle in self.circles))
		self.g_score.set(self.circles[0].score)
		self.b_score.set(self.circles[1].score)
		self.y_score.set(self.circles[2].score)
		self.r_score.set(self.circles[3].score)
		self.canvas.after(10, self.step)

	def pause(self):
		self.cursor.toggle_pause()

	def reset(self):
		self.destroy()
		self.__init__()
	
	def cursor_activated(self, key):
		if self.cursor.running:
			i = self.keys.index(key.keysym)
			if self.circles[i].target_ang <= self.cursor.cursor_ang <= (self.circles[i].target_ang + self.circles[i].target_extent):
				self.circles[i].target_extent -= 1
				self.circles[i].score += 1
			else:
				self.circles[i].target_extent += 2
				self.circles[i].score -= 2
			if self.circles[i].score < 0:
				self.circles[i].score = 0
			if self.circles[i].target_extent > 30:
				self.circles[i].target_extent = 30
			self.canvas.delete(self.circles[i].target)
			self.circles[i].generate_target()


if __name__ == '__main__':
	app = Application()
	app.master.title('Timing Game')
	app.mainloop()