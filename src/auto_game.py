# Leauge Auto Game - main
import tkinter as tk
import win32gui, ctypes
import automate
import time

position_dict = {
	'play button': [127, 39],
	'bottom button': [536, 682],
	'accept button': [643, 555],
	'pvp' : [59, 98],
	"summoner's rift (4)": [127, 216],
	'Aram (4)': [379, 215],
	'One for All (4)': [628, 222],
	'TFT (4)': [868, 217],
	'blind pick': [45, 516],
	'draft pick': [45, 546],
	'ranked solo/duo': [45, 576],
	'ranked flex': [45, 612],
	'left lane option': [483, 476],
	'right lane option': [575, 476],
	'lane panel top': [19, 486],
	'lane panel jungle': [16, 12],
	'lane panel mid': [528, 21],
	'lane panel bottom': [1157, 27],
	'lane panel support': [1234, 486],
	'lane panel fill': [538, 641],
	'champ select search bar': [781, 107],
	'champ select first champ': [378, 170],
	'lock in / ban button': [636, 606],
	'champ select edit rune page button': [439, 685],
	'champ select summoner spell 1': [684, 691],
	'champ select summoner spell 2': [737, 684],
	'cleanse': [624, 474],
	'exhaust': [685, 467],
	'flash': [750, 475],
	'ghost': [801, 473],
	'heal': [621, 536],
	'smite': [687, 538],
	'teleport': [750, 540],
	'ignite': [806, 537],
	'barrier': [627, 604],
	'message box': [141, 682],
	'champ select close rune page' : [1163, 72]
}

def dict_from_win_size(size):
	size = tuple(size)
	if size == (1280, 720):
		return position_dict
	elif size == (1600, 900) or size == (1851, 974):
		return {'accept button': (800, 650)}
	else:
		raise NotImplementedError(f'The window size "{size[0]}x{size[0]}" is not yet supported.')

def ask_lane():
	root = tk.Tk()
	done = tk.BooleanVar()
	done.set(False)
	e = tk.Entry(root)
	e.pack()
	e.focus_set()
	b = tk.Button(root, text='OK', command = lambda : done.set(True))
	b.pack()
	root.wait_variable(done)
	val = e.get()
	root.destroy()
	return val

def ask_champ_set():
	root = tk.Tk()
	root.title('AutoGame')

	done = tk.BooleanVar()
	done.set(False)

	tk.Label(root, text='Champion :').grid(row=0, column=0)
	champ_entry = tk.Entry(root)
	champ_entry.grid(row=0, column=1)
	tk.Label(root, text='Bans :').grid(row=1, column=0)
	bans_entry = tk.Entry(root)
	bans_entry.grid(row=1, column=1)
	tk.Label(root, text='Summoner :').grid(row=2, column=0)
	summ_entry = tk.Entry(root)
	summ_entry.grid(row=2, column=1)
	tk.Button(root, text='OK', command=lambda : done.set(True)).grid(row=3, column=0, columnspan=2)
	champ_entry.focus_set()

	root.wait_variable(done)

	champion = champ_entry.get()
	bans = bans_entry.get().split(', ')
	summs = summ_entry.split(', ')
	root.destroy()

	return {'champion' : champion, 'bans' : bans, 'summoner spells' : summs}

class AutoGame:

	'''
	yo. 644, 584
	accept_match
	ask
	ban_champ
	chose_game_type
	chosen_set
	do_ban
	enter_queue
	game_settings
	lane
	main
	pick_champ
	pre_pick
	set_runes
	set_summoner_spells
	setup
	window_dc
	window_dimensions
	window_id
	'''

	def __init__(self):
		self.game_settings = {}
		self.chosen_set = {}
		self.lane = None # tmp
		self.do_ban = False # tmp

		self.window_dimensions = None
		self.window_id = None
		self.window_dc = None

		self.hwnd = None

	def ask(self):
		self.game_settings = {
			'game mode' : ("summoner's rift (4)", 'draft pick'),
			'lanes' : ('mid', 'jungle'),
			'mid' : {
					0 : {
						'champion' : 'twisted fate',
						'bans' : ['yasuo', 'syndra'],
						'summoner spells' : ('teleport', 'flash')
					},

					1 : {
						'champion' : 'anivia',
						'bans' : ['yasuo', 'kassadin'],
						'summoner spells' : ('ignite', 'flash')
					}
			},
			'jungle' : {
					0 : {
						'champion' : 'ekko',
						'bans' : ['master yi', 'olaf', 'kha'],
						'summoner spells' : ('smite', 'flash')
					},

					1 : {
						'champion' : 'master yi',
						'bans' : ['ekko', 'olaf'],
						'summoner spells' : ('smite', 'flash')
					}
			},
			'top' : {
					0 : {
						'champion' : 'teemo',
						'bans' : ['sett', 'jax', 'ornn'],
						'summoner spells' : ('ignite', 'flash')
					},

					1 : {
						'champion' : 'shen',
						'bans' : ['vayne', 'sett', 'vladimir'],
						'summoner spells' : ('heal', 'flash')
					}
			},
			'bottom' : {
					0 : {
						'champion' : 'tristana',
						'bans' : ['yasuo', 'sivir'],
						'summoner spells' : ('heal', 'flash')
					},

					1: {
						'champion' : 'miss fortune',
						'bans' : ['Jhin', 'Heimerdinger'],
						'summoner spells' : ('heal', 'flash')
					}
			},
			'support' : {
					0 : {
						'champion' : 'anivia',
						'bans' : ['pyke', 'blitzcrank', 'nautilus'],
						'summoner spells' : ('ignite', 'flash')
					},

					1 : {
						'champion' : 'rakan',
						'bans' : ['pyke', 'blitzcrank', 'nautilus'],
						'summoner spells' : ('ignite', 'flash')
					}
			}
		}

		self.game_type = ('rift', 'draft pick')

	def _click(self, pos, sleep_time):
		automate.mouse_click((self.window_dimensions[0] + pos[0], self.window_dimensions[1] + pos[1]))
		time.sleep(sleep_time)

	def _get_cursor(self):
		flags, hcursor, pos = win32gui.GetCursorInfo()
		return pos

	def _set_lanes(self):
		for i, lane in enumerate(self.game_settings['lanes']):
			panel_position = position_dict[['left', 'right'][i] + ' lane option']
			self._click(panel_position, .5)
			lane_position = position_dict['lane panel ' + lane]
			self._click(lane_position, .5)

			if lane == 'fill':
				break

	def _get_pixel(self, x, y):
		return hex(ctypes.windll.gdi32.GetPixel(self.window_dc, x, y))

	def setup(self):
		self.hwnd = win32gui.FindWindow(None, 'League of Legends')
		win32gui.SetForegroundWindow(self.hwnd)
		self.window_dimensions = win32gui.GetWindowRect(self.hwnd)
		self.window_id = win32gui.GetDesktopWindow()
		self.window_dc = win32gui.GetWindowDC(self.window_id)

	def chose_game_type(self):
		self._click(position_dict['play button'], 1)
		self._click(position_dict['pvp'], 1)
		self._click(position_dict[self.game_settings['game mode'][0]], 1)
		self._click(position_dict[self.game_settings['game mode'][1]], 1)
		self._click(position_dict['bottom button'], 2)

	def enter_queue(self):
		if self.game_type[1] in ['draft pick', 'ranked solo/duo', 'flex ranked']:
			self._set_lanes()
		self._click(position_dict['bottom button'], 0)

	def accept_match(self):
		while True:
			print(self._get_pixel(644, 584))
			if self._get_pixel(644, 584) == '0x40301': #0x825a00':
				self._click(position_dict['accept button'], 0)
				break
			time.sleep(1)

	def pre_pick(self):
		self.lane = ask_lane()
		self._click(position_dict['champ select search bar'], .5)
		automate.autoit.send(self.game_settings[self.lane][0]['champion'])

	def ban_champ(self):
		for champ in self.game_settings[self.lane]['bans'][::-1]:
			self._click(position_dict['champ select search bar'], .5)
			automate.autoit.send(champ)
			time.sleep(2)
			self._click(position_dict['champ select first champ'], .5)

	def pick_champ(self):
		for champ_key in list(self.game_settings[self.lane].keys())[::-1]:
			champ = self.game_settings[self.lane][champ_key]['champion']
			self._click(position_dict['champ select search bar'], .5)
			automate.autoit.send(champ)
			time.sleep(2)
			self._click(position_dict['champ select first champ'], .5)
			self.chosen_set = self.game_settings[self.lane][champ_key]
		time.sleep(10)
		self._click(position_dict['lock in / ban button'], 0)

	def set_summoner_spells(self):
		for i in range(2):
			self._click(position_dict['champ select summoner spell '+ str(i + 1)], 2)
			self._click(position_dict[self.chosen_set['summoner spells'][i]], 1)

	def set_runes(self):
		self._click(position_dict['champ select edit rune page button'], 3)
		db = automate.read_db()
		rune_page_name = self.chosen_set['champion'] + ' ' + self.lane
		if rune_page_name in list(db.keys()):
			automate.set_rune_page(rune_page_name)
		else:

			# tmp
			self._click(position_dict['champ select close rune page'], 0)
			exit('no time for op.gg ?')

			rune_set = automate.opgg_to_rune_set(self.chosen_set['champion'], self.lane)
			automate.apply_rune_set('AG: ' + self.chosen_set['champion'] + ' ' + self.lane, rune_set)
		self._click(position_dict['champ select close rune page'], 0)

	def transform_position(self, pos, window_size, context='raw', from_key=False):
		base_size = (1280, 720)
		if from_key:
			pos = dict_from_win_size(window_size)[pos]
			return pos
		else:
			if context == 'raw':
				new_pos = [int(pos[0] * (window_size[0]/base_size[0])), int(pos[1] * (window_size[1]/base_size[1]))]
				return new_pos
			else:
				raise NotImplementedError('Context: "{}" has not been implemented yet.'.format(context))



	def main(self, done=0):
		self.ask()
		if done <= 1:
			print('setup')
			self.setup()
		if done <= 2:
			print('chose_game_type')
			self.chose_game_type()
		if done <= 3:
			print('enter_queue')
			self.enter_queue()
		if done <= 4:
			print('accept match')
			self.accept_match()
		if done <= 5:
			print('pre pick')
			self.pre_pick()
		if self.do_ban and done <= 6:
			print('banning...')
			self.ban_champ()
		else:
			print('do_ban = False :(')
		input('can pick champ ?') # instead of waiting for 30 sec, for now
		if done <= 7:
			print('pick_champ')
			self.pick_champ()
		if done <= 8:
			print('set_summoner_spells')
			self.set_summoner_spells()
		if done <= 9:
			print('set_runes')
			self.set_runes()

if __name__ == '__main__':
	game = AutoGame()
	game.setup()
	game.main()
