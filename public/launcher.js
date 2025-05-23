const { createApp, ref, onMounted, onUnmounted, watch } = Vue;

createApp({
  setup() {
    // 现有代码
    const petContainer = ref(null);
    const petX = ref(window.innerWidth / 2 - 50);
    const petY = ref(window.innerHeight / 3 - 50);
    const dragging = ref(false);
    const offsetX = ref(0);
    const offsetY = ref(0);
    const showAccountList = ref(false);
    
    // 新增钱包状态管理
    const walletAccounts = ref([]);
    const isWalletConnecting = ref(false);
    const walletError = ref('');
    let walletRefreshInterval = null;
    const apiPort = ref(null);
    
    // 从数据库获取钱包列表
    const fetchWallets = async () => {
      if (!window.electron) return;
      
      try {
        const result = await window.electron.getWallets();
        if (result.success && result.wallets) {
          walletAccounts.value = result.wallets.map(wallet => ({
            name: wallet.name,
            address: wallet.address,
            balance: wallet.balance,
            icon: wallet.icon,
            lastUpdated: new Date(wallet.last_updated).toLocaleString()
          }));
        } else {
          console.error('Failed to get wallets:', result.error);
        }
      } catch (error) {
        console.error('Error fetching wallets:', error);
      }
    };
    
    // 启动钱包数据自动刷新
    const startWalletRefresh = () => {
      stopWalletRefresh(); // 确保不会重复启动
      walletRefreshInterval = setInterval(fetchWallets, 5000); // 每5秒刷新一次
    };
    
    // 停止钱包数据自动刷新
    const stopWalletRefresh = () => {
      if (walletRefreshInterval) {
        clearInterval(walletRefreshInterval);
        walletRefreshInterval = null;
      }
    };
    
    // 获取 API 端口
    const getApiPort = async () => {
      if (window.electron) {
        try {
          apiPort.value = await window.electron.getApiPort();
          console.log('API Port:', apiPort.value);
        } catch (error) {
          console.error('Failed to get API port:', error);
        }
      }
    };
    
    // 添加缺失的函数
    const petWidth = 100;
    const petHeight = 100;
    let moveInterval = null;
    let moveDirection = { x: 1, y: 1 };
    
    function updatePetPositionOnResize() {
      if (window.innerWidth < petX.value + petWidth) {
        petX.value = window.innerWidth - petWidth;
      }
      if (window.innerHeight < petY.value + petHeight) {
        petY.value = window.innerHeight - petHeight;
      }
    }
    
    function startAutoMove() {
      if (moveInterval) return;
      
      moveInterval = setInterval(() => {
        // 随机移动方向
        if (Math.random() < 0.05) {
          moveDirection.x = Math.random() > 0.5 ? 1 : -1;
          moveDirection.y = Math.random() > 0.5 ? 1 : -1;
        }
        
        // 更新位置
        petX.value += moveDirection.x;
        petY.value += moveDirection.y;
        
        // 边界检查
        if (petX.value <= 0 || petX.value >= window.innerWidth - petWidth) {
          moveDirection.x *= -1;
          petX.value = Math.max(0, Math.min(petX.value, window.innerWidth - petWidth));
        }
        
        if (petY.value <= 0 || petY.value >= window.innerHeight - petHeight) {
          moveDirection.y *= -1;
          petY.value = Math.max(0, Math.min(petY.value, window.innerHeight - petHeight));
        }
      }, 50);
    }
    
    function stopAutoMove() {
      if (moveInterval) {
        clearInterval(moveInterval);
        moveInterval = null;
      }
    }
    
    function handleMouseDown(event) {
      event.preventDefault();
      dragging.value = true;
      offsetX.value = event.clientX - petX.value;
      offsetY.value = event.clientY - petY.value;
      stopAutoMove();
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    
    function handleMouseMove(event) {
      if (!dragging.value) return;
      
      petX.value = Math.max(0, Math.min(event.clientX - offsetX.value, window.innerWidth - petWidth));
      petY.value = Math.max(0, Math.min(event.clientY - offsetY.value, window.innerHeight - petHeight));
    }
    
    function handleMouseUp() {
      dragging.value = false;
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      startAutoMove();
    }

    const toggleAccountList = () => {
      showAccountList.value = !showAccountList.value;
      if (showAccountList.value) {
        stopAutoMove();
        fetchWallets(); // 获取最新的钱包列表
      } else {
        startAutoMove();
      }
    };
    
    const handleConnectWallet = async () => {
      isWalletConnecting.value = true;
      walletError.value = '';
      
      // 确保已获取 API 端口
      if (!apiPort.value && window.electron) {
        await getApiPort();
      }
      
      // 构建包含 API 端口的 URL
      const baseUrl = 'http://localhost:5173';
      const urlWithPort = apiPort.value 
        ? `${baseUrl}?apiPort=${apiPort.value}` 
        : baseUrl;
      
      if (window.electron) {
        window.electron.connectWallet(urlWithPort);
      } else {
        window.open(urlWithPort, '_blank');
      }
      
      // 启动自动刷新，检查新钱包
      startWalletRefresh();
    };
    
    // 格式化地址显示
    const formatAddress = (address) => {
      if (!address) return '';
      if (address.length <= 10) return address;
      return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    };
    
    // 复制到剪贴板
    const copyToClipboard = (text) => {
      navigator.clipboard.writeText(text).then(() => {
        alert('地址已复制到剪贴板!');
      }).catch(err => {
        console.error('复制失败:', err);
      });
    };
    
    // 清除钱包数据
    const clearWallets = async () => {
      if (!window.electron) return;
      
      if (confirm('确定要清除所有钱包数据吗?')) {
        try {
          await window.electron.clearWallets();
          walletAccounts.value = [];
          alert('钱包数据已清除');
        } catch (error) {
          console.error('清除钱包数据失败:', error);
          alert('清除失败: ' + error.message);
        }
      }
    };
    
    onMounted(async () => {
      updatePetPositionOnResize();
      startAutoMove();
      window.addEventListener('resize', updatePetPositionOnResize);
      
      // 获取 API 端口并加载初始钱包数据
      await getApiPort();
      await fetchWallets();
      
      // 如果有钱包，启动自动刷新
      if (walletAccounts.value.length > 0) {
        startWalletRefresh();
      }
    });
    
    onUnmounted(() => {
      stopAutoMove();
      stopWalletRefresh();
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('resize', updatePetPositionOnResize);
    });
    
    // 监听钱包列表变化
    watch(walletAccounts, (newAccounts) => {
      if (newAccounts.length > 0) {
        isWalletConnecting.value = false;
      }
    });
    
    return {
      petContainer, petX, petY, showAccountList,
      walletAccounts, isWalletConnecting, walletError,
      handleMouseDown, toggleAccountList, handleConnectWallet,
      petWidth, petHeight, formatAddress, copyToClipboard, clearWallets
    };
  },
  template: `
    <div 
      id="pet-container" 
      ref="petContainer" 
      :style="{ left: petX + 'px', top: petY + 'px', width: petWidth + 'px', height: petHeight + 'px' }"
      @mousedown="handleMouseDown"
    >
      <div class="gear-icon-container" @click.stop="toggleAccountList" title="设置">
        <span class="gear-icon">⚙️</span>
      </div>
      <svg width="100" height="100" viewBox="0 0 100 100" class="desktop-pet">
        <circle cx="50" cy="50" r="45" fill="yellow" stroke="black" stroke-width="2" />
        <circle cx="35" cy="40" r="5" fill="black" />
        <circle cx="65" cy="40" r="5" fill="black" />
        <path d="M 30 65 Q 50 80 70 65" stroke="black" stroke-width="3" fill="transparent" />
      </svg>

      <div v-if="showAccountList" class="account-list-modal">
        <div class="account-list-header">
          <h3>钱包账户</h3>
          <button @click="toggleAccountList" class="close-button">&times;</button>
        </div>
        
        <div class="account-list-content">
          <!-- 已连接的钱包账户 -->
          <div v-if="walletAccounts.length > 0" class="connected-accounts">
            <div v-for="(account, index) in walletAccounts" :key="index" class="account-item">
              <div class="account-icon">🪙</div>
              <div class="account-details">
                <span class="account-name">{{ account.name }}</span>
                <span class="account-address" title="点击复制地址" @click="copyToClipboard(account.address)">
                  地址: {{ formatAddress(account.address) }}
                </span>
              </div>
              <div class="account-balance-container">
                <div class="balance-label">余额:</div>
                <div class="balance-value">{{ account.balance }}</div>
                <div class="balance-updated">更新于: {{ account.lastUpdated }}</div>
              </div>
            </div>
          </div>
          
          <!-- 无账户时显示提示 -->
          <div v-else-if="!isWalletConnecting" class="no-accounts">
            <p class="empty-message">未连接钱包</p>
            <p class="help-text">请点击"连接钱包"或在SUI应用中保存钱包</p>
          </div>
          
          <!-- 加载状态 -->
          <div v-else class="loading-accounts">
            <p class="loading-message">连接中...</p>
          </div>
        </div>
        
        <div class="account-list-footer">
          <button 
            class="connect-wallet-button" 
            @click="handleConnectWallet"
            :disabled="isWalletConnecting"
          >
            <span v-if="isWalletConnecting">连接中...</span>
            <span v-else-if="walletAccounts.length > 0">刷新钱包</span>
            <span v-else>连接钱包</span>
          </button>
          <button 
            v-if="walletAccounts.length > 0"
            class="remove-wallet-button" 
            @click="clearWallets"
          >
            清除钱包数据
          </button>
        </div>
      </div>
    </div>
  `
}).mount('#smiley-app');