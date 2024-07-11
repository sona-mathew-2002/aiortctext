
import requests
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio





async def main():
    print("Starting")
    peer_connection = RTCPeerConnection(configuration=config)

    @peer_connection.on("icegatheringstatechange")
    def on_ice_gathering_state_change():
        print(f"ICE gathering state: {peer_connection.iceGatheringState}")
        if peer_connection.iceGatheringState == "complete":
            print("ICE gathering complete")

    @peer_connection.on("icecandidate")
    async def on_icecandidate(event):
        if event.candidate:
            candidate_data = {
                "id": ID,
                "type": "candidate",
                "candidate": event.candidate.candidate,
                "sdpMid": event.candidate.sdpMid,
                "sdpMLineIndex": event.candidate.sdpMLineIndex
            }
            print("posting ice_candidate")
            requests.post(SIGNALING_SERVER_URL + '/candidate', json=candidate_data)

    async def send_pings(channel):
        while True:
            msg = input("Enter message to send: ")
            print("Sending via RTC Datachannel: ", msg)
            channel.send(msg)
            await asyncio.sleep(1)

    @peer_connection.on("datachannel")
    def on_datachannel(channel):
        print(channel, "-", "created by remote party")

        @channel.on("message")
        async def on_message(message):
            print("Received via RTC Datachannel:", message)

        asyncio.ensure_future(send_pings(channel))

    # Get offer
    resp = requests.get(SIGNALING_SERVER_URL + "/get_offer")
    print(resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        if data["type"] == "offer":
            print("Offer received")
            print(data)
            rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await peer_connection.setRemoteDescription(rd)
            await peer_connection.setLocalDescription(await peer_connection.createAnswer())

            message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
            r = requests.post(SIGNALING_SERVER_URL + '/answer', data=message)
            print(message)

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
        await asyncio.sleep(1)

asyncio.run(main())
