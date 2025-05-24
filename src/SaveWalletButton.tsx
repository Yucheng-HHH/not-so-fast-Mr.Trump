import { useWallets } from '@mysten/dapp-kit';
import { useState } from 'react';
import { getFullnodeUrl, SuiClient } from '@mysten/sui/client';

// 后端API的URL
const API_URL = 'http://localhost:3001/api/wallets'; 

export function SaveWalletButton() {
  const wallets = useWallets();
  const currentWallet = wallets.length > 0 ? wallets[0] : undefined;
  const currentAccount = currentWallet?.accounts[0];
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const getBalance = async (address: string) => {
    try {
      const client = new SuiClient({
        url: getFullnodeUrl('testnet') // 或您使用的网络
      });
      const allCoins = await client.getAllCoins({
        owner: address
      });
      let totalBalance = 0;
      allCoins.data.forEach(coin => {
        if (coin.coinType === "0x2::sui::SUI") {
          totalBalance += Number(coin.balance);
        }
      });
      return `${(totalBalance / 1000000000).toFixed(4)} SUI`;
    } catch (error) {
      console.error('获取余额失败:', error);
      setErrorMessage('获取余额失败');
      return '0 SUI'; // 返回默认值，允许后续逻辑判断是否成功
    }
  };

  const saveWalletData = async () => {
    if (!currentAccount) {
      setErrorMessage('请先连接钱包');
      setSaveStatus('error');
      setTimeout(() => {
        setSaveStatus('idle');
        setErrorMessage('');
      }, 3000);
      return;
    }

    setSaveStatus('saving');
    setErrorMessage('');

    try {
      const balance = await getBalance(currentAccount.address);
      // 如果 getBalance 内部设置了 errorMessage，说明获取余额失败
      if (errorMessage === '获取余额失败') {
        setSaveStatus('error');
        // 保持错误信息以便用户看到
        setTimeout(() => {
          setSaveStatus('idle');
          setErrorMessage(''); // 清除错误信息
        }, 3000);
        return;
      }

      const walletToSave = {
        address: currentAccount.address,
        name: `SUI Account ${currentAccount.address.substring(0, 6)}...${currentAccount.address.substring(currentAccount.address.length - 4)}`,
        balance: balance,
        network: 'sui', // 或您正在使用的网络
        // last_updated 会在后端设置
      };

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(walletToSave),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || `API响应错误: ${response.status}`);
      }
      
      setSaveStatus('success');
      // 成功后不立即清除错误信息，因为此时应该没有错误
    } catch (error: any) {
      console.error('保存钱包数据失败:', error);
      setErrorMessage(error.message || '保存失败，请检查控制台。');
      setSaveStatus('error');
    }

    setTimeout(() => {
      setSaveStatus('idle');
      if (saveStatus !== 'success') { 
         // 只在之前不是成功状态时清除错误信息，以便用户能看到成功消息
         setErrorMessage('');
      }
    }, 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginTop: '16px' }}>
      {errorMessage && (
        <div style={{
          color: '#ef4444',
          backgroundColor: '#fee2e2',
          padding: '8px 12px',
          borderRadius: '4px',
          fontSize: '14px',
          textAlign: 'center',
          minWidth: '200px',
          border: '1px solid #fca5a5'
        }}>
          {errorMessage}
        </div>
      )}
      <button 
        onClick={saveWalletData}
        disabled={saveStatus === 'saving' || !currentAccount}
        style={{
          backgroundColor: saveStatus === 'success' ? '#4ade80' : 
                          saveStatus === 'error' ? '#ef4444' : '#3b82f6',
          color: 'white',
          padding: '10px 20px',
          borderRadius: '6px',
          border: 'none',
          cursor: saveStatus === 'saving' || !currentAccount ? 'not-allowed' : 'pointer',
          transition: 'background-color 0.3s ease, transform 0.1s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          fontWeight: '500',
          minWidth: '180px'
        }}
        onMouseDown={(e) => { if (saveStatus !== 'saving' && currentAccount) e.currentTarget.style.transform = 'scale(0.98)'; }}
        onMouseUp={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
      >
        {saveStatus === 'saving' && <span className="spinner" style={{marginRight: '8px'}}></span>} 
        {saveStatus === 'saving' ? '保存中...' : 
         saveStatus === 'success' ? '保存成功!' : 
         saveStatus === 'error' ? '保存失败' : '保存钱包信息'}
      </button>
       {/* 简单的CSS Spinner 
       <style jsx global>{`
        .spinner {
          border: 3px solid rgba(255,255,255,0.3);
          border-radius: 50%;
          border-top-color: #fff;
          width: 16px;
          height: 16px;
          animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style> */}
    </div>
  );
}

// 简单的CSS Spinner示例 (如果您想使用)
// <style>
// .spinner {
//   border: 3px solid rgba(255,255,255,0.3);
//   border-radius: 50%;
//   border-top-color: #fff;
//   width: 16px;
//   height: 16px;
//   animation: spin 1s ease-in-out infinite;
//   margin-right: 8px;
// }
// @keyframes spin {
//   to { transform: rotate(360deg); }
// }
// </style>