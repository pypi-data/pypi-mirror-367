import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtLottie 1.0

ApplicationWindow {
    id: window
    width: 1920*2
    height: 1080*2
    visible: true
    title: "Qt Lottie - PySide6"
    
    // Animation container
    Rectangle {
        id: animationContainer
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: controlsContainer.top
        anchors.margins: 20
        anchors.bottomMargin: 15
        color: "#f0f0f0"
        border.color: "#ccc"
        
        LottieAnimation {
            id: lottieAnimation
            anchors.centerIn: parent
            height: parent.height
            width: height
            
            source: Qt.resolvedUrl("lottie.json")
            autoPlay: true
            loops: -1
            smooth: true
            cacheMode: 1  // Enable loop caching (CacheMode.CacheLoop)
            
            // Performance optimizations for large sizes
            maxRenderSize: 800  // Balanced quality/performance for large displays
            enableRenderScaling: true  // Enable adaptive scaling for performance
            // directRendering: true  // Direct buffer rendering (enabled by default)
            
            Text {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 5
                text: {
                    switch(lottieAnimation.status) {
                        case 0: return "NULL"
                        case 1: return "LOADING"
                        case 2: return "READY"
                        case 3: return "ERROR"
                        default: return "UNKNOWN"
                    }
                }
                color: lottieAnimation.status === 2 ? "green" : "red"
                font.bold: true
                font.pixelSize: 10
            }

            Text {
                text:  " width: " + lottieAnimation.width + ", height: " + lottieAnimation.height + 
                       "\n render: " + (lottieAnimation.enableRenderScaling ? 
                       "scaled (max " + lottieAnimation.maxRenderSize + "px)" : "full size") +
                       "\n method: " + (lottieAnimation.directRendering ? "direct buffer (optimized)" : "PIL (fallback)") +
                       "\n cache: loop caching enabled"
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.margins: 5
                font.pixelSize: 10
                color: "blue"
            }
        }
    }
    
    // Controls container
    Item {
        id: controlsContainer
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        height: 200
        
        // Control buttons
        Row {
            id: buttonRow
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10
            
            Button {
                text: "Play"
                enabled: lottieAnimation.status === 2
                onClicked: lottieAnimation.play()
            }
            
            Button {
                text: "Pause"
                enabled: lottieAnimation.status === 2
                onClicked: lottieAnimation.pause()
            }
            
            Button {
                text: "Stop"
                enabled: lottieAnimation.status === 2
                onClicked: lottieAnimation.stop()
            }
        }
        
        // Progress section
        Item {
            id: progressSection
            anchors.top: buttonRow.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: 15
            height: 50
            
            Text { 
                id: progressLabel
                text: "Progress:"
                anchors.top: parent.top
                anchors.left: parent.left
            }
            ProgressBar {
                id: progressBar
                anchors.top: progressLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.topMargin: 3
                from: 0
                to: 1
                value: lottieAnimation.progress
            }
            Text {
                anchors.top: progressBar.bottom
                anchors.left: parent.left
                anchors.topMargin: 3
                text: (lottieAnimation.progress * 100).toFixed(1) + "%"
                font.family: "monospace"
                font.pixelSize: 10
            }
        }
        
        // Position section
        Item {
            id: positionSection
            anchors.top: progressSection.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: 10
            height: 50
            
            Text { 
                id: positionLabel
                text: "Position:"
                anchors.top: parent.top
                anchors.left: parent.left
            }
            ProgressBar {
                id: positionBar
                anchors.top: positionLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.topMargin: 3
                from: 0
                to: lottieAnimation.duration
                value: lottieAnimation.position
            }
            Text {
                anchors.top: positionBar.bottom
                anchors.left: parent.left
                anchors.topMargin: 3
                text: lottieAnimation.position.toFixed(1) + "s / " + lottieAnimation.duration.toFixed(1) + "s"
                font.family: "monospace"
                font.pixelSize: 10
            }
        }
        
        // Speed section
        Row {
            id: speedSection
            anchors.top: positionSection.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: 10
            spacing: 10
            
            Text { 
                id: speedLabel
                text: "Speed:"
                anchors.verticalCenter: parent.verticalCenter
            }
            Slider {
                id: speedSlider
                width: parent.width - speedLabel.width - speedText.width - 30
                anchors.verticalCenter: parent.verticalCenter
                from: 0.1
                to: 3.0
                value: 1.0
                stepSize: 0.1
                onValueChanged: lottieAnimation.playbackRate = value
            }
            Text {
                id: speedText
                text: speedSlider.value.toFixed(1) + "x"
                font.family: "monospace"
                anchors.verticalCenter: parent.verticalCenter
            }
        }
        
        // Status
        Text {
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Playing: " + (lottieAnimation.playing ? "Yes" : "No")
        }
    }
}