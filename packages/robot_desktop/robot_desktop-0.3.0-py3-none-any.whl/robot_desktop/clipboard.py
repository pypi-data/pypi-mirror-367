import sys

import pyperclip
from contextlib import contextmanager

from robot_base import log_decorator, func_decorator


@log_decorator
@func_decorator
def set_text_to_clipboard(text_content, content_type='plain', **kwargs):
	if content_type == 'plain':
		pyperclip.copy(text_content)
	else:
		if sys.platform != 'win32':
			raise Exception('非win32平台不支持html类型')
		html_to_clipboard(text_content)


@log_decorator
@func_decorator
def get_text_from_clipboard(content_type='plain', **kwargs):
	if content_type == 'plain':
		return pyperclip.paste()
	elif content_type == 'html':
		if sys.platform != 'win32':
			raise Exception('非win32平台不支持html类型')
		return get_clipboard_html()


@contextmanager
def clipboard_open():
	from ctypes import windll

	if not windll.user32.OpenClipboard(None):
		raise RuntimeError('无法打开剪切板')
	try:
		windll.user32.EmptyClipboard()
		yield
	finally:
		windll.user32.CloseClipboard()


def html_to_clipboard(html: str):
	import ctypes
	from ctypes import windll
	# CF_HTML 格式要求的头部信息
	prefix = (
		'Version:0.9\r\n'
		'StartHTML:00000000\r\n'
		'EndHTML:00000000\r\n'
		'StartFragment:00000000\r\n'
		'EndFragment:00000000\r\n'
		'StartSelection:00000000\r\n'
		'EndSelection:00000000\r\n'
		'SourceURL:file://clipboard.html\r\n'
	)
	full_html = f'{prefix}<html><body>{html}</body></html>'

	# 替换占位符中的偏移量
	start_html = len(prefix)
	end_html = len(full_html)
	start_frag = full_html.find('<body>') + len('<body>')
	end_frag = full_html.rfind('</body>')

	full_html = (
		f'Version:0.9\r\n'
		f'StartHTML:{start_html:08d}\r\n'
		f'EndHTML:{end_html:08d}\r\n'
		f'StartFragment:{start_frag:08d}\r\n'
		f'EndFragment:{end_frag:08d}\r\n'
		f'SourceURL:file://clipboard.html\r\n'
		f'<html><body>{html}</body></html>'
	)

	data = (full_html).encode('utf-16le') + b'\x00\x00'

	with clipboard_open():
		size = len(data)
		h_global = windll.kernel32.GlobalAlloc(0x2, size)
		p_global = windll.kernel32.GlobalLock(h_global)
		ctypes.memmove(p_global, data, size)
		windll.kernel32.GlobalUnlock(h_global)
		windll.user32.SetClipboardData(49153, h_global)  # CF_HTML format id is 49153


def get_clipboard_html() -> str:
	import ctypes
	from ctypes import windll
	with clipboard_open():
		if not windll.user32.IsClipboardFormatAvailable(49153):  # CF_HTML
			return ''
		h_global = windll.user32.GetClipboardData(49153)
		if not h_global:
			return ''
		p_global = windll.kernel32.GlobalLock(h_global)
		data = ctypes.create_string_buffer(h_global).value.decode('utf-16le')
		windll.kernel32.GlobalUnlock(h_global)

		# 提取 Fragment 部分
		start_marker = 'StartFragment:'
		end_marker = 'EndFragment:'
		start_idx = int(data.split(start_marker)[1].split('\r\n')[0])
		end_idx = int(data.split(end_marker)[1].split('\r\n')[0])
		fragment = data[start_idx:end_idx]
		return fragment
