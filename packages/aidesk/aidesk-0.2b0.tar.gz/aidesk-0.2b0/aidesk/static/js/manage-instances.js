document.addEventListener('DOMContentLoaded', function() {
    const refreshBtn = document.getElementById('refreshBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const instancesTable = document.querySelector('.instances-table tbody');
    
    // 刷新实例列表
    refreshBtn.addEventListener('click', function() {
        fetch('/api/instances')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch instances');
                }
                return response.json();
            })
            .then(data => {
                updateInstancesTable(data);
            })
            .catch(error => {
                alert(error.message);
            });
    });
    
    // 登出功能
    logoutBtn.addEventListener('click', function() {
        fetch('/api/logout', {
            method: 'POST'
        })
        .then(response => {
            window.location.href = '/login';
        })
        .catch(error => {
            alert('Logout failed: ' + error.message);
        });
    });
    
    // 删除实例
    instancesTable.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-btn')) {
            const instanceId = e.target.getAttribute('data-instance-id');
            if (confirm(`Are you sure you want to delete instance ${instanceId}?`)) {
                fetch(`/api/instances/${instanceId}`, {
                    method: 'DELETE'
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.message || 'Failed to delete instance');
                        });
                    }
                    // 删除成功，刷新列表
                    refreshBtn.click();
                })
                .catch(error => {
                    alert(error.message);
                });
            }
        }
    });
    
    // 更新实例表格
    function updateInstancesTable(data) {
        // 清空现有内容（保留表头）
        instancesTable.innerHTML = '';
        
        // 添加主服务器信息
        const masterRow = document.createElement('tr');
        masterRow.className = 'master-row';
        masterRow.innerHTML = `
            <td>Master</td>
            <td>${data.master.hostname}</td>
            <td>${data.master.ip}</td>
            <td>${data.master.port}</td>
            <td>${new Date(data.master.start_time).toLocaleString()}</td>
            <td>${data.master.status}</td>
            <td>N/A</td>
        `;
        instancesTable.appendChild(masterRow);
        
        // 添加从实例信息
        for (const [instanceId, info] of Object.entries(data.instances)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>Slave</td>
                <td>${info.hostname}</td>
                <td>${info.ip}</td>
                <td>${info.port}</td>
                <td>${new Date(info.start_time).toLocaleString()}</td>
                <td>${info.status}</td>
                <td>
                    <button class="delete-btn" data-instance-id="${instanceId}">Delete</button>
                </td>
            `;
            instancesTable.appendChild(row);
        }
    }
});
