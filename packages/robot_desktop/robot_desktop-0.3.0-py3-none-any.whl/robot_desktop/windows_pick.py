# 设置日志
import base64
import json
import logging
import os
import struct
import sys
import time
import uuid
from io import BytesIO

import psutil
import uiautomation
import xpath
from PIL import ImageGrab
from pynput import mouse, keyboard
from pyrect import Rect

from robot_base import RectangleWindow, TipWindow
from robot_desktop.find_by_xpath import ControlNode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# 移除默认的控制台处理器（如果有）
for handler in logger.handlers[:]:
	if isinstance(handler, logging.StreamHandler):
		logger.removeHandler(handler)


def write_message(message):
	data = message.encode('utf-8')
	length = len(data)
	# 创建一个 2 字节的缓冲区，并以小端字节序存储消息长度
	buf = struct.pack('<I', length)
	# 将消息长度写入标准输出
	sys.stdout.buffer.write(buf)
	sys.stdout.buffer.flush()  # 确保数据被写入
	# 将消息本身写入标准输出
	sys.stdout.buffer.write(data)
	sys.stdout.buffer.flush()  # 确保数据被写入


class PickerServer:
	def __init__(self):
		self.rectangle_window = RectangleWindow(100, 100, 300, 400, text='', color='red')
		self.last_rect: Rect = Rect(0, 0, 0, 0)
		self.last_x = 0
		self.last_y = 0
		self.inspect = False
		self.cancel = False
		self.tip_window = TipWindow(
			text="""按下 Esc 退出拾取\n按下Ctrl+鼠标左键 \n or \n Ctrl+Shit 拾取元素""",
			width=300,
			height=100,
		)
		self.ctrl_press = False
		self.tip_window.hide()
		self.mouse_listener = None
		self.keyboard_listener = None
		self.control_cache = {}

	def start(self):
		write_message('pick server started')
		while True:
			req = None
			try:
				# 从标准输入读取 4 字节
				buf = sys.stdin.buffer.read(4)
				if len(buf) != 4:
					raise ValueError('Failed to read 4 bytes for length')
				# 解析为小端字节序的 uint32
				data_length = struct.unpack('<I', buf)[0]
				# 根据解析的长度读取数据
				data = sys.stdin.buffer.read(data_length)
				if len(data) != data_length:
					raise ValueError('Failed to read the specified number of bytes')
				req = json.loads(data.decode('utf-8'))
				# 打印接收到的数据
				logger.info(f'receive from control: {req}')
				if 'method' not in req:
					raise Exception('No method in client message')
				method = getattr(self, req['method'])
				if method:
					result = method(**req['data'])
					if result is not None:
						message = json.dumps(
							{
								'message_id': req['message_id'],
								'result': 'ok',
								'data': result,
							}
						)
						write_message(message)
				else:
					raise Exception(f'{req["method"]}方法未定义')
			except Exception as e:
				logger.error(f'Error occurred: {e}')
				if req:
					message = json.dumps(
						{
							'message_id': req['message_id'],
							'result': 'error',
							'reason': str(e),
						}
					)
					write_message(message)

	def cache_dump_control(self, index: int, control: uiautomation.Control):
		control_id = uuid.uuid4().hex
		self.control_cache[control_id] = control
		return {
			'id': control_id,
			'automationId': control.AutomationId,
			'name': control.Name,
			'localizeControlType': control.LocalizedControlType,
			'controlTypeName': control.ControlTypeName,
			'className': control.ClassName,
			'frameworkId': control.FrameworkId,
			'index': index,
		}

	@staticmethod
	def get_control_index(control: uiautomation.Control) -> int:
		sibling = control.GetPreviousSiblingControl()
		index = 1
		while sibling is not None:
			if sibling.ControlTypeName == control.ControlTypeName:
				index += 1
			sibling = sibling.GetPreviousSiblingControl()
		return index

	def get_windows_control_info(self, control):
		control_path = []
		control_id = uuid.uuid4().hex
		pic = ImageGrab.grab(
			(
				control.BoundingRectangle.left + 1,
				control.BoundingRectangle.top + 1,
				control.BoundingRectangle.left + control.BoundingRectangle.width() - 1,
				control.BoundingRectangle.top + control.BoundingRectangle.height() - 1,
			)
		)
		display_name = get_control_display_name(control.Name, control.LocalizedControlType)
		image_data = BytesIO()
		pic.save(image_data, format='PNG')
		image_data_bytes = image_data.getvalue()
		encoded_image = base64.b64encode(image_data_bytes).decode('utf-8')
		desktop = uiautomation.GetRootControl()
		process = psutil.Process(control.ProcessId)
		while control and not uiautomation.ControlsAreSame(control, desktop):
			control_path.append(self.generate_windows_control_info(control))
			control = control.GetParentControl()
		control_path.reverse()
		return {
			'id': control_id,
			'type': 'windows',
			'processName': get_display_name(process.name()),
			'name': display_name,
			'image': encoded_image,
			'nodes': control_path,
		}

	def generate_windows_control_info(self, control):
		index = self.get_control_index(control)
		attributes = [
			{
				'name': 'automationId',
				'value': control.AutomationId,
				'isEnable': False,
				'op': 'EqualTo',
			},
			{
				'name': 'className',
				'value': control.ClassName,
				'isEnable': False,
				'op': 'EqualTo',
			},
			{
				'name': 'name',
				'value': control.Name,
				'isEnable': len(control.Name) > 0,
				'op': 'EqualTo',
			},
			{
				'name': 'index',
				'value': index,
				'isEnable': len(control.Name) == 0,
				'op': 'EqualTo',
			},
		]
		return {
			'displayName': get_control_display_name(control.Name, control.LocalizedControlType),
			'name': control.ControlTypeName,
			'isEnable': True,
			'attributes': attributes,
		}

	def get_root(self) -> list:
		self.control_cache.clear()

		desktop = uiautomation.GetRootControl()
		dump_children = []
		children = desktop.GetChildren()
		for index, control in enumerate(children, 1):
			dump_control = self.cache_dump_control(index, control)
			dump_children.append(dump_control)
		return dump_children

	def get_children(self, control_id: str) -> list:
		if control_id in self.control_cache:
			current = self.control_cache[control_id]
			dump_children = []
			children = current.GetChildren()
			for index, control in enumerate(children, 0):
				dump_control = self.cache_dump_control(index, control)
				dump_children.append(dump_control)
			return dump_children
		else:
			return []

	def highlight_current_control(self, control_id: str):
		if control_id in self.control_cache:
			current = self.control_cache[control_id]
			self.rectangle_window.update_position(
				current.BoundingRectangle.left,
				current.BoundingRectangle.top,
				current.BoundingRectangle.width(),
				current.BoundingRectangle.height(),
				text=current.LocalizedControlType,
			)
			self.rectangle_window.highlight()

	def highlight_control(self):
		self.tip_window.show()
		self.start_mouse_keyboard_listener()
		self.inspect = True
		self.cancel = False
		while self.inspect:
			try:
				x, y = uiautomation.GetCursorPos()
				if abs(x - self.last_x) < 2 and abs(y - self.last_y) < 2:
					continue
				self.last_x = x
				self.last_y = y
				control = find_control_from_point(x, y, uiautomation.ControlFromCursor().GetTopLevelControl())
				if control.ProcessId == os.getpid():
					continue
				if control is None:
					self.rectangle_window.hide_all()
					continue
				self.show_highlight_rect(
					Rect(
						control.BoundingRectangle.left,
						control.BoundingRectangle.top,
						control.BoundingRectangle.width(),
						control.BoundingRectangle.height(),
					),
					control.LocalizedControlType,
				)

			except Exception as error:
				logger.exception(error)
			finally:
				time.sleep(0.2)
		if self.cancel:
			raise Exception('cancel')
		else:
			control = find_control_from_point(
				self.last_x,
				self.last_y,
				uiautomation.ControlFromCursor().GetTopLevelControl(),
			)
			return self.get_windows_control_info(control)

	def show_highlight_rect(self, rect, text):
		if self.last_rect == rect:
			return
		else:
			self.last_rect = rect
			self.rectangle_window.update_position(
				rect.left,
				rect.top,
				rect.width,
				rect.height,
				text=text,
			)

	def start_mouse_keyboard_listener(self):
		self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
		self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
		self.mouse_listener.start()
		self.keyboard_listener.start()

	def on_mouse_click(self, x, y, button, pressed):
		if pressed and button == mouse.Button.left and self.ctrl_press:
			self.last_x = x
			self.last_y = y
			self.tip_window.hide()
			self.rectangle_window.hide_all()
			self.mouse_listener.stop()
			self.keyboard_listener.stop()
			self.ctrl_press = False
			self.inspect = False
			self.cancel = False

	def on_key_press(self, key):
		if key == keyboard.Key.esc:
			self.tip_window.hide()
			self.rectangle_window.hide_all()
			self.mouse_listener.stop()
			self.keyboard_listener.stop()
			self.inspect = False
			self.cancel = True
		elif self.ctrl_press and (
			key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r
		):
			self.tip_window.hide()
			self.rectangle_window.hide_all()
			self.mouse_listener.stop()
			self.keyboard_listener.stop()
			self.ctrl_press = False
			self.inspect = False
			self.cancel = False
		elif key == keyboard.Key.f1:
			self.pick_mode = 'web'
		elif key == keyboard.Key.f2:
			self.pick_mode = 'windows'
		elif key == keyboard.Key.f3:
			self.pick_mode = 'java'
		elif key == keyboard.Key.f4:
			self.pick_mode = 'auto'
		elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
			self.ctrl_press = True

	def on_key_release(self, key):
		if key == keyboard.Key.ctrl:
			self.ctrl_press = False

	def check_control(self, element_info):
		element_info = json.loads(element_info)
		if element_info['type'] == 'windows':
			element_xpath = element_info.get('xpath', '')
			root = ControlNode(uiautomation.GetRootControl())
			controls = xpath.find(element_xpath, root)
			if len(controls) == 0:
				raise Exception('元素未找到')
			else:
				for i in range(min(len(controls), 3)):
					control = controls[i].current_control
					self.rectangle_window.update_position(
						control.BoundingRectangle.left,
						control.BoundingRectangle.top,
						control.BoundingRectangle.width(),
						control.BoundingRectangle.height(),
						text=control.LocalizedControlType,
					)
					self.rectangle_window.highlight()
				return len(controls)

	def get_select_control(self, control_id: str):
		if control_id in self.control_cache:
			control: uiautomation.Control = self.control_cache[control_id]
			return self.get_windows_control_info(control)
		else:
			raise Exception('元素未找到')


def find_control_from_point(x, y, control=None):
	if len(control.GetChildren()) == 0:
		return control
	controls = [
		node for node in control.GetChildren() if node.BoundingRectangle and node.BoundingRectangle.contains(x, y)
	]
	if len(controls) == 0:
		return control
	results = []
	for control in controls:
		result = find_control_from_point(x, y, control)
		if result:
			results.append(result)
	if len(results) > 0:
		sorted_results = sorted(
			results,
			key=lambda node: node.BoundingRectangle.width() * node.BoundingRectangle.height(),
		)
		return sorted_results[0]
	return None


def get_control_display_name(text, tag):
	if len(text) == 0:
		return tag
	elif len(text) > 30:
		return text[:30] + '...[' + tag + ']'
	else:
		return text + '[' + tag + ']'


def get_display_name(text):
	if len(text) <= 30:
		return text
	return text[:30] + '...'


if __name__ == '__main__':
	if len(sys.argv) > 1:
		file_handler = logging.FileHandler(sys.argv[1])
		file_handler.setLevel(logging.INFO)  # 设置文件处理器的日志级别

		# 创建日志格式
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		file_handler.setFormatter(formatter)

		# 将文件处理器添加到 root logger
		logger.addHandler(file_handler)
	PickerServer().start()
