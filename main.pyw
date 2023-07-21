import asyncio
import time
import sys

import socketio
import pystray
import PIL.Image

import rpc

sio = socketio.AsyncClient()
rpc_client = rpc.RPC.Set_ID('900755240532471888')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def on_quit(icon, item):
	icon.stop()
	rpc_client.clear_activity()
	await sio.disconnect()
	sys.exit(0)

icon = pystray.Icon('Stopify', PIL.Image.open('stopify.jpg'), 'Stopify', menu=pystray.Menu(
	pystray.MenuItem('Quit', lambda icon, item: asyncio.run_coroutine_threadsafe(on_quit(icon, item), loop))
))

icon.run_detached()

@sio.on('connect')
async def on_connect():
	print('Connected to stopify')

@sio.on('disconnect')
async def on_disconnect():
	print('Disconnected from stopify')

@sio.on('playerState')
async def on_playerState(data):
	if 'knownUsers' not in data:
		return

	conn_users = list(map(lambda x: str(x['id']), data['knownUsers']))
	if data['playing'] and str(rpc_client.user['id']) in conn_users:
		rpc_client.set_activity(
			details = data['song']['title'] + ' - ' + data['song']['artist'],
			large_image = data['song']['thumbnail'],
			large_text = data['song']['title'],
			timestamp = int(time.time()) - data['currentTime'],
			buttons = [
				{
					'label': 'Listen along',
					'url': 'https://stopify.silentjungle.me'
				}
			]
		)
	else:
		rpc_client.clear_activity()

async def main():
	await sio.connect('https://stopify.silentjungle.me')
	await sio.wait()

try:
	loop.run_until_complete(main())
except KeyboardInterrupt:
	rpc_client.clear_activity()