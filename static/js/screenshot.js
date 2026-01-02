// 截图功能实现
function takeScreenshot(addMessageFunction, recordActionFunction = null) {
    // 显示通知
    showNotification('正在准备截图...', 'info');
    
    // 检查浏览器是否支持截图API
    if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
        navigator.mediaDevices.getDisplayMedia({
            video: {
                cursor: 'always'
            },
            audio: false
        })
        .then(stream => {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.onloadedmetadata = () => {
                video.play();
                
                // 创建canvas并绘制视频帧
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                
                // 延迟绘制以确保视频帧已加载
                setTimeout(() => {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    // 停止流
                    stream.getTracks().forEach(track => track.stop());
                    
                    // 将canvas转换为blob并处理
                    canvas.toBlob(blob => {
                        const file = new File([blob], 'screenshot.png', { type: 'image/png' });
                        
                        // 添加截图消息到聊天窗口
                        addMessageFunction('🖼️ 上传了截图: ' + file.name);
                        
                        // 记录用户操作
                        if (recordActionFunction) {
                            recordActionFunction(`上传截图: ${file.name}`);
                        } else {
                            console.log(`上传截图: ${file.name}`);
                        }
                        
                        // 显示成功通知
                        showNotification('截图成功', 'success');
                    }, 'image/png');
                }, 100);
            };
        })
        .catch(error => {
            showNotification(`截图失败: ${error.message}`, 'error');
            console.error('截图失败:', error);
            if (recordActionFunction) {
                recordActionFunction(`截图失败: ${error.message}`);
            }
        });
    } else {
        showNotification('您的浏览器不支持截图功能', 'error');
        if (recordActionFunction) {
            recordActionFunction('浏览器不支持截图功能');
        }
    }
}

// 通知功能实现
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transform: translateY(-20px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    `;
    
    // 设置不同类型的背景色
    const typeColors = {
        success: '#4CAF50',
        error: '#f44336',
        info: '#2196F3',
        warning: '#ff9800'
    };
    notification.style.backgroundColor = typeColors[type] || typeColors.info;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示通知
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // 3秒后隐藏通知
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        
        // 移除元素
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}