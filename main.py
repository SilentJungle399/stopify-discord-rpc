import rpc
import time
import socketio
import asyncio

sio = socketio.AsyncClient()
rpc_client = rpc.RPC.Set_ID('900755240532471888')

@sio.on('connect')
async def on_connect():
	print('Connected to stopify')

@sio.on('disconnect')
async def on_disconnect():
	print('Disconnected from stopify')

@sio.on('playerState')
async def on_playerState(data):
	global bro

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
	asyncio.run(main())
except KeyboardInterrupt:
	rpc_client.clear_activity()