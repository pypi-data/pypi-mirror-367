import base64
import fnmatch
import json
import os
import platform
import shutil
import subprocess
import time
import typing
import uuid
from io import BytesIO
from urllib.parse import unquote

try:
	import ddddocr
except:
	pass
import psutil
import websocket as websocket_client
from PIL import Image

from robot_base import ParamException, TemporaryException


class ExtensionBrowser(object):
	def __init__(self):
		self.browser_process = None
		self.websocket_conn = None
		self.executable_path = None

	def open_browser(
		self,
		url,
		executable_path,
		privacy_mode,
		user_data_dir,
		download_path,
		timeout,
		is_headless,
		extension_path,
		extra_args,
		viewport,
	):
		self.executable_path = executable_path
		nativehost_port_path = os.path.join(os.path.expanduser('~'), '.gobot', 'nativehost_port')
		if not os.path.exists(nativehost_port_path):
			params = '--start-maximized'
			if user_data_dir is not None and user_data_dir != '':
				params += f' --user-data-dir={user_data_dir}'
			if extra_args is not None and extra_args != '':
				params += f' {extra_args}'
			if platform.system() == 'Windows':
				import win32con
				from win32comext.shell import shellcon
				from win32comext.shell.shell import ShellExecuteEx

				ShellExecuteEx(
					fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
					hwnd=None,
					lpFile=executable_path,
					nShow=win32con.SW_SHOWMAXIMIZED,
					lpParameters=params,
				)
			else:
				params += ' --disable-gpu'
				self.browser_process = subprocess.Popen(
					[executable_path] + params.split(' '),
					stdout=subprocess.DEVNULL,
					stderr=subprocess.DEVNULL,
				)

			time.sleep(2)
		if not os.path.exists(nativehost_port_path):
			raise Exception('浏览器插件未正确配置')
		self.connect_browser()
		if url:
			self.new_page(url, timeout)

	def new_page(self, url, timeout):
		resp = self.request_to_native_host(
			{
				'name': 'CreateNewTabRequest',
				'parameters': {'url': url},
			}
		)
		if resp['result'] == 0:
			if resp['error']['message'] == 'No current window':
				if platform.system() == 'Windows':
					import win32con
					from win32comext.shell import shellcon
					from win32comext.shell.shell import ShellExecuteEx

					ShellExecuteEx(
						fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
						hwnd=None,
						lpFile=self.executable_path,
						nShow=win32con.SW_SHOWMAXIMIZED,
						lpParameters=url,
					)
				else:
					self.browser_process = subprocess.Popen(
						[self.executable_path, url],
						stdout=subprocess.DEVNULL,
						stderr=subprocess.DEVNULL,
					)
			else:
				raise Exception(resp['error']['message'])

	def goto_url(self, url, timeout):
		resp = self.request_to_native_host(
			{
				'name': 'NavigateRequest',
				'parameters': {'url': url},
			}
		)
		if resp['result'] == 0:
			raise Exception(resp['error']['message'])

	def reload_page(self, timeout):
		resp = self.request_to_native_host(
			{
				'name': 'RefreshPageRequest',
				'parameters': {},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def page_forward(self, timeout):
		resp = self.request_to_native_host(
			{
				'name': 'GoForwardRequest',
				'parameters': {},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def page_go_back(self, timeout):
		resp = self.request_to_native_host(
			{
				'name': 'GoBackwardRequest',
				'parameters': {},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def page_close(self):
		resp = self.request_to_native_host(
			{
				'name': 'CloseTabRequest',
				'parameters': {},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def browser_close(self):
		if self.browser_process:
			try:
				self.browser_process.kill()
			except:
				pass
		file_name = os.path.basename(self.executable_path)
		file_name_without_extension, _ = os.path.splitext(file_name)
		pids = psutil.pids()
		for pid in pids:
			pro = psutil.Process(pid)
			if file_name_without_extension == pro.name() or file_name_without_extension + '.exe' == pro.name():
				pro.kill()

	def page_screenshot(self, timeout, save_path, full_page):
		resp = self.request_to_native_host(
			{
				'name': 'CapturePageImageRequest',
				'parameters': {
					'format': 'png',
					'whole': full_page,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		images = []
		for img in resp['result']:
			img_data = base64.b64decode(img['img'])
			img = Image.open(BytesIO(img_data))
			images.append(img)
		total_height = sum(img.height for img in images)
		max_width = max(img.width for img in images)
		new_img = Image.new('RGB', (max_width, total_height))
		y_offset = 0
		for img in images:
			# 如果图片宽度不一致，居中放置
			if img.width != max_width:
				x_offset = (max_width - img.width) // 2
				new_img.paste(img, (x_offset, y_offset))
			else:
				new_img.paste(img, (0, y_offset))
			y_offset += img.height
		new_img.save(save_path)

	def get_page_info(self, info_type):
		tabs = self.get_all_tabs()
		activate_tab = [tab for tab in tabs['result'] if tab['active']][0]
		if info_type == 'url':
			return activate_tab['url']
		elif info_type == 'title':
			return activate_tab['title']
		elif info_type == 'content':
			resp = self.request_to_native_host(
				{
					'name': 'GetSourceRequest',
					'parameters': {},
				}
			)
			if 'error' in resp and resp['error']:
				raise Exception(resp['error']['message'])
			return unquote(base64.b64decode(resp['result']).decode('utf-8'))

	def switch_page(self, match_target, match_strategy, url, title, index, bring_to_front, **kwargs):
		tabs = self.get_all_tabs()['result']
		if match_target == 'title':
			if match_strategy == 'equals':
				for tab in tabs:
					if tab['title'] == title:
						self.activate_tab(tab['id'])
						return
				raise Exception(f'{title}未找到')
			elif match_strategy == 'contains':
				for tab in tabs:
					if tab['title'].__contains__(title):
						self.activate_tab(tab['id'])
						return
				raise Exception(f'{title}未找到')
			elif match_strategy == 'fnmatch':
				for tab in tabs:
					if fnmatch.fnmatch(tab['title'], title):
						self.activate_tab(tab['id'])
						return
				raise Exception(f'{title}未找到')
		elif match_target == 'url':
			if match_strategy == 'equals':
				for tab in tabs:
					if tab['url'] == url:
						self.activate_tab(tab['id'])
						return
				raise Exception(f'{url}未找到')
			elif match_strategy == 'contains':
				for tab in tabs:
					if tab['url'].__contains__(url):
						self.activate_tab(tab['id'])
						return
				raise Exception(f'{url}未找到')
			elif match_strategy == 'fnmatch':
				for tab in tabs:
					if fnmatch.fnmatch(tab['url'], url):
						self.activate_tab(tab['id'])
						return
				raise Exception(f'{url}未找到')
		elif match_target == 'index':
			index = int(index)
			if index > len(tabs) - 1:
				raise Exception(f'{index}未找到')
			else:
				self.activate_tab(tabs[index]['id'])

	def get_active_tab_id(self):
		tabs = self.get_all_tabs()
		return [tab for tab in tabs['result'] if tab['active']][0]['id']

	def get_all_tabs(self):
		resp = self.request_to_native_host(
			{
				'name': 'GetTabRequest',
				'parameters': {},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		return resp

	def activate_tab(self, tab_id):
		resp = self.request_to_native_host(
			{
				'name': 'ActivateTabRequest',
				'parameters': {
					'tabId': tab_id,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		return resp

	def find_element(self, element_type, element_selector, highlight, **kwargs):
		if element_type == 'pick':
			pick_element = kwargs.get('pick_element', {})
			if pick_element is None or 'xpath' not in pick_element:
				raise ParamException('元素选择器不能为空')
			return ExtensionElement(
				self,
				pick_element.get('name', ''),
				pick_element['xpath'],
				pick_element.get('frameXpath', ''),
			)
		elif element_type == 'locator':
			return ExtensionElement(
				self,
				'',
				element_selector,
				kwargs.get('frame_selector', ''),
			)

	def find_elements(self, element_type, element_selector, highlight, **kwargs):
		elements = []
		frame_selector = ''
		if element_type == 'pick':
			pick_element = kwargs.get('pick_element', {})
			element_selector = pick_element['xpath']
			frame_selector = pick_element.get('frameXpath', '')
		elif element_type == 'locator':
			frame_selector = kwargs.get('frame_selector', '')
		resp = self.request_to_native_host(
			{
				'name': 'GetElementObjectsRequest',
				'parameters': {
					'selector': {
						'name': '',
						'xpath': element_selector,
						'iframeXPath': frame_selector,
					},
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		for element in resp['result']:
			elements.append(
				ExtensionElement(
					self,
					element['tag'],
					element['xpath'],
					element['iframeXPath'],
					element['uid'],
				)
			)
		return elements

	def query_element_count(self, name, xpath, iframe_xpath):
		resp = self.request_to_native_host(
			{
				'name': 'QueryElementCountByXpathRequest',
				'parameters': {
					'selector': {
						'name': name,
						'xpath': xpath,
						'iframeXPath': iframe_xpath,
					}
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		return resp.get('result', {}).get('count', 0)

	def mouse_move(self, x, y, steps, **kwargs):
		resp = self.request_to_native_host(
			{
				'name': 'MouseMoveRequest',
				'parameters': {'x': x, 'y': y, 'options': {'steps': steps}},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def mouse_up_down(self, mouse_type, button, click_count, x=0, y=0, **kwargs):
		resp = self.request_to_native_host(
			{
				'name': 'MousePressedRequest' if mouse_type == 'down' else 'MouseReleasedRequest',
				'parameters': {'x': x, 'y': y, 'button': button, 'clickCount': click_count},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def mouse_click(
		self,
		click_type,
		x,
		y,
		button,
		click_count,
		delay,
		**kwargs,
	):
		if click_type == 'single':
			resp = self.request_to_native_host(
				{
					'name': 'MouseClickRequest',
					'parameters': {
						'x': x,
						'y': y,
						'options': {'clickCount': click_count, 'delay': delay, 'button': button},
					},
				}
			)
			if 'error' in resp and resp['error']:
				raise Exception(resp['error']['message'])
		else:
			resp = self.request_to_native_host(
				{
					'name': 'MouseDbClickRequest',
					'parameters': {
						'x': x,
						'y': y,
						'options': {'clickCount': click_count, 'delay': delay, 'button': button},
					},
				}
			)
			if 'error' in resp and resp['error']:
				raise Exception(resp['error']['message'])

	def mouse_scroll(self, delta_x, delta_y, **kwargs):
		resp = self.request_to_native_host(
			{
				'name': 'MouseWheelRequest',
				'parameters': {
					'deltaX': delta_x,
					'deltaY': delta_y,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def hotkey(self, key, delay, **kwargs):
		resp = self.request_to_native_host(
			{
				'name': 'KeyPressRequest',
				'parameters': {
					'key': key.replace(';', '+'),
					'options': {'delay': delay},
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def keyboard_input(self, content, delay, **kwargs):
		resp = self.request_to_native_host(
			{
				'name': 'InsertTextRequest',
				'parameters': {
					'text': content,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def connect_browser(self):
		nativehost_port_path = os.path.join(os.path.expanduser('~'), '.gobot', 'nativehost_port')
		with open(nativehost_port_path, 'r') as f:
			nativehost_port = f.read()
		try:
			self.websocket_conn = websocket_client.create_connection(f'ws://127.0.0.1:{nativehost_port}/ws')
		except:
			raise Exception('浏览器插件未正确配置,请重新配置浏览器插件')

	def request_to_native_host(self, data):
		request_id = str(uuid.uuid1())
		data['requestId'] = request_id
		if self.websocket_conn is None or not self.websocket_conn.connected:
			raise Exception('web_conn is not connected')
		try:
			self.websocket_conn.send(json.dumps(data))
		except Exception:
			self.connect_browser()
			self.websocket_conn.send(json.dumps(data))
		while True:
			resp = self.websocket_conn.recv()
			resp_data = json.loads(resp)
			if 'requestId' in resp_data and resp_data['requestId'] == request_id:
				return resp_data


class ExtensionElement(object):
	def __init__(self, browser, name, xpath, iframe_xpath, uid=''):
		self.browser = browser
		self.name = name
		self.xpath = xpath
		self.iframe_xpath = iframe_xpath
		self.uid = uid

	def get_xpath(self):
		if self.uid:
			return f'//*[@octopus-uid="{self.uid}"]|({self.xpath})[1]'
		return self.xpath

	def ensure_element(self):
		count = self.browser.query_element_count(
			self.name,
			self.get_xpath(),
			self.iframe_xpath,
		)
		if count == 0:
			raise TemporaryException('未找到元素')

	def click(
		self,
		*,
		modifiers=None,
		position=None,
		x=0,
		y=0,
		delay=0,
		button=None,
		click_count=1,
		force=False,
		timeout=30000,
	):
		if modifiers is None:
			modifiers = []
		timeout = int(timeout)
		if button == 'left':
			button_type = 0
		elif button == 'right':
			button_type = 2
		else:
			button_type = 1
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'ClickElementRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'clickOptions': {
						'mockHuman': False,
						'isDoubleClick': click_count > 1,
						'buttonType': button_type,
						'ctrlKey': modifiers and 'Control' in modifiers,
						'shiftKey': modifiers and 'Shift' in modifiers,
						'altKey': modifiers and 'Alt' in modifiers,
					},
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def hover(self, *, modifiers=None, x=0, y=0, position=None, force=False):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'HoverElementRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def fill(self, content, clear, simulate, delay):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'EnterTextRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'options': {
						'isAppend': not clear,
						'pressEnterAtEnd': False,
						'pressTabAtEnd': True,
						'mockHuman': simulate,
						'containShortcut': False,
						'inputIntervalMs': 5,
					},
					'value': content,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def get_content(self, content_type):
		if content_type == 'text':
			attribute_name = 'text'
		elif content_type == 'html':
			attribute_name = 'sourceCode'
		elif content_type == 'value':
			attribute_name = 'value'
		else:
			raise Exception(f'不支持的类型{content_type}')
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'GetElementAttributeRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'attributeName': attribute_name,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		return unquote(base64.b64decode(resp['result']).decode('utf-8'))

	def capture(self, save_path):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'CaptureElementImageRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'format': 'png',
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		with open(save_path, 'wb') as f:
			f.write(base64.b64decode(resp['result']))

	def get_attribute(self, attribute_name):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'GetElementAttributeRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'attributeName': attribute_name,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		return unquote(base64.b64decode(resp['result']).decode('utf-8'))

	def set_attribute(self, attribute_name, attribute_value):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'SetElementAttributeRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'attributeName': attribute_name,
					'attributeValue': attribute_value,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def remove_attribute(self, attribute_name):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'RemoveElementAttributeRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'attributeName': attribute_name,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def select_option(
		self,
		select_type,
		select_value: typing.Optional[typing.Union[str, typing.List[str], None]],
	):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'GetSelectElementOptionsRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'optionsToGet': 'all',
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		position = 1
		if select_type == 'by_value':
			raise Exception('不支持')
		elif select_type == 'by_label':
			result = resp.get('result', [])
			position = result.index(select_value)
		resp = self.browser.request_to_native_host(
			{
				'name': 'SetSelectElementOptionRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'position': position,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def upload_file(
		self,
		file: typing.Optional[typing.Union[str, typing.List[str], None]],
		timeout=30000,
	):
		self.ensure_element()
		files = [file] if isinstance(file, str) else file
		resp = self.browser.request_to_native_host(
			{
				'name': 'UploadFileRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'files': files,
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def down_file(self, folder, timeout=30000):
		self.ensure_element()
		timeout = int(timeout) / 1000
		resp = self.browser.request_to_native_host(
			{
				'name': 'ClickElementRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'clickOptions': {
						'mockHuman': False,
						'isDoubleClick': False,
						'buttonType': 0,
						'ctrlKey': False,
						'shiftKey': False,
						'altKey': False,
					},
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		start = time.perf_counter()
		download_id = 0
		while True:
			try:
				if download_id == 0:
					resp = self.browser.request_to_native_host(
						{
							'name': 'SearchDownloadItemsRequest',
							'parameters': {
								'limit': 1,
								'orderBy': ['-startTime'],
							},
						}
					)
					if 'error' in resp and resp['error']:
						raise Exception(resp['error']['message'])
					if len(resp['result']) > 0:
						download_id = resp['result'][0]['id']
				else:
					resp = self.browser.request_to_native_host(
						{
							'name': 'SearchDownloadItemsRequest',
							'parameters': {
								'limit': 1,
								'id': download_id,
							},
						}
					)
					if 'error' in resp and resp['error']:
						raise Exception(resp['error']['message'])
					if len(resp['result']) > 0:
						if resp['result'][0]['state'] == 'complete':
							filename = resp['result'][0]['filename']
							file_name = os.path.basename(filename)
							shutil.move(filename, str(os.path.join(folder, file_name)))
							return str(os.path.join(folder, file_name))
			except:
				pass

			remain = start + timeout - time.perf_counter()
			if remain > 0:
				time.sleep(min(remain, 0.5))
			else:
				raise TemporaryException('下载超时')

	def verification_code_identification(self, **kwargs):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'CaptureElementImageRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'format': 'png',
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		ocr = ddddocr.DdddOcr()
		return ocr.classification(base64.b64decode(resp['result']))

	def scroll_into_view_if_needed(self):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'ScrollToElementRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'behavior': 'instant',
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])

	def bounding_box(self, **kwargs):
		self.ensure_element()
		resp = self.browser.request_to_native_host(
			{
				'name': 'GetElementRectRequest',
				'parameters': {
					'selector': {
						'name': self.name,
						'xpath': self.get_xpath(),
						'iframeXPath': self.iframe_xpath,
					},
					'behavior': 'instant',
				},
			}
		)
		if 'error' in resp and resp['error']:
			raise Exception(resp['error']['message'])
		return resp['result']

	def wait_element(self, display, timeout, **kwargs):
		timeout = int(timeout)
		start = time.perf_counter()
		while True:
			try:
				count = self.browser.query_element_count(
					self.name,
					self.get_xpath(),
					self.iframe_xpath,
				)
				if display == 'display' and count > 0:
					return True
				if display != 'display' and (count == 0):
					return False
				remain = start + timeout - time.perf_counter()
				if remain > 0:
					time.sleep(min(remain, 0.5))
				else:
					return count > 0
			except:
				pass
