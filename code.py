#!/usr/bin/env python3

import pandas as pd
import json
import os
import re
import time

start_time = time.time()

def main():

	# String normalization: punctuation (substituted by space), stop characters (can be inside model name, so just deleted) and aliases
	punctuation = [",", ":", ";", "!", "?", "(", ")", "[", "]", "{", "}", "/", "|", '"', "*"]
	stop_chars = ["-"]
	aliases = {"cannon": "canon", "canonpowershot": "canon", "eos": "canon", "usedcanon": "canon", "fugi": "fujifilm", "fugifilm": "fujifilm", "fuji": "fujifilm",
			   "fujufilm": "fujifilm", "general": "ge", "gopros": "gopro", "hikvision3mp": "hikvision", "hikvisionip": "hikvision", "bell+howell": "howell",
			   "howellwp7": "howell", "minotla": "minolta", "canon&nikon": "nikon", "olympuss": "olympus", "panosonic": "panasonic", "pentax": "ricoh",
			   "ssamsung": "samsung", "repairsony": "sony", "elf": "elph", "s480016mp": "s4800", "vivicam": "v", "plus": "+", "1080p": "", "720p": ""}

	# List of common manufacturers for the brand extraction
	brands = ["aiptek", "apple", "argus", "benq", "canon", "casio", "coleman", "contour", "dahua", "epson", "fujifilm", "garmin", "ge", "gopro", "hasselblad",
			  "hikvision", "howell", "hp", "intova", "jvc", "kodak", "leica", "lg", "lowepro", "lytro", "minolta", "minox", "motorola", "mustek", "nikon",
			  "olympus",  "panasonic", "pentax", "philips", "polaroid", "ricoh", "sakar", "samsung", "sanyo", "sekonic", "sigma", "sony", "tamron", "toshiba",
			  "vivitar", "vtech", "wespro", "yourdeal"]

	# List of measure suffixes to be ignored for the model extraction
	measures = ["cm", "mm", "nm", "inch", "gb", "mb", "mp", "megapixel", "megapixels", "mega", "ghz", "hz", "mah", "cmos", "mps"]

	# Read JSON specifications
	path = 'Dataset/2013_camera_specs'

	solved_specs = []
	unsolved_specs = []

	for folder_name in os.listdir(path):
		for file_name in os.listdir(path + '/' + str(folder_name)):
			with open(path + '/' + str(folder_name) + '/' + str(file_name), 'r') as data:
				camera = {}

				# Read the JSON content as a dictionary
				spec = json.load(data)
				spec = dict((k.lower(), v) for k, v in spec.items())

				# Add file path as 'id' attribute
				camera['id'] = str(folder_name) + '//' + str(file_name[:-5])

				# Add and normalize 'page_title' attribute
				camera['page_title'] = spec['<page title>'].lower()
				for p in punctuation:
					camera['page_title'] = camera['page_title'].replace(p, ' ')
				for c in stop_chars:
					camera['page_title'] = camera['page_title'].replace(c, '')

				splitted = camera['page_title'].split()

				# Resolve aliases
				for s in splitted:
					if s in aliases.keys():
						index = splitted.index(s)
						splitted[index] = aliases[s]
						s = splitted[index]

				# Extract brand (no more only among the first 5 words, but in the whole string)
				brand = 'none'
				for s in splitted:
					if s in brands:
						brand = s
						break

				# Manage specific elements of each brand
				prefixes = []
				suffixes = []
				models = [] # only alphabetic or only numeric models (so not retrieved through regular expressions)
				exceptions = [] # alphanumeric words which do not represent models
				equivalences = {} # equivalent names for the same model

				if brand == 'aiptek':
					prefixes = ['dv']
					exceptions = ['3d']
				elif brand == 'argus':
					prefixes = ['dc']
				elif brand == 'apple':
					prefixes = ['iphone','quicktake']
				elif brand == 'canon':
					prefixes = ['a', 'bg', 'elph', 'hf', 'ixus', 'ixy', 'pro', 'sd', 'sx']
					suffixes = ['c', 'd', 'ds', 'dx', 'x']
					models = ['ixusi', 'ixusii', 'xs', 'xsi', 'xt', 'xti']
					exceptions = ['100v', '1280x', '130ft', '2000s', '3color', '3x', '40m', '4608x', '4colors', '4x', '50x', '5260b009', '5x', '6colors', '70db',
								  '70dkis', '70dpk', '70dsk', '8160b001', '8231b005', '8595b005', '8x', '9126b003', '9156b001', 'd700', 'ew73b', 'g151428',
								  'gfb064', 'k47']
					equivalences = {'600db': '600d', '600dk': '600d', '600dtk': '600d', 'a34000': 'a3400', 'eos1d mark3': '1d mark3', 'eos1dc': '1dc',
									'eos1dx': '1dx', 'eos40d': '40d', 'eos7d': '7d', 'g1xb': 'g1x', 'g1xc': 'g1x', 's110bk': 's110', 's120bk': 's120',
									's200bk': 's200', 'sx170isbk': 'sx170', 'sx400isbk': 'sx400', 'sx400isr': 'sx400', 'sx600hsbk': 'sx600', 'sx700hsbk': 'sx700',
									'sx700hsr': 'sx700'}
				elif brand == 'casio':
					prefixes = ['ex', 'qv']
					models = ['tryx']
					exceptions = ['2colors', '3x', 'fc150', 'l00ks', 'w0w']
					equivalences = {'exh10bk': 'exh10', 'exh30bk': 'exh30', 'exs10a': 'exs10', 'exs5pe': 'exs5', 'exs770rd': 'exs770', 'extr15w': 'extr15',
									'exz80a': 'exz80', 'tr350': 'extr350', 'tr700': 'extr700', 'tryx': 'extr100', 'zr700': 'exzr700'}
				elif brand == 'coleman':
					exceptions = ['xtreme2', 'xtreme3']
					equivalences = {'2v7wpo': '2v7wp', '2v7wpp': '2v7wp'}
				elif brand == 'contour':
					prefixes = ['roam']
				elif brand == 'dahua':
					exceptions = ['1.3m', '1.3mpl', '100m', '150m', '18x', '2048x1536', '20m', '20x', '30x', '3m', '3x', '50m', '700tvl', 'h.246', 'h.264', 'h264', 'ik10',
								  'ip66', 'ir100m', 'onvif2.0', 'p2p', 'rs485']
				elif brand == 'epson':
					prefixes = ['r', 'rd']
				elif brand == 'fujifilm':
					prefixes = ['ax', 'ds', 'hs', 'instax', 'jx', 'mx', 'quicksnap', 'x', 'xpro', 'z']
					suffixes = ['exr', 'fd']
					models = ['1300', '2300', '2400', '2600', '2650', '2800', '3800', '4700', '4900']
					exceptions = ['12x', '2.7in', '3d', '30x', '5in1', '5x', 'casioexg1', 'f550']
					equivalences = {'fxjx500pink': 'jx500', 'jz250black': 'jz250'}
				elif brand == 'garmin':
					suffixes = ['elite']
					models = ['virb', 'virbelite']
				elif brand == 'ge':
					suffixes = ['w']
					equivalences = {'c1233bk': 'c1233', 'c1440w': 'c1440', 'e1680wbk': 'e1680w', 'x2600w': 'x2600', 'x500bk': 'x500'}
				elif brand == 'gopro':
					prefixes = ['hero']
					suffixes = ['+']
					exceptions = ['30m', '3d', '45m', '5m', 'h3', 'st29']
				elif brand == 'hasselblad':
					prefixes = ['cfv']
					suffixes = ['40', '50']
					models = ['lunar', 'stellar']
				elif brand == 'hikvision':
					prefixes = ['ds']
					exceptions = ['100m', '10m', '12v', '20m', '20x', '30m', '32g', '50m', '960p', 'h.246', 'h.264', 'h.624', 'hikvision1080p', 'ip65', 'ip66',
								  'ir100m', 'ir30m', 'm14', 'no.1', 'rj45', 'rs485']
					equivalences = {'camerads2cd2032i': 'ds2cd2032i', 'chinads2cd2612fis': 'ds2cd2612fis', 'nds2cd2612fis': 'ds2cd2612fis',
									'poeds2cd2112i': 'ds2cd2112i'}
				elif brand == 'howell':
					prefixes = ['take']
					exceptions = ['splash2']
					equivalences = {'dc5r': 'dc5', 'take1hd': 'take1', 'wp10y': 'wp10'}
				elif brand == 'hp':
					prefixes = ['r']
					models = ['215', '315', '318', '320', '435', '618', '635', '720', '735', '812', '850', '935', '945']
					exceptions = ['8x']
					equivalences = {'r6074': 'r607'}
				elif brand == 'intova':
					prefixes = ['cp', 'ic']
				elif brand == 'kodak':
					prefixes = ['cx', 'dc', 'dcs', 'dx', 'kv', 'm']
					exceptions = ['10x', '3x', '7c55', 'kodakc182bluecolor', 'mpeg4', 'v2.21']
					equivalences = {'fz41bk': 'fz41'}
				elif brand == 'leica':
					prefixes = ['digilux', 'dlux', 'lux', 'vlux', 'x']
					suffixes = ['p']
					models = ['112', '114', '240', '701', '9', 'xvario']
					exceptions = ['0.68x']
					equivalences = {'9p': 'm9p', 'd6': 'dlux6', 'dluxd3': 'dlux3', 'typ240': 'm240'}
				elif brand == 'lg':
					exceptions = ['32in', '3d', 'pn4500']
				elif brand == 'minolta':
					prefixes = ['x', 'xg']
					suffixes = ['si']
					models = ['5', '7', 'blowout']
					exceptions = ['3x', 'vc7d']
				elif brand == 'minox':
					models = ['dcc', 'dsc', 'minoctar']
				elif brand == 'motorola':
					prefixes = ['phone']
				elif brand == 'mustek':
					prefixes = ['mdc']
				elif brand == 'nikon':
					prefixes = ['aw', 'd', 'l', 's', 'tc', 'v']
					models = ['25462', '25480', '26286', '2000', '2100', '2200', '2500', '3100', '3200', '3500', '3700', '4200', '4300', '4500', '4600', '4800',
							  '5000', '5100', '5400', '5600', '5700', '600', '700', '7600', '775', '7900', '800', '8400', '8700', '8800', '885', '950', '990',
							  '995', 'a', 'df']
					exceptions = ['10x', '130ft', '2colors', '2pcs', '30x', '3colors', '3d', '3x', '40m', '42x', '4g', '4x', '6x', '7x', 'k164318', 'm130ft',
								  'nikon1', 's2868', 's3090', 's800bk']
					equivalences = {'1j2': 'j2', '25462': 'd3000', '25480': 'd800', '26286': 'p7100', 'd1oo': 'd100', 'd32oo': 'd3200', 'd7100lk18': 'd7100',
									'e3200': '3200', 'e5400': '5400', 'e5600': '5600', 'e8400': '8400', 'e995': '995', 'l610b': 'l610', 's3600sl': 's3600',
									's6600wh': 's6600', 'so1': 's01', 'so2': 's02'}
				elif brand == 'olympus':
					prefixes = ['c', 'd', 'e', 'em', 'ep', 'epm', 'f', 'fe', 'sh', 'sp', 'sz', 't', 'tg', 'vg', 'vh', 'vr', 'x', 'xz']
					suffixes = ['sw', 'uz']
					models = ['105', '300', '400', '410', '500', '600', '710', '730', '740', '750', '760', '780', '800', '810', '820', '830', '850', '1000',
							  '1010', '1040', '1200', '3000', '5010', '6000', '6010', '6020', '7000', '7010', '7030', '7040', '8000', '8010', '9000', '9010']
					exceptions = ['10.7x', '10x', '1134shot', '15x', '1m', '20x', '26gvy1ozukj', '36x', '3d', '3x', '40m', '50x', '7x', 'dem10', 'dscrx100', 'f2',
								  'j1', 'v103020bu000', 'x21']
					equivalences = {'550uz': 'sp550uz', 'emp1': 'epm1', 'tg630ihs': 'tg630', 'tg850ihs': 'tg850', 'tough8000': '8000'}
				elif brand == 'panasonic':
					prefixes = ['fs', 'fx', 'hc', 'hx', 'tz']
					models = ['141', '161', '91']
					exceptions = ['100v', '10x', '20x', '35x', '3colors', '4colors', '4x', '5x', '60x', '8x']
					equivalences = {'dmcgh4kbody': 'gh4'}
				elif brand == 'philips':
					exceptions = ['3d', '3x']
					equivalences = {'p44417a': 'p44417', 'p44417b': 'p44417', 'p44417p': 'p44417', 'p44417s': 'p44417', 'p44417w': 'p44417'}
				elif brand == 'polaroid':
					prefixes = ['is','pdc']
					models = ['320', 'pogo']
					equivalences = {'if045b': 'if045', 'z2300blk': 'z2300'}
				elif brand == 'ricoh':
					prefixes = ['i', 'ist', 'k', 'mx', 'q', 'wg', 'x']
					suffixes = ['ii', 'iis']
					models = ['30', '60', 'efina', 'gr', 'gxr', 'istd', 'istdl', 'istds', 'km', 'kr', 'kx', 'q+', 'qdigital', 'qrare', 'qwhite', 'theta', 'wgii',
							  'wgiii']
					exceptions = ['4x', 'opti0']
					equivalences = {'km': 'k2000', 'q+': 'q', 'q01': 'q', 'q12': 'q', 'qdigital': 'q', 'qrare': 'q', 'qs102': 'qs1', 'qwhite': 'q',
									'wg3gps': 'wg3', 'wgii': 'wg2', 'wgiii': 'wg3'}
				elif brand == 'samsung':
					prefixes = ['dv', 'mv', 'note', 'pl', 'sh', 'st', 'tl', 'wb']
					exceptions = ['18x', '20m', '21x', '21x23', '240hz', '26x', '2colors', '3d', '3g', '3x', '4k', '5m', 'camera2', 'case2013', 'ip66']
					equivalences = {'dv50bk': 'dv50', 'ecdv150f': 'dv150f', 'ecpl120': 'pl120', 'ecpl170': 'pl170', 'ecsh100': 'sh100', 'ecst700': 'st700',
									'ekgc110zwaxar': 'ekgc110', 'ekgc200zkabtu': 'ekgc200', 'ekgc200zkawtu': 'ekgc200', 'ekgc200zkaxar': 'ekgc200', 'ekgc200zkaxsa': 'ekgc200',
									'evnx2000bfwca': 'nx2000', 'evnx300zbsvus': 'nx300', 'gc100': 'ekgc100', 'gc110': 'ekgc110', 'gc120': 'ekgc120',
									'gc120bkv': 'ekgc120', 'gc200': 'ekgc200', 'gc200zwaxar': 'ekgc200', 'hz15wgray': 'hz15w', 'nx2000bfwca': 'nx2000',
									'sl102pbp': 'sl102', 'un22f5000afxza': 'un22f5000', 'wb110zbarus': 'wb110', 'wb22oof': 'wb2200f', 'wb350.': 'wb350'}
				elif brand == 'sanyo':
					prefixes = ['s']
					exceptions = ['4x', '5x']
					equivalences = {'s1285w': 's1285', 's770pu': 's770'}
				elif brand == 'sigma':
					prefixes = ['f', 'sd']
					suffixes = ['merrill', 'quattro']
				elif brand == 'sony':
					prefixes = ['dsc', 'hdr', 'ilca', 'ilce', 'kdf', 'kdl', 'nex', 'nsx']
					suffixes = ['tvl']
					exceptions = ['0whli', '10x', '12x', '130ft', '15m', '16x', '18pcs', '1g', '20m', '24ir', "24led's", '24pcs', '27x', '28x', '2x', "3'sony",
								  '36x', '3color', '3g', '3x', '4.2v', '40m', '40mbs', '40meter', '42in', '42v', '4x', '500m', '50m', '5x', '63x', '6x', '7075m',
								  '75m', '7colors', '7fps', '7x', '94mbs', '960h', '960p', 'bullet1', 'bw21', 'bw65', 'cmos1000tvl', 'color1', 'dome1', 'ip66',
								  'ip66rated', 'ip67', 'ir40m', 'mpeg4', 'onvif2.2', 'p2p', 'price1', 'ps3', 'ry5001c', 'ry7075', 'ry70d1', 'sensor720p',
								  'sony+dslr+700+michigan', 'sony1', 'sonydscwx5b', 'ss7162', 'top10']
				elif brand == 'tamron':
					prefixes = ['f']
				elif brand == 'toshiba':
					prefixes = ['pdr']
				elif brand == 'vivitar':
					prefixes = ['v']
					models = ['20', '5118']
					exceptions = ['10x25', '4x']
					equivalences = {'20': 'v20', '5118': 'v5118', 'f124': 'vf124', 'f128': 'vf128', 's130': 'vs130', 't027': 'vt027', 't324n': 'vt324',
									'v5024s': 'v5024', 'vf128pnk': 'vf128', 'vt324n': 'vt324', 'vx014n': 'vx014', 'vx137blk': 'vx137', 'x022': 'vx022',
									'x137': 'vx137', 'x426': 'vx426'}

				# Manage suffixes to make alphanumeric model strings
				if len(suffixes) > 0:
					for i in range(1, len(splitted)):
						if (splitted[i] in suffixes) and (splitted[i - 1].endswith(splitted[i]) == False):
							splitted[i - 1] = splitted[i - 1] + splitted[i]

				# Manage prefixes to make alphanumeric model strings
				if len(prefixes) > 0:
					for i in range(0, len(splitted) - 1):
						if (splitted[i] in prefixes) and (splitted[i + 1].startswith(splitted[i]) == False):
							splitted[i] = splitted[i] + splitted[i + 1]

				# Extract model (no more only among the first 5 words, but in the whole string)
				model = 'none'
				for s in splitted:
					if ((bool(re.match('^(?=.*[0-9])(?=.*[a-z])', s)) == True) and (s not in exceptions)) or (s in models):
						is_measure = False
						for m in measures:
							if s.endswith(m):
								is_measure = True
						if is_measure == False:
							model = s
							break

				if brand == 'canon' and model != 'none':
					if model in ['1d', '1ds', '5d', '6d', '7d', 'eos1d', 'g1x']:
						if ' iv ' in camera['page_title']:
							model = model + ' ' + 'mark4'
						elif ' iii ' in camera['page_title']:
							model = model + ' ' + 'mark3'
						elif ' ii ' in camera['page_title'] or ' markii ' in camera['page_title'] or ' mkii ' in camera['page_title'] \
						or ' mark 2 ' in camera['page_title']:
							if ' ii n ' in camera['page_title']:
								model = model + ' ' + 'mark2n'
							else:
								model = model + ' ' + 'mark2'
						elif ' i ' in camera['page_title']:
							model = model + ' ' + 'mark1'
					mods = {'sl1': '100d', 'x7': '100d', 't1i': '500d', 't1': '500d', 't2i': '550d', 't3': '1100d', 'x50': '1100d', 'ds126291': '1100d',
							't3i': '600d', '3ti': '600d', 'x5': '600d', 'ds126311': '600d', 't4i': '650d', 't5': '1200d', 't5i': '700d', 'x7i': '700d',
							'ds126191': '1000d', 'xs': '1000d', 'ds6041': '300d', 'ds126071': '350d', 'xt': '350d', 'ds126151': '400d', 'xti': '400d',
							'ds126181': '450d', 'xsi': '450d', 'ds126281': '60d', 'ixy120': '135', 'ixy31s': '500', 'ixy610f': '330', 'ixy800': 'sd700',
							'ixy90': 'sd750', 'ixus100': 'sd780', 'ixus1000': 'sd4500', 'ixus105': 'sd1300', 'ixus110': 'sd960', 'ixus1100': '510',
							'ixus115': '100', 'ixus120': 'sd940', 'ixus125': '110',	'ixus130': 'sd1400', 'ixus132': '115', 'ixus135': '120', 'ixus140': '130',
							'ixus145': '135', 'ixus145bk': '135', 'ixus145pr': '135', 'ixus145r': '135', 'ixus150': '140', 'ixus150gy': '140', 'ixus150r': '140',
							'ixus155': '150', 'ixus155bl': '150', 'ixus155r': '150', 'ixus155s': '150', 'ixus200': 'sd980', 'ixus210': 'sd3500', 'ixus220': '300',
							'ixus230': '310', 'ixus240': '320', 'ixus255': '330', 'ixus265': '340', 'ixus30': 'sd200', 'ixus300': 'sd4000', 'ixus310': '500',
							'ixus40': 'sd300', 'ixus400': 's400', 'ixus430': 's410', 'ixus50': 'sd400', 'ixus500': '520', 'ixus510': '530', 'ixus55': 'sd450',
							'ixus60': 'sd600', 'ixus65': 'sd630', 'ixus70': 'sd1000', 'ixus700': 'sd500', 'ixus75': 'sd750', 'ixus750': 'sd550',
							'ixus80': 'sd1100', 'ixus800': 'sd700', 'ixus85': 'sd770', 'ixus850': 'sd800', 'ixus860': 'sd870', 'ixus870': 'sd880',
							'ixus90': 'sd790', 'ixus900': 'sd900', 'ixus95': 'sd1200', 'ixus950': 'sd850', 'ixus960': 'sd950', 'ixus970': 'sd890',
							'ixus980': 'sd990', 'ixus990': 'sd970', 'ixusi5': 'sd20', 'ixusi7': 'sd40'}
					if model.endswith('is'):
						model = model.replace('is', '')
					if model.endswith('hs'):
						model = model.replace('hs', '')
					if model in mods.keys():
						model = mods[model]
					if model.startswith('elph'):
						model = model.replace('elph', '')
					if model.startswith('pro'):
						model = model.replace('pro', '')

				if brand == 'dahua' and model != 'none':
					if model.startswith('ipc'):
						model = model.replace('ipc', 'dhipc')
					elif model.startswith('pc'):
						model = model.replace('pc', 'dhipc')
					elif model.startswith('hdb'):
						model = model.replace('hdb', 'dhipchdb')
					elif model.startswith('hfw'):
						model = model.replace('hfw', 'dhipchfw')
					elif model.startswith('sd'):
						model = model.replace('sd', 'dhsd')

				if brand == 'leica' and model != 'none':
					if model.startswith('lux'):
						if ' d ' in camera['page_title']:
							model = 'd' + model
						elif ' v ' in camera['page_title']:
							model = 'v' + model
						elif ' c ' in camera['page_title']:
							model = 'c' + model
					if model == '240':
						if ' p ' in camera['page_title']:
							model = 'mp240'
						else:
							model = 'm240'

				if brand == 'panasonic' and model != 'none':
					if model.startswith('dmc'):
						model = model.replace('dmc', '')
					if model.endswith('s'):
						model = model.replace('s', '')
					if model.endswith('a'):
						model = model.replace('a', '')
					if model.endswith('r'):
						model = model.replace('r', '')
					if model.endswith('p'):
						model = model.replace('p', '')
					if model.endswith('w'):
						model = model.replace('w', '')
					if model.endswith('d'):
						model = model.replace('d', '')
					if model.endswith('h'):
						model = model.replace('h', '')
					if model.endswith('c'):
						model = model.replace('c', '')
					if model.endswith('kk'):
						model = model.replace('kk', '')
					if model.endswith('k'):
						model = model.replace('k', '')

				if brand == 'ricoh' and model == 'gr':
					if ' iv ' in camera['page_title']:
						model = 'gr digital iv'
					elif ' iii ' in camera['page_title']:
						model = 'gr digital iii'
					elif ' ii ' in camera['page_title']:
						model = 'gr digital ii'
					elif ' digital ' in camera['page_title'] or ' 16mp ' in camera['page_title']:
						model = 'gr digital'

				if brand == 'sony' and model != 'none':
					if model.startswith('dslr'):
						model = model.replace('dslr', '')
					elif model.startswith('hx'):
						model = model.replace('hx', 'dschx')
					elif model.startswith('ilca'):
						model = model.replace('ilca', 'a')
					elif model.startswith('ilcea'):
						model = model.replace('ilcea', 'a')
					elif model.startswith('ilce'):
						model = model.replace('ilce', 'a')
					elif model.startswith('ice'):
						model = model.replace('ice', 'a')
					elif model.startswith('mvc'):
						model = model.replace('mvc', '')
					elif model.startswith('p'):
						model = model.replace('p', 'dscp')
					elif model.startswith('qx'):
						model = model.replace('qx', 'dscqx')
					elif model.startswith('rx'):
						model = model.replace('rx', 'dscrx')
					elif model.startswith('slt'):
						model = model.replace('slt', '')
					elif model.startswith('tx'):
						model = model.replace('tx', 'dsctx')
					elif model.startswith('w'):
						model = model.replace('w', 'dscw')
					mods = {'1200tv': '1200tvl', '300k': 'a300', '350x': 'a350', '420800tvl': '420tvl', '480600tvl': '480tvl', '5n': 'nex5n',
							'600tvllow': '600tvl', '700tv': '700tvl', '7r': 'a7r', '7s': 'a7s', 'a350x': 'a350', 'a37m': 'a37', 'a55vl': 'a55', 'a58m': 'a58',
							'a65vk': 'a65', 'a65vl': 'a65', 'a65vm': 'a65', 'a77m2': 'a77 2', 'a77m2q': 'a77 2', 'a77vm': 'a77', 'cd400kitis' : 'cd400',
							'dsch7megamovie': 'dsch7', 'dschx400vb': 'dschx400', 'dschx50vb': 'dschx50', 'dschx60vb': 'dschx60', 'dscp93a': 'dscp93',
							'dscrx100m': 'dscrx100', 'dsct300r': 'dsct300', 'dscw120p': 'dscw120', 'dscw120digital': 'dscw120', 'dscw150r': 'dscw150',
							'dscw1digital': 'dscw1', 'dscw350d': 'dscw350', 'dscw710p': 'dscw710', 'dscw810s': 'dscw810', 'dscw830s': 'dscw830',
							'dscwx350w': 'dscwx350', 'f707': 'dscf707',	'f828': 'dscf828', 'h10': 'dsch10', 'h20': 'dsch20', 'h200': 'dsch200', 'h400': 'dsch400',
							'h50': 'dsch50', 'h90': 'dsch90', 'hdras100vr': 'hdras100', 'hdrpj240er': 'hdrpj240e', 'hdrpj240es': 'hdrpj240e',
							'hdrpj340ew': 'hdrpj340e', 'nex3kb': 'nex3', 'nex3nbmbdl': 'nex3n', 'nex567': 'nex5', 'nex5c': 'nex5', 'nex5ndslr': 'nex5n',
							'nex5rkb': 'nex5r', 'nex5tls': 'nex5t',	'nex6lb2bdl': 'nex6', 'nex6lb': 'nex6', 's2100': 'dscs2100', 's50': 'dscs50',
							's650': 'dscs650', 's70': 'dscs70', 's85': 'dscs85', 'slta55': 'a55', 'stla99v': 'a99', 't300': 'dsct300', 't90': 'dsct90',
							't99': 'dsct99'}
					if model in mods.keys():
						model = mods[model]
					if model.endswith('b'):
						model = model.replace('b', '')
					elif model.endswith('k'):
						model = model.replace('k', '')
					elif model.endswith('l'):
						model = model.replace('l', '')
					elif model.endswith('v'):
						model = model.replace('v', '')
					elif model.endswith('y'):
						model = model.replace('y', '')
					if model == 'a77':
						if ' ii ' in camera['page_title'] or ' 2 ' in camera['page_title']:
							model = model + ' ' + '2'
					if model.startswith('dscrx100'):
						if ' ii ' in camera['page_title'] or model in ['dscrx1002', 'dscrx100m2']:
							model = 'dscrx100' + ' ' + '2'
						elif ' iii ' in camera['page_title'] or model in ['dscrx100iii', 'dscrx100m3', 'dscrx100m3b', 'dscrx100miii']:
							model = 'dscrx100' + ' ' + '3'

				if model in equivalences.keys():
						model = equivalences[model]

				camera['page_title'] = ' '.join(splitted)

				# Put the current specification in the right group (solved or unsolved)
				if (brand != 'none') and (model != 'none'):
					camera['brand_n_model'] = brand + ' ' + model
					solved_specs.append(camera)
				else:
					unsolved_specs.append(camera)

	mid_time = time.time()
	print(mid_time - start_time)

	print(len(solved_specs))
	print(len(unsolved_specs))

#	solved_specs_df = pd.DataFrame(solved_specs)
#	solved_specs_df.set_index('id')

#	unsolved_specs_df = pd.DataFrame(unsolved_specs)
#	unsolved_specs_df.set_index('id')

#	solved_specs_df = solved_specs_df.sort_values(by=['brand_n_model'])
#	solved_specs_df.to_csv('solved_specs.csv', index=False)
#	unsolved_specs_df.to_csv('unsolved_specs.csv', index=False)

	# Get matches from solved specifications

	clusters = dict()

	for s in solved_specs:
		if s['brand_n_model'] in clusters.keys():
			clusters[s['brand_n_model']].append(s['id'])
		else:
			clusters.update({s['brand_n_model'] : [s['id']]})

	couples = set()
	for c in clusters.keys():
		if len(clusters[c]) > 1:
			for i in clusters[c]:
				for j in clusters[c]:
					if i < j:
						couples.add((i, j))
					if i > j:
						couples.add((j, i))

	couples = list(couples)
	couples = pd.DataFrame(couples, columns = ['left_spec_id', 'right_spec_id'])

	print(couples)

	# Find identical strings in unsolved specifications

	clusters = dict()

	for u in unsolved_specs:
		if u['page_title'] in clusters.keys():
			clusters[u['page_title']].append(u['id'])
		else:
			clusters.update({u['page_title'] : [u['id']]})

	identities = set()
	for c in clusters.keys():
		if len(clusters[c]) > 1:
			for i in clusters[c]:
				for j in clusters[c]:
					if i < j:
						identities.add((i, j))
					if i > j:
						identities.add((j, i))

	identities = list(identities)
	identities = pd.DataFrame(identities, columns = ['left_spec_id', 'right_spec_id'])

	print(identities)

	couples = pd.concat([couples, identities])

	couples.to_csv('matches_from_solved.csv', index=False)

	final_time = time.time()
	print(final_time - mid_time)

if __name__ == "__main__":
    main()
