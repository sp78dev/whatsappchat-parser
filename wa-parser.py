#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os
import sys
import inspect
import json
import argparse
import datetime
import time
import pandas as pd
import numpy as np


def chatParser(text_file):
	
	"""
		Parse the chat in the given text file and give the pandas dataframe

	"""
	
	prev_matched = ""
	same_msg = []; full_msg = []; sender = []; message = []; created_date = [];

	try:

		with open(text_file, encoding="utf-8") as f:
			firstline = f.readline()
			list_data = f.readlines()
			with_ampm_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}) (AM|PM|am|pm)'
			without_ampm_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2})'

			with_ampm = False

			if re.match(with_ampm_regex, firstline):
				with_ampm = True
				chat_regex = re.compile(r'((\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}) (AM|PM|am|pm) - ([\w\s]+): ((.|\n)*))', re.MULTILINE)
				time_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2})'
			
			elif re.match(without_ampm_regex, firstline):
				chat_regex = re.compile(r'((\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}) - ([\w\s]+): ((.|\n)*))', re.MULTILINE)
				time_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2})'

			else:
				print(json.dumps({"message": "Datetime format not matched", 'ok':0}, indent=4))
				sys.exit(1)


			# convert the multline message into single message
			for ind, i in enumerate(list_data):

				if re.match(time_regex, i):
					if same_msg:
						same_msg.insert(0, prev_matched)
						full_msg.append('\n'.join(same_msg))
						same_msg = []
					prev_matched = i
					full_msg.append(i)
				else:
					same_msg.append(i)
					if ind == len(list_data)-1:
						if same_msg:
							same_msg.insert(0, prev_matched)
							full_msg.append('\n'.join(same_msg))
						continue
					if len(same_msg) == 1 and full_msg:
						del full_msg[-1]

			if with_ampm:

				for j in full_msg:
					for m in chat_regex.finditer(j):
						parsed_date = datetime.datetime.strptime(m.group(2)+" "+m.group(3)+" "+m.group(4), "%d/%m/%y %I:%M %p")
						created_date.append(parsed_date)
						sender.append(m.group(5).encode('utf-8').strip())
						message.append(m.group(6).encode('utf-8').strip())
			else:

				for j in full_msg:
					for m in chat_regex.finditer(j):
						parsed_date = datetime.datetime.strptime(m.group(2)+" "+m.group(3), "%m/%d/%y %H:%M")
						created_date.append(parsed_date)
						sender.append(m.group(4).encode('utf-8').strip())
						message.append(m.group(5).encode('utf-8').strip())

		df = pd.DataFrame(zip(sender, message, created_date), columns=['sender', 'message', 'created_at'])
		df['message'], df['sender'] = df['message'].str.decode("utf-8"), df['sender'].str.decode("utf-8")

	except Exception as e:
		print(json.dumps({"message": "Error at line {0} -- {1}".format(sys.exc_info()[-1].tb_lineno, str(e)), 'ok':0}, indent=4))
		sys.exit(1)

	return df


def chatParserWithNumpy(text_file):
	"""
		Parse the chat in the given text file using numpy and give the pandas dataframe

	"""

	prev_matched = ""
	same_msg = []; full_msg = []; sender = []; message = []; created_date = [];

	try:

		array_data = np.loadtxt(text_file, skiprows=0, dtype='str', delimiter='\n', encoding='utf8')
		firstline = array_data[0]

		with_ampm_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}) (AM|PM|am|pm)'
		without_ampm_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2})'

		with_ampm = False

		if re.match(with_ampm_regex, firstline):
			with_ampm = True
			chat_regex = re.compile(r'((\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}) (AM|PM|am|pm) - ([\w\s]+): ((.|\n)*))', re.MULTILINE)
			time_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2})'
		
		elif re.match(without_ampm_regex, firstline):
			chat_regex = re.compile(r'((\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}) - ([\w\s]+): ((.|\n)*))', re.MULTILINE)
			time_regex = r'(\d{1,2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2})'

		else:
			print(json.dumps({"message": "Datetime format not matched", 'ok':0}, indent=4))
			sys.exit(1)

		# convert the multline message into single message
		# for ind, i in enumerate(array_data):

		# 	if re.match(time_regex, i):
		# 		if same_msg:
		# 			same_msg = np.insert(same_msg, 0, prev_matched)
		# 			full_msg = np.append(full_msg, '\n'.join(same_msg))
		# 			same_msg = []
		# 		prev_matched = i
		# 		full_msg=np.append(full_msg, i)
		# 	else:
		# 		same_msg.append(i)
		# 		if ind == len(array_data)- 1:
		# 			if same_msg:
		# 				same_msg.insert(0, prev_matched)
		# 				full_msg = np.append(full_msg, '\n'.join(same_msg))
		# 			continue
		# 		if len(same_msg) == 1 and len(same_msg) > 0:
		# 			full_msg=np.delete(full_msg,-1)

		# if with_ampm:

		# 	for j in full_msg:
		# 		for m in chat_regex.finditer(j):
		# 			parsed_date = datetime.datetime.strptime(m.group(2)+" "+m.group(3)+" "+m.group(4), "%d/%m/%y %I:%M %p")
		# 			created_date = np.append(created_date, parsed_date)
		# 			sender = np.append(sender, m.group(5).encode('utf-8').strip())
		# 			message = np.append(message, m.group(6).encode('utf-8').strip())
		# else:

		# 	for j in full_msg:
		# 		for m in chat_regex.finditer(j):
		# 			parsed_date = datetime.datetime.strptime(m.group(2)+" "+m.group(3), "%m/%d/%y %H:%M")
		# 			created_date = np.append(created_date, parsed_date)
		# 			sender = np.append(sender, m.group(4).encode('utf-8').strip())
		# 			message = np.append(message, m.group(5).encode('utf-8').strip())

		for ind, i in enumerate(array_data):

				if re.match(time_regex, i):
					if same_msg:
						same_msg.insert(0, prev_matched)
						full_msg.append('\n'.join(same_msg))
						same_msg = []
					prev_matched = i
					full_msg.append(i)
				else:
					same_msg.append(i)
					if ind == len(array_data)-1:
						if same_msg:
							same_msg.insert(0, prev_matched)
							full_msg.append('\n'.join(same_msg))
						continue
					if len(same_msg) == 1 and full_msg:
						del full_msg[-1]

		if with_ampm:

			for j in full_msg:
				for m in chat_regex.finditer(j):
					parsed_date = datetime.datetime.strptime(m.group(2)+" "+m.group(3)+" "+m.group(4), "%d/%m/%y %I:%M %p")
					created_date.append(parsed_date)
					sender.append(m.group(5).encode('utf-8').strip())
					message.append(m.group(6).encode('utf-8').strip())
		else:

			for j in full_msg:
				for m in chat_regex.finditer(j):
					parsed_date = datetime.datetime.strptime(m.group(2)+" "+m.group(3), "%m/%d/%y %H:%M")
					created_date.append(parsed_date)
					sender.append(m.group(4).encode('utf-8').strip())
					message.append(m.group(5).encode('utf-8').strip())
		df = pd.DataFrame(zip(sender, message, created_date), columns=['sender', 'message', 'created_at'])
		df['message'], df['sender'] = df['message'].str.decode("utf-8"), df['sender'].str.decode("utf-8")

	except Exception as e:
		print(json.dumps({"message": "Error at line {0} -- {1}".format(sys.exc_info()[-1].tb_lineno, str(e)), 'ok':0}, indent=4))
		sys.exit(1)

	return df

	# return pd.DataFrame()


def parse_args():
	"""
	Get the arguments passed while running the program.
	:return: parsed arguments
	"""

	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument('-p', '--path', type=str, help='Give the exported chat file path',
						action="store", required= False)

	parser.add_argument('-s', "--save", choices=['json', 'csv'], action="store",
						help='Get the result in json or csv file')

	parser.add_argument("-o", "--order", choices=['asc', 'desc'], help="To order the chat by time",
						action="store")

	return parser.parse_args()


if __name__ == '__main__':
	try:
		args = parse_args()

		if sys.version_info[0] == 2:

			print(json.dumps({"message": "Whatappchat-parser only suported for python 3", 'ok': 0 }, indent=4))
			sys.exit(1)

		# DB Initialization process
		if args.path and args.save:
			
			if os.path.isfile(args.path):
				filename, file_extension = os.path.splitext(args.path)

				if file_extension not in ['.txt', '.log']:
					print(json.dumps({"message": "Unsupported file extension", 'ok':0}, indent=4))
					sys.exit(1)

				start = time.time()
				print("start time", start)
				df = chatParser(args.path) #chatParserWithNumpy(args.path)
				end = time.time()
				print("start time", end)
				print("parse time", end - start)

				if args.order == 'desc':
					df = df.iloc[::-1]

				if args.save == 'json':
					output_path = filename + '.json'
					df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
					df.to_json(output_path, orient='records')
					print(json.dumps({"message": "JSON File successfully created", 'ok':1}, indent=4))

				elif args.save == 'csv':
					output_path = filename+ '.csv'
					df.to_csv(output_path, index= False, date_format= "%Y-%m-%d %H:%M:%S")
					print(json.dumps({"message": "CSV File successfully created", 'ok':1}, indent=4))

			else:
				print(json.dumps({"message": "Given file path not exist", 'ok':0}, indent=4))

		else:

			print(json.dumps({"message": "Give the proper arguments", 'ok':0}, indent=4))

	except Exception as e:

		print(json.dumps({"message": "Error at line {0} -- {1}".format(sys.exc_info()[-1].tb_lineno, str(e)), 'ok':0}, indent=4))

	except KeyboardInterrupt:
		print("Byee")
		sys.exit(0)