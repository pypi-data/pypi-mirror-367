# starclient

Next gen VLA infer client, based on communicate with a Starfoce-Server,
Any device can calling VLA result via websocket connecting with server. It doesn't requires any inference enviorment or compute, you can control robot, on a CPU, by calling a same local network 4090.

starclient usage could be simple:

```
# pip install starclient


from starclient import WebsocketPolicyClient


client = WebsocketPolicyClient(url='127.0.0.1', port=8080, api_key=None)
res = client.infer(obs)

# res is numpy array

```

The requested image and state should all using numpy array as a dict. The key format is:

```
observation.image.cam_high
observation.image.cam_left_wrist
observation.image.cam_right_wrist

observation.state
action

```


