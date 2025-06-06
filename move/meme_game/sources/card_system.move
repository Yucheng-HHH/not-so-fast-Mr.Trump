module meme_game::card_system {
    use std::vector;
    use std::string::{Self, String};
    
    use sui::object::{Self, ID, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::event;
    use sui::clock::{Self, Clock};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    
    use meme_game::meme_nft;
    
    // ===== 错误代码 =====
    /// 余额不足
    const EInsufficientFunds: u64 = 1;
    /// 没有权限执行操作
    const ENotAuthorized: u64 = 2;
    /// 无效的卡片类型
    const EInvalidCardType: u64 = 3;
    /// 概率总和不等于100
    const EProbabilityNotEqualTo100: u64 = 4;
    
    // ===== 常量 =====
    /// 单次抽卡费用（0.01 SUI）
    const SINGLE_DRAW_FEE: u64 = 10_000_000;
    /// 十连抽费用（0.09 SUI，打9折）
    const TEN_DRAW_FEE: u64 = 90_000_000;
    
    // ===== 类型定义 =====
    
    /// 卡片类型
    struct CardType has store, copy, drop {
        /// 卡片类型ID
        id: u8,
        /// 卡片名称
        name: String,
        /// 卡片描述
        description: String,
        /// 卡片图片URL前缀
        image_url_prefix: String,
        /// 卡片稀有度（1-5）
        rarity: u8,
        /// 掉落概率（1-100）
        drop_rate: u8
    }
    
    /// 卡片配置
    struct CardConfig has key {
        id: UID,
        /// 管理员地址
        admin: address,
        /// 卡片类型列表
        card_types: vector<CardType>,
        /// 单次抽卡费用
        single_draw_fee: u64,
        /// 十连抽费用
        ten_draw_fee: u64,
        /// 抽卡总次数
        total_draws: u64,
        /// 收集的费用总额
        total_fees: u64
    }
    
    /// 抽卡记录
    struct DrawRecord has store {
        /// 抽卡时间戳
        timestamp: u64,
        /// 抽到的卡片类型ID
        card_type_id: u8,
        /// 生成的NFT ID
        nft_id: ID
    }
    
    /// 用户抽卡历史
    struct UserDrawHistory has key {
        id: UID,
        /// 用户地址
        user: address,
        /// 抽卡记录
        records: vector<DrawRecord>,
        /// 总抽卡次数
        total_draws: u64
    }
    
    // ===== 事件 =====
    
    /// 抽卡事件
    struct CardDrawn has copy, drop {
        /// 抽卡用户
        drawer: address,
        /// 卡片类型ID
        card_type_id: u8,
        /// 卡片名称
        card_name: String,
        /// 卡片稀有度
        rarity: u8,
        /// 生成的NFT ID
        nft_id: ID,
        /// 抽卡时间戳
        timestamp: u64
    }
    
    /// 卡片配置更新事件
    struct CardConfigUpdated has copy, drop {
        /// 更新者
        updater: address,
        /// 单次抽卡费用
        single_draw_fee: u64,
        /// 十连抽费用
        ten_draw_fee: u64,
        /// 卡片类型数量
        card_type_count: u64
    }
    
    // ===== 函数 =====
    
    /// 创建卡片配置
    public entry fun create_card_config(ctx: &mut TxContext) {
        let config = CardConfig {
            id: object::new(ctx),
            admin: tx_context::sender(ctx),
            card_types: vector::empty(),
            single_draw_fee: SINGLE_DRAW_FEE,
            ten_draw_fee: TEN_DRAW_FEE,
            total_draws: 0,
            total_fees: 0
        };
        
        // 初始化一些基础卡片类型
        add_card_type_internal(
            &mut config,
            1,
            string::utf8(b"Common Meme"),
            string::utf8(b"A common meme card"),
            string::utf8(b"https://memevstrump.game/nft/common/"),
            1, // 稀有度
            60 // 60%概率
        );
        
        add_card_type_internal(
            &mut config,
            2,
            string::utf8(b"Uncommon Meme"),
            string::utf8(b"An uncommon meme card"),
            string::utf8(b"https://memevstrump.game/nft/uncommon/"),
            2, // 稀有度
            25 // 25%概率
        );
        
        add_card_type_internal(
            &mut config,
            3,
            string::utf8(b"Rare Meme"),
            string::utf8(b"A rare meme card"),
            string::utf8(b"https://memevstrump.game/nft/rare/"),
            3, // 稀有度
            10 // 10%概率
        );
        
        add_card_type_internal(
            &mut config,
            4,
            string::utf8(b"Epic Meme"),
            string::utf8(b"An epic meme card"),
            string::utf8(b"https://memevstrump.game/nft/epic/"),
            4, // 稀有度
            4 // 4%概率
        );
        
        add_card_type_internal(
            &mut config,
            5,
            string::utf8(b"Legendary Meme"),
            string::utf8(b"A legendary meme card"),
            string::utf8(b"https://memevstrump.game/nft/legendary/"),
            5, // 稀有度
            1 // 1%概率
        );
        
        // 验证概率总和是否为100%
        validate_drop_rates(&config.card_types);
        
        // 共享卡片配置对象
        transfer::share_object(config);
        
        // 发送配置更新事件
        event::emit(CardConfigUpdated {
            updater: tx_context::sender(ctx),
            single_draw_fee: SINGLE_DRAW_FEE,
            ten_draw_fee: TEN_DRAW_FEE,
            card_type_count: 5
        });
    }
    
    /// 创建用户抽卡历史记录
    fun create_user_draw_history(user: address, ctx: &mut TxContext): UserDrawHistory {
        UserDrawHistory {
            id: object::new(ctx),
            user,
            records: vector::empty(),
            total_draws: 0
        }
    }
    
    /// 添加新的卡片类型 (内部函数)
    fun add_card_type_internal(
        config: &mut CardConfig,
        id: u8,
        name: String,
        description: String,
        image_url_prefix: String,
        rarity: u8,
        drop_rate: u8
    ) {
        let card_type = CardType {
            id,
            name,
            description,
            image_url_prefix,
            rarity,
            drop_rate
        };
        
        vector::push_back(&mut config.card_types, card_type);
    }
    
    /// 验证掉落率总和是否为100%
    fun validate_drop_rates(card_types: &vector<CardType>) {
        let len = vector::length(card_types);
        assert!(len > 0, EInvalidCardType);
        
        let total_rate = 0u8;
        let i = 0;
        
        while (i < len) {
            let card_type = vector::borrow(card_types, i);
            total_rate = total_rate + card_type.drop_rate;
            i = i + 1;
        };
        
        assert!(total_rate == 100, EProbabilityNotEqualTo100);
    }
    
    /// 添加新的卡片类型 (管理员功能)
    public entry fun add_card_type(
        config: &mut CardConfig,
        id: u8,
        name: vector<u8>,
        description: vector<u8>,
        image_url_prefix: vector<u8>,
        rarity: u8,
        drop_rate: u8,
        ctx: &mut TxContext
    ) {
        // 检查调用者是否为管理员
        assert!(tx_context::sender(ctx) == config.admin, ENotAuthorized);
        
        add_card_type_internal(
            config,
            id,
            string::utf8(name),
            string::utf8(description),
            string::utf8(image_url_prefix),
            rarity,
            drop_rate
        );
        
        // 验证概率总和是否为100%
        validate_drop_rates(&config.card_types);
        
        // 发送配置更新事件
        event::emit(CardConfigUpdated {
            updater: tx_context::sender(ctx),
            single_draw_fee: config.single_draw_fee,
            ten_draw_fee: config.ten_draw_fee,
            card_type_count: vector::length(&config.card_types)
        });
    }
    
    /// 设置抽卡费用 (管理员功能)
    public entry fun set_draw_fees(
        config: &mut CardConfig,
        single_draw_fee: u64,
        ten_draw_fee: u64,
        ctx: &mut TxContext
    ) {
        // 检查调用者是否为管理员
        assert!(tx_context::sender(ctx) == config.admin, ENotAuthorized);
        
        config.single_draw_fee = single_draw_fee;
        config.ten_draw_fee = ten_draw_fee;
        
        // 发送配置更新事件
        event::emit(CardConfigUpdated {
            updater: tx_context::sender(ctx),
            single_draw_fee,
            ten_draw_fee,
            card_type_count: vector::length(&config.card_types)
        });
    }
    
    /// 单次抽卡
    public entry fun draw_card(
        config: &mut CardConfig,
        payment: &mut Coin<SUI>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // 检查支付金额是否足够
        assert!(coin::value(payment) >= config.single_draw_fee, EInsufficientFunds);
        
        // 扣除费用
        let fee = coin::split(payment, config.single_draw_fee, ctx);
        transfer::public_transfer(fee, config.admin);
        
        // 更新统计数据
        config.total_draws = config.total_draws + 1;
        config.total_fees = config.total_fees + config.single_draw_fee;
        
        // 执行抽卡
        let sender = tx_context::sender(ctx);
        let timestamp = clock::timestamp_ms(clock);
        
        draw_card_internal(config, sender, timestamp, ctx);
    }
    
    /// 十连抽
    public entry fun draw_cards_batch(
        config: &mut CardConfig,
        payment: &mut Coin<SUI>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // 检查支付金额是否足够
        assert!(coin::value(payment) >= config.ten_draw_fee, EInsufficientFunds);
        
        // 扣除费用
        let fee = coin::split(payment, config.ten_draw_fee, ctx);
        transfer::public_transfer(fee, config.admin);
        
        // 更新统计数据
        config.total_draws = config.total_draws + 10;
        config.total_fees = config.total_fees + config.ten_draw_fee;
        
        // 执行十连抽
        let sender = tx_context::sender(ctx);
        let timestamp = clock::timestamp_ms(clock);
        
        let i = 0;
        while (i < 10) {
            // 每次抽卡使用不同的时间戳派生值，增加随机性
            let derived_timestamp = timestamp + (i as u64);
            draw_card_internal(config, sender, derived_timestamp, ctx);
            i = i + 1;
        }
    }
    
    /// 内部抽卡实现
    fun draw_card_internal(
        config: &CardConfig,
        recipient: address,
        timestamp: u64,
        ctx: &mut TxContext
    ) {
        // 使用时间戳作为随机数种子
        let seed = timestamp + config.total_draws;
        
        // 选择卡片类型
        let card_type = select_card_type(&config.card_types, seed);
        
        // 为卡片生成唯一ID（用于图片URL）
        let card_id = ((timestamp % 1000000) as u64);
        
        // 生成NFT元数据
        let name = card_type.name;
        let description = card_type.description;
        
        // 生成完整的图片URL
        let url = generate_card_url(&card_type.image_url_prefix, card_id);
        
        // 铸造NFT
        let nft_id = meme_nft::mint_from_card_system(
            string::to_bytes(copy name),
            string::to_bytes(copy description),
            string::to_bytes(copy url),
            card_type.rarity,
            recipient,
            ctx
        );
        
        // 发送抽卡事件
        event::emit(CardDrawn {
            drawer: recipient,
            card_type_id: card_type.id,
            card_name: name,
            rarity: card_type.rarity,
            nft_id,
            timestamp
        });
    }
    
    /// 根据概率选择卡片类型
    fun select_card_type(card_types: &vector<CardType>, seed: u64): CardType {
        let len = vector::length(card_types);
        assert!(len > 0, EInvalidCardType);
        
        // 生成0-99之间的随机数
        let random = ((seed % 100) as u8);
        
        let cumulative = 0u8;
        let i = 0;
        
        while (i < len) {
            let card_type = *vector::borrow(card_types, i);
            cumulative = cumulative + card_type.drop_rate;
            
            if (random < cumulative) {
                return card_type
            };
            
            i = i + 1;
        };
        
        // 默认返回第一种卡片类型
        *vector::borrow(card_types, 0)
    }
    
    /// 生成卡片完整URL
    fun generate_card_url(prefix: &String, card_id: u64): String {
        let mut url = *prefix;
        string::append_str(&mut url, u64_to_string(card_id));
        string::append_str(&mut url, string::utf8(b".png"));
        url
    }
    
    /// 将u64转换为字符串
    fun u64_to_string(value: u64): String {
        if (value == 0) {
            return string::utf8(b"0")
        };
        
        let mut buffer = vector::empty<u8>();
        let mut temp = value;
        
        while (temp > 0) {
            let digit = (((temp % 10) as u8) + 48u8);
            vector::push_back(&mut buffer, digit);
            temp = temp / 10;
        };
        
        // 反转buffer
        let len = vector::length(&buffer);
        let mut i = 0;
        let mut j = len - 1;
        
        while (i < j) {
            let temp_val = *vector::borrow(&buffer, i);
            *vector::borrow_mut(&mut buffer, i) = *vector::borrow(&buffer, j);
            *vector::borrow_mut(&mut buffer, j) = temp_val;
            i = i + 1;
            j = j - 1;
        };
        
        string::utf8(buffer)
    }
    
    /// 获取卡片配置信息
    public fun get_config_info(config: &CardConfig): (address, u64, u64, u64, u64) {
        (
            config.admin,
            config.single_draw_fee,
            config.ten_draw_fee,
            config.total_draws,
            config.total_fees
        )
    }
    
    /// 获取卡片类型数量
    public fun get_card_type_count(config: &CardConfig): u64 {
        vector::length(&config.card_types)
    }
    
    /// 获取卡片类型信息
    public fun get_card_type_info(config: &CardConfig, index: u64): (u8, String, u8, u8) {
        assert!(index < vector::length(&config.card_types), EInvalidCardType);
        
        let card_type = vector::borrow(&config.card_types, index);
        (
            card_type.id,
            card_type.name,
            card_type.rarity,
            card_type.drop_rate
        )
    }
    
    /// 获取用户抽卡总次数
    public fun get_user_total_draws(history: &UserDrawHistory): u64 {
        history.total_draws
    }
}