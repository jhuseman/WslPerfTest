#! /usr/bin/env python

import argparse
import sys
import os
import shutil
import subprocess
import random
import json

import detect_wsl
from Timer import Timer

class WslPerfTest(object):
	def __init__(self, distro=['Ubuntu'], cross_test=True, cross_perf_test=True, output=None, size='32M', output_type='json', performance_tests='largefile,smallfile'):
		self.is_win = detect_wsl.is_running_win()
		self.is_wsl = detect_wsl.is_running_wsl()

		self.distro = distro
		self.cross_test = cross_test
		self.cross_perf_test = cross_perf_test
		self.output = output
		self.size_str = size
		self.output_type = output_type
		self.performance_tests = performance_tests
		if not isinstance(self.distro, list):
			self.distro = self.distro.split(',')
		if not isinstance(self.cross_test, bool):
			self.cross_test = (self.cross_test.lower() in ['true','t','y','yes'])
		if not isinstance(self.cross_perf_test, bool):
			self.cross_perf_test = (self.cross_perf_test.lower() in ['true','t','y','yes'])
		if self.output=='-':
			self.output = None
		self.size = (float(self.size_str[:-1]), {'B':0,'K':10,'M':20,'G':30,'T':40,'P':50,'E':60,'Z':70,'Y':80}[self.size_str[-1].upper()])
		self.size = list(self.size)
		for i in range(20):
			if self.size[0] % 1 >= 0.000001:
				if self.size[1] > 0:
					self.size[0] = self.size[0]*2
					self.size[1] = self.size[1]-1
		self.size = tuple(self.size)
	
	def run_and_output(self):
		'''run the test, and output it to the specified output file'''
		results = self.run()
		if self.output_type.lower() in ['json']:
			result_string = json.dumps(results, indent=4)
		elif self.output_type.lower() in ['csv']:
			result_string = results.to_csv()
		else:
			raise RuntimeError('Unknown output type "{}"!'.format(self.output_type))
		if self.output is None:
			print(result_string)
		else:
			with open(self.output, 'wb') as fp:
				fp.write(result_string.encode('utf-8'))

	def run(self):
		'''run the test, and replicate the test on another system if specified'''
		results = {}
		if self.is_win:
			main_result = 'Windows'
		elif self.is_wsl:
			main_result = 'WSL'
		else:
			main_result = 'Unknown_MAIN'
		results[main_result] = {}
		results[main_result]['native'] = self.run_test(os.path.join(os.curdir,'temp'))
		results[main_result]['cross_perf_test'] = {}
		if self.cross_perf_test:
			for dist in self.get_iterable_of_distros():
				crossdir = self.get_cross_dir(dist,'WslPerfTest_temp_data')
				results[main_result]['cross_perf_test'][dist] = self.run_test(crossdir)
		if self.cross_test:
			for dist in self.get_iterable_of_distros():
				results[dist] = self.run_cross_test(dist)
		if self.output_type.lower() in ['json']:
			return results
		elif self.output_type.lower() in ['csv']:
			return self.convert_to_df(results)
		else:
			raise RuntimeError('Unknown output type "{}"!'.format(self.output_type))

	
	def run_test(self, testdir):
		'''run the test on your own platform, with file accesses in the specified directory'''
		need_dir = not os.path.isdir(testdir)
		if need_dir:
			os.makedirs(testdir)
		fname1 = os.path.join(testdir, 'test1.bin')
		fname2 = os.path.join(testdir, 'test2.bin')
		fname3 = os.path.join(testdir, 'test3.bin')
		folder1 = os.path.join(testdir, 'test_dir1')
		folder2 = os.path.join(testdir, 'test_dir2')
		results = {}
		gen_timer = Timer()
		sys.stderr.write('Generating data...\n')
		with gen_timer:
			dat1 = bytes([a % 256 for a in range(2**self.size[1])])
			dat = bytes([])
			for i in range(int(self.size[0])):
				dat = dat + dat1
		results['generate'] = gen_timer.get_delta()
		if 'largefile' in self.performance_tests.lower():
			write_timer = Timer()
			read_timer = Timer()
			copy_timer = Timer()
			rename_timer = Timer()
			delete_timer = Timer()
			delete2_timer = Timer()
			sys.stderr.write('Writing data to {fn1}...\n'.format(fn1=fname1))
			with write_timer:
				with open(fname1, 'wb') as fp:
					fp.write(dat)
			sys.stderr.write('Reading data from {fn1}...\n'.format(fn1=fname1))
			with read_timer:
				with open(fname1, 'rb') as fp:
					dat2 = fp.read()
			sys.stderr.write('Copying data from {fn1} to {fn2}...\n'.format(fn1=fname1,fn2=fname2))
			with copy_timer:
				shutil.copy(fname1, fname2)
			sys.stderr.write('Renaming {fn2} to {fn3}...\n'.format(fn2=fname2,fn3=fname3))
			with rename_timer:
				os.rename(fname2, fname3)
			sys.stderr.write('Deleting {fn1}...\n'.format(fn1=fname1))
			with delete_timer:
				os.remove(fname1)
			sys.stderr.write('Deleting {fn3}...\n'.format(fn3=fname3))
			with delete2_timer:
				os.remove(fname3)
			results['write'] = write_timer.get_delta()
			results['read'] = read_timer.get_delta()
			results['copy'] = copy_timer.get_delta()
			results['rename'] = rename_timer.get_delta()
			results['delete'] = delete_timer.get_delta()
			results['delete2'] = delete2_timer.get_delta()
		if 'smallfile' in self.performance_tests.lower():
			mkdir_timer = Timer()
			small_write_timer = Timer()
			copy_dir_timer = Timer()
			rm_rec_timer = Timer()
			rm_rec2_timer = Timer()
			sys.stderr.write('Creating directory {dir1}...\n'.format(dir1=folder1))
			if os.path.isdir(folder1):
				shutil.rmtree(folder1)
			with mkdir_timer:
				os.mkdir(folder1)
			small_file_size = 256
			num_small_files = int(len(dat)/small_file_size)
			small_dat = dat[:small_file_size]
			sys.stderr.write('Writing data to {num} small files in {dir1}...\n'.format(num=num_small_files, dir1=folder1))
			with small_write_timer:
				for i in range(num_small_files):
					with open(os.path.join(folder1,'{}.dat'.format(i)), 'wb') as fp:
						fp.write(small_dat)
			sys.stderr.write('Copying folder from {dir1} to {dir2}...\n'.format(dir1=folder1, dir2=folder2))
			if os.path.isdir(folder2):
				try:
					shutil.rmtree(folder2)
				except:
					pass
			with copy_dir_timer:
				try:
					shutil.copytree(folder1, folder2)
				except:
					copy_dir_timer.nullify()
			sys.stderr.write('Deleting {dir1}...\n'.format(dir1=folder1))
			with rm_rec_timer:
				try:
					shutil.rmtree(folder1)
				except:
					rm_rec2_timer.nullify()
			sys.stderr.write('Deleting {dir2}...\n'.format(dir2=folder2))
			with rm_rec2_timer:
				try:
					shutil.rmtree(folder2)
				except:
					rm_rec2_timer.nullify()
			results['mkdir'] = mkdir_timer.get_delta()
			results['small_write'] = small_write_timer.get_delta()
			results['copy_dir'] = copy_dir_timer.get_delta()
			results['rm_rec'] = rm_rec_timer.get_delta()
			results['rm_rec2'] = rm_rec2_timer.get_delta()
		sys.stderr.write('Benchmarks complete!\n')
		if need_dir:
			os.rmdir(testdir)
		return results
	
	def get_cross_dir(self, dist, name):
		if self.is_win:
			return '\\\\wsl$\\{dist}\\tmp\\{name}'.format(dist=dist,name=name)
		elif self.is_wsl:
			return '/mnt/c/{name}'.format(name=name)
		else:
			raise RuntimeError("Cannot run a cross-platform test in an environment that is neither Windows nor WSL!")

	def get_iterable_of_distros(self):
		if self.is_win:
			return self.distro
		elif self.is_wsl:
			return ['Windows']
		else:
			raise RuntimeError("Cannot run a cross-platform test in an environment that is neither Windows nor WSL!")

	def run_cross_test(self, dist):
		'''run the test on the opposing platform'''
		workdir, command = self.gen_exec_command(dist)
		args = self.gen_argslist()
		data = self.run_in_opposing(command+args, workdir, dist)
		self.cleanup_exec_env(workdir)
		return data

	def run_in_opposing(self, com, workdir, dist):
		'''runs the specified command and arguments in the given working directory in the opposing system'''
		if self.is_win:
			run_args = ['wsl', '-d', dist] + com
		elif self.is_wsl:
			run_args = ['cmd.exe', '/C', ' '.join(com)]
		else:
			raise RuntimeError("Cannot run a cross-platform test in an environment that is neither Windows nor WSL!")
		out = subprocess.check_output(run_args,cwd=workdir)
		ret = json.loads(out)
		return ret[list(ret.keys())[0]]
	
	def gen_exec_command(self, dist):
		'''
		returns a list of arguments to run this python file on the other system, along with a suitable working directory
		also generates the working directory in the opposite system and copies the necessary files into that directory
		'''
		if sys.version_info[0] < 3:
			pyexec = 'python'
		else:
			pyexec = 'python3'
		workdir = self.get_cross_dir(dist,'WslPerfTest_temp_inst')
		if not os.path.isdir(workdir):
			os.makedirs(workdir)
		extra_copied_files = ['detect_wsl.py','Timer.py']
		scriptdir = os.path.dirname(__file__)
		scriptfname = os.path.basename(__file__)
		for fn in extra_copied_files + [scriptfname]:
			fp = os.path.join(scriptdir,fn)
			if os.path.isfile(fp):
				shutil.copyfile(fp, os.path.join(workdir,fn))
		return (
			workdir,
			[pyexec, scriptfname],
		)

	def cleanup_exec_env(self, workdir):
		'''cleans up the copied files created for the other system'''
		if os.path.basename(__file__) in os.listdir(workdir):
			shutil.rmtree(workdir)
		else:
			sys.stderr.write("WARNING! The python file seems to have not copied over! Not deleting directory to prevent catastrophic deleting mistakes!\n")

	def convert_to_df(self, results):
		import pandas as pd
		results_flat = {}
		for platform in results:
			results_flat[platform+'/'+platform] = results[platform]['native']
			for cross in results[platform]['cross_perf_test']:
				results_flat[platform+'/'+cross] = results[platform]['cross_perf_test'][cross]
		return pd.DataFrame.from_dict(results_flat, orient='index')

	def gen_argslist(self):
		'''returns a list of arguments that replicates the same test on another system'''
		return [
			'--distro',','.join(self.distro),
			'--cross_test','False',
			'--cross_perf_test',{True:'True',False:'False'}[self.cross_perf_test],
			'--output','-',
			'--size',self.size_str,
			'--output_type','json',
			'--performance_tests',self.performance_tests,
		]

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Test file access performance in Windows Subsystem for Linux (WSL)')
	parser.add_argument('-d', '--distro',            dest='distro',            default=argparse.SUPPRESS, help='Comma-separated list of distros to run the test on. Ignored if run from inside WSL (instead runs test in Windows). Defaults to Ubuntu.')
	parser.add_argument('-c', '--cross_test',        dest='cross_test',        default=argparse.SUPPRESS, help='Indicates whether the test should also be conducted in WSL if run from Windows or conducted in Windows if run from WSL. Any other flag than "true", "yes", "t", or "y" (case insensitive) is interpreted as False. Defaults to True.')
	parser.add_argument('-x', '--cross_perf_test',   dest='cross_perf_test',   default=argparse.SUPPRESS, help='Indicates whether the test should also be conducted in a WSL folder if run from Windows or conducted in a Windows folder if run from WSL. Any other flag than "true", "yes", "t", or "y" (case insensitive) is interpreted as False. Defaults to True.')
	parser.add_argument('-o', '--output',            dest='output',            default=argparse.SUPPRESS, help='Indicates a file that the output results should be saved to.  If omitted, or set to "-", outputs to STDOUT.')
	parser.add_argument('-s', '--size',              dest='size',              default=argparse.SUPPRESS, help='The size of file that should be generated for the test. Should be a string in the format "1G", "128M", or "64K", etc.')
	parser.add_argument('-t', '--output_type',       dest='output_type',       default=argparse.SUPPRESS, help='The type of output that should be created. Should be one of "json" or "csv".')
	parser.add_argument('-p', '--performance_tests', dest='performance_tests', default=argparse.SUPPRESS, help='Comma-separated list of the specific tests to run. For all tests, should be "largefile,smallfile".')
	args = parser.parse_args()
	init_settings = args.__dict__
	WslPerfTest(**init_settings).run_and_output()
