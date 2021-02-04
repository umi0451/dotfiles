import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
try:
	import unittest.mock as mock
except ImportError: # pragma: no cover
	import mock
mock.patch.TEST_PREFIX = 'should'

import os, subprocess, logging
from clckwrkbdgr.jobsequence import JobSequence
import pathlib
from pathlib import Path

def mock_iterdir(data):
	data = {Path(key):list(map(Path, values)) for key,values in data.items()}
	def _actual(self):
		result = data.get(self)
		assert result is not None, "Unexpected path in iterdir: {0}".format(self)
		return result
	return _actual

class TestJobSequence(unittest.TestCase):
	def should_generate_verbose_option(self):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		result = seq.verbose_option()
		click.option.assert_called_once_with('-v', '--verbose', count=True, help='Verbosity level.Passed to jobs via $MY_VERBOSE_VAR.Has cumulative value, each flag adds one level to verbosity and one character to environment variable: MY_VERBOSE_VAR=vvv.')
	def should_generate_job_dir_option(self):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		result = seq.job_dir_option()
		click.option.assert_called_once_with('-d', '--dir', 'job_dirs', multiple=True, default=['my_default_dir'], show_default=True, help="Custom directory with job files. Can be specified several times, job files from all directories are sorted and executed in total order.")
	def should_generate_dry_run_option(self):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		result = seq.dry_run_option()
		click.option.assert_called_once_with('--dry', 'dry_run', is_flag=True, help="Dry run. Only report about actions, do not actually execute them. Implies at least one level in verbosity.")
	def should_generate_patterns_argument(self):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		result = seq.patterns_argument()
		click.argument.assert_called_once_with('patterns', nargs=-1)
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call')
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({'my_default_dir':[]}))
	def should_run_job_sequence(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		seq.run(None, None, verbose=0)
		self.assertEqual(os.environ['MY_VERBOSE_VAR'], '')
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_not_called()
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[0, 0, 0, 0])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_default_dir') : [
			Path('my_default_dir')/'foo.2',
			Path('my_default_dir')/'bar',
			],
		Path('my_other_dir') : [
			Path('my_other_dir')/'foo.1',
			Path('my_other_dir')/'baz',
			],
		}))
	def should_run_several_job_dirs(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', ['my_default_dir', 'my_other_dir'], click=click)
		seq.run(None, None, verbose=0)
		self.assertEqual(os.environ['MY_VERBOSE_VAR'], '')
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_has_calls([
				mock.call([os.path.join('my_default_dir', 'bar')], shell=True),
				mock.call([os.path.join('my_other_dir', 'baz')], shell=True),
				mock.call([os.path.join('my_other_dir', 'foo.1')], shell=True),
				mock.call([os.path.join('my_default_dir', 'foo.2')], shell=True),
				])
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[0, 0])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_default_dir') : [
			Path('my_default_dir')/'foo',
			Path('my_default_dir')/'bar',
			],
		}))
	def should_run_verbose(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		seq.run(None, None, verbose=2)
		self.assertEqual(os.environ['MY_VERBOSE_VAR'], 'vv')
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_has_calls([
				mock.call([os.path.join('my_default_dir', 'bar')], shell=True),
				mock.call([os.path.join('my_default_dir', 'foo')], shell=True),
				])
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[0, 0])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_default_dir') : [
			Path('my_default_dir')/'foo',
			Path('my_default_dir')/'bar',
			],
		}))
	def should_perform_dry_run(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		seq.run(None, None, verbose=2, dry_run=True)
		self.assertIsNone(os.environ.get('MY_VERBOSE_VAR'))
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_has_calls([])
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[0, 0])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_other_dir') : [
			Path('my_other_dir')/'foo',
			Path('my_other_dir')/'bar',
			],
		}))
	def should_run_on_specified_log_dir(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		seq.run(None, 'my_other_dir', verbose=2)
		self.assertEqual(os.environ['MY_VERBOSE_VAR'], 'vv')
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_has_calls([
				mock.call([os.path.join('my_other_dir', 'bar')], shell=True),
				mock.call([os.path.join('my_other_dir', 'foo')], shell=True),
				])
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[1, 2])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_other_dir') : [
			Path('my_other_dir')/'foo',
			Path('my_other_dir')/'bar',
			],
		}))
	def should_collect_return_codes(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		rc = seq.run(None, 'my_other_dir', verbose=2)
		self.assertEqual(rc, 3)
		self.assertEqual(os.environ['MY_VERBOSE_VAR'], 'vv')
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_has_calls([
				mock.call([os.path.join('my_other_dir', 'bar')], shell=True),
				mock.call([os.path.join('my_other_dir', 'foo')], shell=True),
				])
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[0, 0])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_other_dir') : [
			Path('my_other_dir')/'foo',
			Path('my_other_dir')/'bar',
			Path('my_other_dir')/'baz',
			],
		}))
	def should_match_patterns(self, path_iterdir, subprocess_call, logging_info):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)
		seq.run(['ba'], 'my_other_dir', verbose=2)
		self.assertEqual(os.environ['MY_VERBOSE_VAR'], 'vv')
		path_iterdir.assert_has_calls([])
		subprocess_call.assert_has_calls([
				mock.call([os.path.join('my_other_dir', 'bar')], shell=True),
				mock.call([os.path.join('my_other_dir', 'baz')], shell=True),
				])
	@mock.patch.dict(os.environ, os.environ.copy())
	@mock.patch('sys.exit')
	@mock.patch('logging.info')
	@mock.patch('subprocess.call', side_effect=[0, 0])
	@mock.patch.object(pathlib.Path, 'iterdir', autospec=True, side_effect=mock_iterdir({
		Path('my_default_dir') : [
			Path('my_default_dir')/'foo',
			Path('my_default_dir')/'bar',
			Path('my_default_dir')/'baz',
			],
		}))
	def should_run_cli(self, path_iterdir, subprocess_call, logging_info, sys_exit):
		click = mock.MagicMock()
		seq = JobSequence('MY_VERBOSE_VAR', 'my_default_dir', click=click)

		seq.run = mock.MagicMock(return_value=1)
		click.command = mock.MagicMock(side_effect=lambda *args, **kwargs: (lambda x:x))
		seq.verbose_option = mock.MagicMock(side_effect=lambda *args, **kwargs: (lambda x:x))
		seq.dry_run_option = mock.MagicMock(side_effect=lambda *args, **kwargs: (lambda x:x))
		seq.job_dir_option = mock.MagicMock(side_effect=lambda *args, **kwargs: (lambda x:x))
		seq.patterns_argument = mock.MagicMock(side_effect=lambda *args, **kwargs: (lambda x:x))

		seq.cli(['patterns'], None)

		seq.verbose_option.assert_called_with()
		seq.dry_run_option.assert_called_with()
		seq.job_dir_option.assert_called_with()
		seq.patterns_argument.assert_called_with()
		seq.run.assert_called_once_with(['patterns'], None, verbose=0, dry_run=False)
		sys_exit.assert_called_once_with(1)
