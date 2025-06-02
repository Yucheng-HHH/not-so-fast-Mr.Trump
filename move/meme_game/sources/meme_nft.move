module meme_game::meme_nft {
    use std::string::{Self, String};
    
    use sui::object::{Self, ID, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::url::{Self, Url};
    use sui::event;
    use sui::package;
    use sui::display;

    // ===== 错误代码 =====
    /// 没有权限执行操作
    const ENotAuthorized: u64 = 1;
    /// 无效的稀有度值
    const EInvalidRarity: u64 = 2;

    // ===== 常量 =====
    /// 最高稀有度级别
    const MAX_RARITY: u8 = 5;

    // ===== 类型定义 =====
    
    /// 一次性见证，用于初始化
    struct MEME_NFT has drop {}
    
    /// NFT稀有度类型
    struct Rarity has store, copy, drop {
        /// 稀有度值，范围1-5
        value: u8
    }
    
    /// Meme NFT结构
    struct MemeNFT has key, store {
        /// NFT的唯一ID
        id: UID,
        /// NFT名称
        name: String,
        /// NFT描述
        description: String,
        /// NFT图片URL
        url: Url,
        /// NFT稀有度
        rarity: Rarity,
        /// NFT创建者
        creator: address
    }
    
    /// NFT集合，用于管理NFT的铸造权限
    struct MemeCollection has key {
        id: UID,
        /// 管理员地址
        admin: address,
        /// 已铸造的NFT数量
        minted_count: u64
    }
    
    // ===== 事件 =====
    
    /// NFT铸造事件
    struct NFTMinted has copy, drop {
        nft_id: ID,
        name: String,
        creator: address,
        owner: address,
        rarity: u8
    }
    
    // ===== 函数 =====
    
    /// 初始化函数，创建NFT集合和Display信息
    fun init(witness: MEME_NFT, ctx: &mut TxContext) {
        // 创建NFT集合
        let collection = MemeCollection {
            id: object::new(ctx),
            admin: tx_context::sender(ctx),
            minted_count: 0
        };
        
        // 转移集合给创建者
        transfer::transfer(collection, tx_context::sender(ctx));
        
        // 创建和共享Display信息，用于在钱包和市场中显示NFT
        let publisher = package::claim(witness, ctx);
        
        let keys = vector[
            string::utf8(b"name"),
            string::utf8(b"description"),
            string::utf8(b"image_url"),
            string::utf8(b"creator"),
            string::utf8(b"rarity")
        ];
        
        let values = vector[
            string::utf8(b"{name}"),
            string::utf8(b"{description}"),
            string::utf8(b"{url}"),
            string::utf8(b"{creator}"),
            string::utf8(b"Rarity: {rarity}")
        ];
        
        let display = display::new_with_fields<MemeNFT>(
            &publisher, keys, values, ctx
        );
        
        display::update_version(&mut display);
        
        // 将Display设置为不可变
        transfer::public_freeze_object(display);
        transfer::public_freeze_object(publisher);
    }
    
    /// 创建稀有度对象
    public fun create_rarity(value: u8): Rarity {
        assert!(value > 0 && value <= MAX_RARITY, EInvalidRarity);
        Rarity { value }
    }
    
    /// 获取稀有度值
    public fun get_rarity_value(rarity: &Rarity): u8 {
        rarity.value
    }
    
    /// 铸造新的Meme NFT (管理员功能)
    public entry fun mint_admin(
        collection: &mut MemeCollection,
        name: vector<u8>,
        description: vector<u8>,
        url: vector<u8>,
        rarity_value: u8,
        recipient: address,
        ctx: &mut TxContext
    ) {
        // 检查调用者是否为管理员
        assert!(tx_context::sender(ctx) == collection.admin, ENotAuthorized);
        
        // 创建NFT
        let nft = MemeNFT {
            id: object::new(ctx),
            name: string::utf8(name),
            description: string::utf8(description),
            url: url::new_unsafe_from_bytes(url),
            rarity: create_rarity(rarity_value),
            creator: tx_context::sender(ctx)
        };
        
        // 增加已铸造计数
        collection.minted_count = collection.minted_count + 1;
        
        // 发送事件
        event::emit(NFTMinted {
            nft_id: object::id(&nft),
            name: nft.name,
            creator: nft.creator,
            owner: recipient,
            rarity: rarity_value
        });
        
        // 转移NFT给接收者
        transfer::transfer(nft, recipient);
    }
    
    /// 通过抽卡系统铸造NFT (供抽卡系统调用)
    public fun mint_from_card_system(
        name: vector<u8>,
        description: vector<u8>,
        url: vector<u8>,
        rarity_value: u8,
        recipient: address,
        ctx: &mut TxContext
    ): ID {
        // 创建NFT
        let nft = MemeNFT {
            id: object::new(ctx),
            name: string::utf8(name),
            description: string::utf8(description),
            url: url::new_unsafe_from_bytes(url),
            rarity: create_rarity(rarity_value),
            creator: tx_context::sender(ctx)
        };
        
        let nft_id = object::id(&nft);
        
        // 发送事件
        event::emit(NFTMinted {
            nft_id,
            name: nft.name,
            creator: nft.creator,
            owner: recipient,
            rarity: rarity_value
        });
        
        // 转移NFT给接收者
        transfer::transfer(nft, recipient);
        
        nft_id
    }
    
    /// 转移NFT给新所有者
    public entry fun transfer_nft(
        nft: MemeNFT,
        recipient: address
    ) {
        transfer::transfer(nft, recipient);
    }
    
    /// 获取NFT信息
    public fun get_nft_info(nft: &MemeNFT): (String, String, Url, u8, address) {
        (
            nft.name,
            nft.description,
            nft.url,
            nft.rarity.value,
            nft.creator
        )
    }
    
    /// 获取NFT ID
    public fun get_nft_id(nft: &MemeNFT): ID {
        object::id(nft)
    }
    
    /// 获取NFT稀有度
    public fun get_nft_rarity(nft: &MemeNFT): u8 {
        nft.rarity.value
    }
    
    /// 获取已铸造的NFT数量
    public fun get_minted_count(collection: &MemeCollection): u64 {
        collection.minted_count
    }
}