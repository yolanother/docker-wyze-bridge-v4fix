# Wyze Cam v4 WebRTC Endpoints - Quick Reference

## 🎯 Your Specific v4 Cameras

Based on your setup, here are the direct endpoints for your three v4 cameras:

### Camera: **View** (HL_CAM4)
- **WebRTC Player**: `http://localhost:5001/webrtc/view`
- **Signaling**: `http://localhost:5001/signaling/view?kvs`
- **Status**: Available via WebRTC (shows "connecting" in UI but works via WebRTC)

### Camera: **Marina South** (HL_CAM4) 
- **WebRTC Player**: `http://localhost:5001/webrtc/marina-south`
- **Signaling**: `http://localhost:5001/signaling/marina-south?kvs`
- **Status**: Available via WebRTC

### Camera: **Marina North** (HL_CAM4)
- **WebRTC Player**: `http://localhost:5001/webrtc/marina-north` 
- **Signaling**: `http://localhost:5001/signaling/marina-north?kvs`
- **Status**: Available via WebRTC

## 🔄 Working Cameras (RTSP)

Your other cameras continue to work via standard RTSP:

- **Palms** (WYZECP1_JEF): `rtsp://localhost:8555/palms`
- **Studio** (HL_CAM3P): `rtsp://localhost:8555/studio`
- **Other cameras**: `rtsp://localhost:8555/<camera-name>`

## 📋 For VistterStudio Integration

```javascript
// Camera detection logic
const v4Cameras = ['view', 'marina-south', 'marina-north'];
const rtspCameras = ['palms', 'studio', 'living-room-cam', 'bedroom'];

function getStreamEndpoint(cameraName) {
    if (v4Cameras.includes(cameraName)) {
        return {
            type: 'webrtc',
            player: `http://localhost:5001/webrtc/${cameraName}`,
            signaling: `http://localhost:5001/signaling/${cameraName}?kvs`
        };
    } else {
        return {
            type: 'rtsp',
            stream: `rtsp://localhost:8555/${cameraName}`
        };
    }
}
```

## ✅ Verification

Test the endpoints:
- Visit `http://localhost:5001/webrtc/view` to see v4 camera WebRTC player
- Check `http://localhost:5001/signaling/view?kvs` for WebRTC signaling data
- Confirm RTSP: `rtsp://localhost:8555/palms` for working camera

## 🌐 Network Requirements

- **Local network**: RTSP cameras work locally
- **Internet required**: v4 cameras need internet for AWS KVS WebRTC
- **Ports**: 5001 (web), 8555 (RTSP), 8890 (WebRTC)
