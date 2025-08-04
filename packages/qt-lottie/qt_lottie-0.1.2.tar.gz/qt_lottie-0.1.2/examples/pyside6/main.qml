import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLottie 1.0

ApplicationWindow {
    id: window
    width: 600
    height: 500
    visible: true
    title: "Qt Lottie - PySide6"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15
        
        // Animation
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 250
            color: "#f0f0f0"
            border.color: "#ccc"
            
            LottieAnimation {
                id: lottieAnimation
                anchors.centerIn: parent
                width: Math.min(parent.width - 20, 300)
                height: Math.min(parent.height - 20, 300)
                
                source: "file://" + Qt.resolvedUrl("lottie.json").toString().slice(7)
                autoPlay: true
                loops: -1
                smooth: true
                
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
            }
        }
        
        // Controls
        RowLayout {
            Layout.fillWidth: true
            
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
        
        // Progress
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 3
            
            Text { text: "Progress:" }
            ProgressBar {
                Layout.fillWidth: true
                from: 0
                to: 1
                value: lottieAnimation.progress
            }
            Text {
                text: (lottieAnimation.progress * 100).toFixed(1) + "%"
                font.family: "monospace"
                font.pixelSize: 10
            }
        }
        
        // Position
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 3
            
            Text { text: "Position:" }
            ProgressBar {
                Layout.fillWidth: true
                from: 0
                to: lottieAnimation.duration
                value: lottieAnimation.position
            }
            Text {
                text: lottieAnimation.position.toFixed(1) + "s / " + lottieAnimation.duration.toFixed(1) + "s"
                font.family: "monospace"
                font.pixelSize: 10
            }
        }
        
        // Speed
        RowLayout {
            Layout.fillWidth: true
            
            Text { text: "Speed:" }
            Slider {
                Layout.fillWidth: true
                from: 0.1
                to: 3.0
                value: 1.0
                stepSize: 0.1
                onValueChanged: lottieAnimation.playbackRate = value
            }
            Text {
                text: parent.children[1].value.toFixed(1) + "x"
                font.family: "monospace"
            }
        }
        
        // Status
        Text {
            Layout.fillWidth: true
            text: "Playing: " + (lottieAnimation.playing ? "Yes" : "No")
            horizontalAlignment: Text.AlignHCenter
        }
    }
}