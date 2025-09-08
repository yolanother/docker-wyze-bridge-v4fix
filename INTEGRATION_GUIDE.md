# WyzeBridge Integration Guide for VistterStudio
## Handling Wyze Cam v4 WebRTC Streaming After February 2025 Firmware Update

### 📋 Overview

This guide explains how to integrate with WyzeBridge after the February 2025 Wyze firmware update that broke TUTK/RTSP streaming for Wyze Cam v4 (HL_CAM4) cameras. The solution involves using **dual streaming protocols**:

- **Legacy cameras** (v1, v2, v3, Pan, etc.): Continue using RTSP streams
- **v4 cameras** (HL_CAM4): Use WebRTC/KVS cloud streaming

### 🔧 Camera Detection & Protocol Selection

#### 1. Detect Camera Models
Query the WyzeBridge API to identify camera models:

```bash
GET http://localhost:5001/api/sse_status
```

**Response Example:**
```json
{
  "palms": {"status": "connected", "motion": false},           // WYZECP1_JEF - Use RTSP
  "view": {"status": "connecting", "motion": false},           // HL_CAM4 - Use WebRTC  
  "marina-south": {"status": "connecting", "motion": false},   // HL_CAM4 - Use WebRTC
  "studio": {"status": "connected", "motion": false}          // HL_CAM3P - Use RTSP
}
```

#### 2. Get Detailed Camera Information
```bash
GET http://localhost:5001/api/<camera_name>
```

**Response includes:**
```json
{
  "product_model": "HL_CAM4",  // This identifies v4 cameras
  "nickname": "View",
  "status": "connecting",
  // ... other camera details
}
```

### 🎯 Streaming Protocol Logic

```javascript
// Pseudo-code for VistterStudio integration
function getStreamingEndpoint(cameraName, cameraInfo) {
    if (cameraInfo.product_model === "HL_CAM4") {
        // v4 cameras: Use WebRTC
        return {
            protocol: "webrtc",
            endpoint: `http://localhost:5001/webrtc/${cameraName}`,
            signaling: `http://localhost:5001/signaling/${cameraName}?kvs`,
            type: "cloud_streaming"
        };
    } else {
        // Legacy cameras: Use RTSP
        return {
            protocol: "rtsp", 
            endpoint: `rtsp://localhost:8555/${cameraName}`,
            type: "local_streaming"
        };
    }
}
```

### 📡 WebRTC Integration for v4 Cameras

#### WebRTC Signaling Endpoint
```bash
GET http://localhost:5001/signaling/<camera_name>?kvs
```

**Response:**
```json
{
  "cam": "view",
  "result": "ok", 
  "ClientId": "092d7dcd-32bb-4f4d-810b-ca02bd5b9ca8",
  "servers": [
    {
      "credential": "AWS_CREDENTIAL_HERE",
      "urls": "turn:35-160-232-207.t-0b38280f.kinesisvideo.us-west-2.amazonaws.com:443?transport=udp",
      "username": "AWS_USERNAME_HERE"
    }
    // ... more TURN/STUN servers
  ],
  "signalingUrl": "wss://v-33f3a210.kinesisvideo.us-west-2.amazonaws.com/?X-Amz-Algorithm=..."
}
```

#### WebRTC Player Integration
For v4 cameras, VistterStudio should:

1. **Fetch WebRTC signaling data** from `/signaling/<camera_name>?kvs`
2. **Establish WebRTC connection** using the provided AWS KVS credentials
3. **Handle WebRTC streams** instead of RTSP for these cameras

**HTML5 WebRTC Player Example:**
```html
<video id="v4-camera-stream" autoplay muted></video>
<script>
// Use the signaling data to establish WebRTC connection
// This connects directly to AWS Kinesis Video Streams
</script>
```

### 🔄 Migration Strategy

#### Phase 1: Detect Camera Types
```javascript
async function categorizeCamera(cameraName) {
    const response = await fetch(`http://localhost:5001/api/${cameraName}`);
    const cameraInfo = await response.json();
    
    return {
        name: cameraName,
        model: cameraInfo.product_model,
        isV4: cameraInfo.product_model === "HL_CAM4",
        streamingMethod: cameraInfo.product_model === "HL_CAM4" ? "webrtc" : "rtsp"
    };
}
```

#### Phase 2: Handle Both Protocols
```javascript
async function initializeStream(camera) {
    if (camera.isV4) {
        // Initialize WebRTC stream for v4 cameras
        const signalingData = await fetch(`http://localhost:5001/signaling/${camera.name}?kvs`);
        return setupWebRTCStream(signalingData);
    } else {
        // Initialize RTSP stream for legacy cameras  
        return setupRTSPStream(`rtsp://localhost:8555/${camera.name}`);
    }
}
```

### 📊 Status Monitoring

#### Camera Status Interpretation
```javascript
function interpretCameraStatus(camera) {
    if (camera.model === "HL_CAM4") {
        // v4 cameras show "connecting" but are available via WebRTC
        return {
            available: true,
            method: "webrtc",
            note: "RTSP unavailable, use WebRTC endpoint"
        };
    } else {
        return {
            available: camera.status === "connected",
            method: "rtsp", 
            note: camera.status === "connected" ? "RTSP stream active" : "Camera offline"
        };
    }
}
```

### 🌐 Network Configuration

#### Port Requirements
- **RTSP**: `8555` (for legacy cameras)
- **WebRTC**: `8890` (for v4 cameras)  
- **Web Interface**: `5001`
- **HLS**: `8889`

#### Firewall Considerations
- **Legacy cameras**: Only need local network access
- **v4 cameras**: Require internet access for AWS KVS WebRTC

### ⚠️ Important Notes

#### 1. Camera Model Identification
- **HL_CAM4** = Wyze Cam v4 (requires WebRTC)
- **WYZECP1_JEF** = Wyze Cam v1/v2 (uses RTSP)
- **HL_CAM3P** = Wyze Cam v3 Pro (uses RTSP)
- **HL_PAN3** = Wyze Pan v3 (uses RTSP)

#### 2. Stream Quality
- **RTSP streams**: Full local quality, low latency
- **WebRTC streams**: Cloud-dependent quality, higher latency

#### 3. Fallback Strategy
```javascript
// Always attempt WebRTC for v4 cameras, fallback gracefully
async function getStream(camera) {
    if (camera.isV4) {
        try {
            return await setupWebRTCStream(camera);
        } catch (error) {
            console.warn(`WebRTC failed for ${camera.name}, camera may be offline`);
            return null;
        }
    }
    // Standard RTSP for other cameras
    return setupRTSPStream(camera);
}
```

### 🚀 Implementation Checklist for VistterStudio

- [ ] **Camera Detection**: Query `/api/sse_status` to get all cameras
- [ ] **Model Identification**: Check `product_model` field for each camera  
- [ ] **Protocol Selection**: Use WebRTC for `HL_CAM4`, RTSP for others
- [ ] **WebRTC Integration**: Implement KVS WebRTC client for v4 cameras
- [ ] **Dual Protocol Support**: Handle both RTSP and WebRTC streams
- [ ] **Error Handling**: Graceful fallback when streams unavailable
- [ ] **Status Monitoring**: Interpret "connecting" status for v4 cameras correctly

### 📞 Support Information

**Issue**: Wyze Cam v4 cameras stopped working after February 2025 firmware update
**Root Cause**: TUTK protocol disabled, moved to cloud-only WebRTC streaming
**Solution**: Dual protocol support (RTSP + WebRTC)

**Contact**: This integration was developed to resolve the v4 camera connectivity issue. The WyzeBridge container is now running the standard version with documented WebRTC endpoints for v4 cameras.
