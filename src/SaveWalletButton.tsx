import { useWallets } from '@mysten/dapp-kit';
import { useState } from 'react';
import { getFullnodeUrl, SuiClient } from '@mysten/sui/client';

export function SaveWalletButton() {
  const wallets = useWallets();
  const currentWallet = wallets.length > 0 ? wallets[0] : undefined;
  const currentAccount = currentWallet?.accounts[0];
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');

  // 修改获取余额函数
  const getBalance = async (address: string) => {
    try {
      // 创建SUI客户端
      const client = new SuiClient({
        url: getFullnodeUrl('testnet')
      });
      
      // 获取所有代币
      const allCoins = await client.getAllCoins({
        owner: address
      });
      
      // 计算总余额
      let totalBalance = 0;
      allCoins.data.forEach(coin => {
        if (coin.coinType === "0x2::sui::SUI") {
          totalBalance += Number(coin.balance);
        }
      });
      
      // 转换为SUI单位并格式化
      return `${(totalBalance / 1000000000).toFixed(4)} SUI`;
    } catch (error) {
      console.error('获取余额失败:', error);
      return '0 SUI';
    }
  };

  // 保存钱包数据到wallet_data.json
  const saveWalletData = async () => {
    if (!currentAccount) {
      alert('请先连接钱包');
      return;
    }

    try {
      setSaveStatus('saving');
      
      // 获取余额
      const balance = await getBalance(currentAccount.address);
      
      // 准备钱包数据
      const walletData = {
        address: currentAccount.address,
        name: `SUI Account ${currentAccount.address.substring(0, 6)}...`,
        balance: balance,
        network: 'sui',
        last_updated: new Date().toISOString()
      };
      

        // 如果没有Electron API，尝试使用HTTP API
        const apiPort = new URLSearchParams(window.location.search).get('apiPort') || '3000';
        const response = await fetch(`http://localhost:${apiPort}/api/wallets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(walletData)
        });
        
        if (!response.ok) {
            throw new Error(`API响应错误: ${response.status}`);
        }
        
        setSaveStatus('success');
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    catch (error) {
      console.error('保存钱包数据失败:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  return (
    <button 
      onClick={saveWalletData}
      disabled={saveStatus === 'saving' || !currentAccount}
      style={{
        backgroundColor: saveStatus === 'success' ? '#4ade80' : 
                        saveStatus === 'error' ? '#ef4444' : '#3b82f6',
        color: 'white',
        padding: '8px 16px',
        borderRadius: '4px',
        border: 'none',
        cursor: saveStatus === 'saving' || !currentAccount ? 'not-allowed' : 'pointer',
        transition: 'background-color 0.3s',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        marginTop: '16px'
      }}
    >
      {saveStatus === 'saving' && <span>保存中...</span>}
      {saveStatus === 'success' && <span>保存成功!</span>}
      {saveStatus === 'error' && <span>保存失败</span>}
      {saveStatus === 'idle' && <span>保存钱包信息</span>}
    </button>
  );
}