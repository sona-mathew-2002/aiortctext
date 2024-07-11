import requests
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio



async def main():
    print("Starting")
    peer_connection = RTCPeerConnection(configuration=config)
    print("New peer connection created")
    channel = peer_connection.createDataChannel("chat")
    print("New channel chat created")

    @peer_connection.on("icegatheringstatechange")
    def on_ice_gathering_state_change():
        print(f"ICE gathering state: {peer_connection.iceGatheringState}")
        if peer_connection.iceGatheringState == "complete":
            print("ICE gathering complete")
            
    
    @peer_connection.on("icecandidate")
    async def on_icecandidate(event):
        print("on-icecandidate")
        if event.candidate:
            candidate_data = {
                "id": ID,
                "type": "candidate",
                "candidate": event.candidate.candidate,
                "sdpMid": event.candidate.sdpMid,
                "sdpMLineIndex": event.candidate.sdpMLineIndex
            }
            print("Sending ICE candidate:", candidate_data)
            try:
                response = requests.post(SIGNALING_SERVER_URL + '/candidate', json=candidate_data)
                response.raise_for_status()  # Raise an exception for bad status codes
                print("ICE candidate sent successfully.")
            except requests.exceptions.RequestException as e:
                print(f"Error sending ICE candidate: {e}")


    async def send_pings(channel):
        while True:
            msg = input("Enter message to send: ")
            print("Sending via RTC Datachannel: ", msg)
            channel.send(msg)
            await asyncio.sleep(1)

    @channel.on("open")
    def on_open():
        print("Channel opened")
        channel.send("Hello from Offerer via Datachannel")
        asyncio.ensure_future(send_pings(channel))
    

    @channel.on("message")
    def on_message(message):
        print("Received via RTC Datachannel:", message)

    # Send offer
    await peer_connection.setLocalDescription(await peer_connection.createOffer())
    message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
    r = requests.post(SIGNALING_SERVER_URL + '/offer', data=message)
    print(r.status_code)

    # Poll for answer
    while True:
        resp = requests.get(SIGNALING_SERVER_URL + "/get_answer")
        if resp.status_code == 503:
            print("Answer not ready, trying again")
            await asyncio.sleep(1)
        elif resp.status_code == 200:
            data = resp.json()
            if data["type"] == "answer":
                print("Answer received")
                rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await peer_connection.setRemoteDescription(rd)
                print("rtcremotedesc")
                print(peer_connection.remoteDescription)
                break
        print(resp.status_code)

    # Poll for candidates
    while True:
        resp = requests.get(SIGNALING_SERVER_URL + "/get_candidates")
        if resp.status_code == 200:
            candidates = resp.json()
            for candidate in candidates:
                ice_candidate = RTCIceCandidate(
                    sdpMid=candidate["sdpMid"],
                    sdpMLineIndex=candidate["sdpMLineIndex"],
                    candidate=candidate["candidate"]
                )
                await peer_connection.addIceCandidate(ice_candidate)
                print("ice candidate added")
        await asyncio.sleep(1)

asyncio.run(main())
