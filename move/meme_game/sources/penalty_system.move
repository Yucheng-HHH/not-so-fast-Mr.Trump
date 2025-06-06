module meme_game::penalty_system {
    use std::string::{Self, String};
    use std::vector;
    
    use sui::object::{Self, ID, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::event;
    use sui::table::{Self, Table};
    use sui::clock::{Self, Clock};
    
    // ===== 错误代码 =====
    /// 没有权限执行操作
    const ENotAuthorized: u64 = 1;
    /// 惩罚记录不存在
    const EPenaltyNotFound: u64 = 2;
    /// 无效的惩罚类型
    const EInvalidPenaltyType: u64 = 3;
    /// 无效的惩罚时长
    const EInvalidPenaltyDuration: u64 = 4;
    /// 惩罚已过期
    const EPenaltyExpired: u64 = 5;
    /// 惩罚未过期
    const EPenaltyNotExpired: u64 = 6;
    
    // ===== 常量 =====
    /// 惩罚类型：警告
    const PENALTY_TYPE_WARNING: u8 = 1;
    /// 惩罚类型：禁止抽卡
    const PENALTY_TYPE_NO_DRAW: u8 = 2;
    /// 惩罚类型：禁止战斗
    const PENALTY_TYPE_NO_BATTLE: u8 = 3;
    /// 惩罚类型：禁止所有活动
    const PENALTY_TYPE_BAN: u8 = 4;
    
    /// 永久惩罚标记
    const PERMANENT_PENALTY: u64 = 0;
    
    // ===== 类型定义 =====
    
    /// 惩罚记录
    struct PenaltyRecord has store, copy, drop {
        /// 惩罚ID
        id: ID,
        /// 惩罚类型
        penalty_type: u8,
        /// 惩罚原因
        reason: String,
        /// 惩罚开始时间
        start_time: u64,
        /// 惩罚结束时间（0表示永久）
        end_time: u64,
        /// 是否已解除
        revoked: bool,
        /// 惩罚施加者
        issuer: address
    }
    
    /// 惩罚类型定义
    struct PenaltyType has store, copy, drop {
        /// 类型ID
        id: u8,
        /// 类型名称
        name: String,
        /// 类型描述
        description: String,
        /// 默认惩罚时长（毫秒）
        default_duration: u64
    }
    
    /// 惩罚系统
    struct PenaltySystem has key {
        id: UID,
        /// 管理员地址
        admin: address,
        /// 惩罚类型定义
        penalty_types: vector<PenaltyType>,
        /// 用户惩罚记录
        penalties: Table<address, vector<PenaltyRecord>>,
        /// 活跃惩罚记录（未过期且未撤销）
        active_penalties: Table<address, vector<PenaltyRecord>>,
        /// 总惩罚次数
        total_penalties: u64
    }
    
    // ===== 事件 =====
    
    /// 惩罚应用事件
    struct PenaltyApplied has copy, drop {
        /// 惩罚ID
        penalty_id: ID,
        /// 被惩罚用户
        target: address,
        /// 惩罚类型
        penalty_type: u8,
        /// 惩罚原因
        reason: String,
        /// 惩罚开始时间
        start_time: u64,
        /// 惩罚结束时间
        end_time: u64,
        /// 惩罚施加者
        issuer: address
    }
    
    /// 惩罚解除事件
    struct PenaltyRevoked has copy, drop {
        /// 惩罚ID
        penalty_id: ID,
        /// 被惩罚用户
        target: address,
        /// 惩罚类型
        penalty_type: u8,
        /// 解除时间
        revoke_time: u64,
        /// 解除者
        revoker: address
    }
    
    // ===== 函数 =====
    
    /// 创建惩罚系统
    public entry fun create_penalty_system(ctx: &mut TxContext) {
        let penalty_system = PenaltySystem {
            id: object::new(ctx),
            admin: tx_context::sender(ctx),
            penalty_types: vector::empty(),
            penalties: table::new(ctx),
            active_penalties: table::new(ctx),
            total_penalties: 0
        };
        
        // 初始化惩罚类型
        add_penalty_type_internal(
            &mut penalty_system,
            PENALTY_TYPE_WARNING,
            string::utf8(b"Warning"),
            string::utf8(b"A warning without actual restrictions"),
            0 // 警告没有默认时长
        );
        
        add_penalty_type_internal(
            &mut penalty_system,
            PENALTY_TYPE_NO_DRAW,
            string::utf8(b"No Draw"),
            string::utf8(b"Forbidden from drawing cards"),
            24 * 60 * 60 * 1000 // 24小时
        );
        
        add_penalty_type_internal(
            &mut penalty_system,
            PENALTY_TYPE_NO_BATTLE,
            string::utf8(b"No Battle"),
            string::utf8(b"Forbidden from participating in battles"),
            48 * 60 * 60 * 1000 // 48小时
        );
        
        add_penalty_type_internal(
            &mut penalty_system,
            PENALTY_TYPE_BAN,
            string::utf8(b"Ban"),
            string::utf8(b"Banned from all activities"),
            7 * 24 * 60 * 60 * 1000 // 7天
        );
        
        transfer::share_object(penalty_system);
    }
    
    /// 添加惩罚类型（内部函数）
    fun add_penalty_type_internal(
        penalty_system: &mut PenaltySystem,
        id: u8,
        name: String,
        description: String,
        default_duration: u64
    ) {
        let penalty_type = PenaltyType {
            id,
            name,
            description,
            default_duration
        };
        
        vector::push_back(&mut penalty_system.penalty_types, penalty_type);
    }
    
    /// 添加惩罚类型（管理员功能）
    public entry fun add_penalty_type(
        penalty_system: &mut PenaltySystem,
        id: u8,
        name: vector<u8>,
        description: vector<u8>,
        default_duration: u64,
        ctx: &mut TxContext
    ) {
        // 检查调用者是否为管理员
        assert!(tx_context::sender(ctx) == penalty_system.admin, ENotAuthorized);
        
        add_penalty_type_internal(
            penalty_system,
            id,
            string::utf8(name),
            string::utf8(description),
            default_duration
        );
    }
    
    /// 应用惩罚
    public entry fun apply_penalty(
        penalty_system: &mut PenaltySystem,
        target: address,
        penalty_type: u8,
        reason: vector<u8>,
        duration: u64, // 毫秒，0表示使用默认时长，PERMANENT_PENALTY表示永久
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // 检查调用者是否为管理员
        assert!(tx_context::sender(ctx) == penalty_system.admin, ENotAuthorized);
        
        // 检查惩罚类型是否有效
        let type_valid = false;
        let default_duration = 0u64;
        
        let i = 0;
        let len = vector::length(&penalty_system.penalty_types);
        
        while (i < len) {
            let pt = vector::borrow(&penalty_system.penalty_types, i);
            if (pt.id == penalty_type) {
                type_valid = true;
                default_duration = pt.default_duration;
                break
            };
            i = i + 1;
        };
        
        assert!(type_valid, EInvalidPenaltyType);
        
        // 确定惩罚时长
        let actual_duration = if (duration == 0) {
            default_duration
        } else {
            duration
        };
        
        // 获取当前时间
        let current_time = clock::timestamp_ms(clock);
        
        // 计算结束时间（0表示永久）
        let end_time = if (duration == PERMANENT_PENALTY) {
            PERMANENT_PENALTY
        } else {
            current_time + actual_duration
        };
        
        // 创建惩罚记录
        let penalty_id = object::new(ctx);
        let penalty_record = PenaltyRecord {
            id: object::uid_to_inner(&penalty_id),
            penalty_type,
            reason: string::utf8(reason),
            start_time: current_time,
            end_time,
            revoked: false,
            issuer: tx_context::sender(ctx)
        };
        
        // 删除临时UID
        object::delete(penalty_id);
        
        // 添加惩罚记录
        if (!table::contains(&penalty_system.penalties, target)) {
            table::add(&mut penalty_system.penalties, target, vector::empty());
            table::add(&mut penalty_system.active_penalties, target, vector::empty());
        };
        
        let user_penalties = table::borrow_mut(&mut penalty_system.penalties, target);
        vector::push_back(user_penalties, penalty_record);
        
        let active_penalties = table::borrow_mut(&mut penalty_system.active_penalties, target);
        vector::push_back(active_penalties, penalty_record);
        
        // 更新总惩罚次数
        penalty_system.total_penalties = penalty_system.total_penalties + 1;
        
        // 发送惩罚事件
        event::emit(PenaltyApplied {
            penalty_id: penalty_record.id,
            target,
            penalty_type,
            reason: string::utf8(reason),
            start_time: current_time,
            end_time,
            issuer: tx_context::sender(ctx)
        });
    }
    
    /// 解除惩罚
    public entry fun revoke_penalty(
        penalty_system: &mut PenaltySystem,
        target: address,
        penalty_id: ID,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // 检查调用者是否为管理员
        assert!(tx_context::sender(ctx) == penalty_system.admin, ENotAuthorized);
        
        // 检查用户是否有惩罚记录
        assert!(table::contains(&penalty_system.penalties, target), EPenaltyNotFound);
        
        // 获取用户的惩罚记录
        let user_penalties = table::borrow_mut(&mut penalty_system.penalties, target);
        let active_penalties = table::borrow_mut(&mut penalty_system.active_penalties, target);
        
        // 查找并更新指定的惩罚记录
        let found = false;
        let penalty_type = 0u8;
        
        let i = 0;
        let len = vector::length(user_penalties);
        
        while (i < len && !found) {
            let penalty = vector::borrow_mut(user_penalties, i);
            if (penalty.id == penalty_id && !penalty.revoked) {
                penalty.revoked = true;
                penalty_type = penalty.penalty_type;
                found = true;
                break
            };
            i = i + 1;
        };
        
        assert!(found, EPenaltyNotFound);
        
        // 从活跃惩罚列表中移除
        let j = 0;
        let active_len = vector::length(active_penalties);
        
        while (j < active_len) {
            if (vector::borrow(active_penalties, j).id == penalty_id) {
                vector::remove(active_penalties, j);
                break
            };
            j = j + 1;
        };
        
        // 发送惩罚解除事件
        event::emit(PenaltyRevoked {
            penalty_id,
            target,
            penalty_type,
            revoke_time: clock::timestamp_ms(clock),
            revoker: tx_context::sender(ctx)
        });
    }
    
    /// 清理过期惩罚
    public entry fun clean_expired_penalties(
        penalty_system: &mut PenaltySystem,
        target: address,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        // 任何人都可以调用此函数清理过期惩罚
        
        // 检查用户是否有惩罚记录
        if (!table::contains(&penalty_system.active_penalties, target)) {
            return
        };
        
        // 获取当前时间
        let current_time = clock::timestamp_ms(clock);
        
        // 获取用户的活跃惩罚记录
        let active_penalties = table::borrow_mut(&mut penalty_system.active_penalties, target);
        
        // 移除所有过期的惩罚
        let i = 0;
        while (i < vector::length(active_penalties)) {
            let penalty = vector::borrow(active_penalties, i);
            
            // 如果惩罚已过期（结束时间不为0且小于当前时间）
            if (penalty.end_time != PERMANENT_PENALTY && penalty.end_time < current_time) {
                // 从活跃惩罚列表中移除
                vector::remove(active_penalties, i);
                
                // 更新用户惩罚记录中的状态
                let user_penalties = table::borrow_mut(&mut penalty_system.penalties, target);
                let j = 0;
                let len = vector::length(user_penalties);
                
                while (j < len) {
                    let p = vector::borrow_mut(user_penalties, j);
                    if (p.id == penalty.id) {
                        p.revoked = true;
                        break
                    };
                    j = j + 1;
                };
                
                // 发送惩罚解除事件
                event::emit(PenaltyRevoked {
                    penalty_id: penalty.id,
                    target,
                    penalty_type: penalty.penalty_type,
                    revoke_time: current_time,
                    revoker: tx_context::sender(ctx)
                });
            } else {
                // 只有当前元素没有被移除时才递增i
                i = i + 1;
            }
        };
    }
    
    /// 检查用户是否有指定类型的活跃惩罚
    public fun has_active_penalty(
        penalty_system: &PenaltySystem,
        user: address,
        penalty_type: u8,
        clock: &Clock
    ): bool {
        // 如果用户没有惩罚记录，直接返回false
        if (!table::contains(&penalty_system.active_penalties, user)) {
            return false
        };
        
        // 获取当前时间
        let current_time = clock::timestamp_ms(clock);
        
        // 获取用户的活跃惩罚记录
        let active_penalties = table::borrow(&penalty_system.active_penalties, user);
        
        // 检查是否有指定类型的活跃惩罚
        let i = 0;
        let len = vector::length(active_penalties);
        
        while (i < len) {
            let penalty = vector::borrow(active_penalties, i);
            
            // 如果找到指定类型的惩罚，且未过期
            if (penalty.penalty_type == penalty_type && 
                (penalty.end_time == PERMANENT_PENALTY || penalty.end_time > current_time)) {
                return true
            };
            
            i = i + 1;
        };
        
        false
    }
    
    /// 检查用户是否有任何活跃惩罚
    public fun has_any_active_penalty(
        penalty_system: &PenaltySystem,
        user: address,
        clock: &Clock
    ): bool {
        // 如果用户没有惩罚记录，直接返回false
        if (!table::contains(&penalty_system.active_penalties, user)) {
            return false
        };
        
        // 获取当前时间
        let current_time = clock::timestamp_ms(clock);
        
        // 获取用户的活跃惩罚记录
        let active_penalties = table::borrow(&penalty_system.active_penalties, user);
        
        // 检查是否有任何活跃惩罚
        let i = 0;
        let len = vector::length(active_penalties);
        
        while (i < len) {
            let penalty = vector::borrow(active_penalties, i);
            
            // 如果找到未过期的惩罚
            if (penalty.end_time == PERMANENT_PENALTY || penalty.end_time > current_time) {
                return true
            };
            
            i = i + 1;
        };
        
        false
    }
    
    /// 获取用户惩罚记录数量
    public fun get_penalty_count(
        penalty_system: &PenaltySystem,
        user: address
    ): u64 {
        if (!table::contains(&penalty_system.penalties, user)) {
            0
        } else {
            vector::length(table::borrow(&penalty_system.penalties, user))
        }
    }
    
    /// 获取用户活跃惩罚记录数量
    public fun get_active_penalty_count(
        penalty_system: &PenaltySystem,
        user: address
    ): u64 {
        if (!table::contains(&penalty_system.active_penalties, user)) {
            0
        } else {
            vector::length(table::borrow(&penalty_system.active_penalties, user))
        }
    }
    
    /// 获取总惩罚数量
    public fun get_total_penalties(penalty_system: &PenaltySystem): u64 {
        penalty_system.total_penalties
    }
    
    /// 获取惩罚类型数量
    public fun get_penalty_type_count(penalty_system: &PenaltySystem): u64 {
        vector::length(&penalty_system.penalty_types)
    }
    
    /// 获取惩罚类型信息
    public fun get_penalty_type_info(
        penalty_system: &PenaltySystem,
        index: u64
    ): (u8, String, String, u64) {
        assert!(index < vector::length(&penalty_system.penalty_types), EInvalidPenaltyType);
        
        let penalty_type = vector::borrow(&penalty_system.penalty_types, index);
        (
            penalty_type.id,
            penalty_type.name,
            penalty_type.description,
            penalty_type.default_duration
        )
    }
}