"""
路由监控系统集成示例
展示如何在现有的Flask应用中集成路由监控功能

重点：批量装饰器应用 - 无需手动为每个函数添加装饰器！

使用方法：
1. 导入监控模块
2. 定义需要监控的路由列表
3. 批量应用装饰器
4. 可选择性地添加全局监控

"""

# ========================================
# 方法1：批量装饰器应用（强烈推荐） 
# ========================================

from monitor import monitor_request, get_request_id, get_statistics_summary
from routes import register_routes

# 在 dpflask.py 文件末尾添加以下代码：

# 第一步：定义需要监控的路由函数名列表
MONITORED_ROUTES = [
    # DeepSeek相关接口
    'deepseek_request',              # 主要接口
    'deepseek_public_key',           # 获取公钥接口
    'deepseek_update',               # 更新日志接口
    'deepseek_feedback',             # 客户端反馈接口
    'deepseek_chat_history',         # 加载历史记录接口
    'deepseek_client_id_save_user_info',     # 存储client id
    'deepseek_client_id_auth_user_info',     # 校检client id
    
    # 生意参谋相关接口
    'sycm_access_control_info',      # 访问控制信息
    'sycm_load_userinfo',            # 用户信息加载
    'sycm_list_database',            # 数据库列表
    'sycm_list_tables',              # 数据表列表
    'sycm_view_table',               # 查看表数据
]

# 第二步：批量应用监控装饰器的函数
def apply_monitor_to_routes(app_globals, route_names):
    """
    为指定的路由函数批量添加监控装饰器
    
    优势：
    - 无需手动修改每个函数
    - 统一管理监控配置
    - 避免遗漏或重复
    - 便于维护
    """
    applied_count = 0
    skipped_count = 0
    
    print("🚀 开始批量应用监控装饰器...")
    
    for route_name in route_names:
        if route_name in app_globals and callable(app_globals[route_name]):
            # 检查是否已经添加过监控装饰器
            if not hasattr(app_globals[route_name], '_is_monitored'):
                # 应用监控装饰器
                app_globals[route_name] = monitor_request(app_globals[route_name])
                app_globals[route_name]._is_monitored = True
                applied_count += 1
                print(f"  ✅ 已为 {route_name} 添加监控")
            else:
                skipped_count += 1
                print(f"  ⚠️  {route_name} 已经有监控装饰器，跳过")
        else:
            print(f"  ❌ 未找到函数: {route_name}")
    
    print(f"📊 批量装饰器应用完成：")
    print(f"  - 成功添加: {applied_count} 个")
    print(f"  - 已存在跳过: {skipped_count} 个")
    print(f"  - 总计处理: {len(route_names)} 个")

# 第三步：执行批量应用（在 dpflask.py 文件最后添加）
"""
# 批量应用监控装饰器
apply_monitor_to_routes(globals(), MONITORED_ROUTES)

# 注册管理界面路由
register_routes(app)

print("🎯 路由监控系统初始化完成！")
"""

# ========================================
# 方法2：按模式自动应用（更智能）
# ========================================

def auto_apply_monitor_by_pattern(app_globals, pattern_prefixes=None, exclude_patterns=None):
    """
    根据函数名模式自动添加监控装饰器
    
    Args:
        pattern_prefixes: 匹配的函数名前缀，如 ['deepseek_', 'sycm_']
        exclude_patterns: 排除的模式，如 ['_test', '_internal']
    """
    if pattern_prefixes is None:
        pattern_prefixes = ['deepseek_', 'sycm_', 'api_']
    
    if exclude_patterns is None:
        exclude_patterns = ['_test', '_internal', '_helper', '_debug']
    
    applied_count = 0
    
    print("🔍 开始自动扫描并应用监控装饰器...")
    
    for name, obj in app_globals.items():
        # 检查是否为函数且符合命名模式
        if callable(obj) and any(name.startswith(prefix) for prefix in pattern_prefixes):
            # 检查是否需要排除
            if any(exclude in name for exclude in exclude_patterns):
                print(f"  🚫 跳过排除的函数: {name}")
                continue
                
            # 检查是否已经有监控装饰器
            if not hasattr(obj, '_is_monitored'):
                app_globals[name] = monitor_request(obj)
                app_globals[name]._is_monitored = True
                applied_count += 1
                print(f"  ✅ 自动为 {name} 添加监控")
    
    print(f"🎯 自动扫描完成，为 {applied_count} 个路由添加了监控")

# 使用自动模式的示例：
"""
# 自动为所有以 deepseek_ 和 sycm_ 开头的函数添加监控
auto_apply_monitor_by_pattern(globals(), 
    pattern_prefixes=['deepseek_', 'sycm_'],
    exclude_patterns=['_test', '_internal', '_debug']
)
"""

# ========================================
# 方法3：环境感知的监控配置（生产级）
# ========================================

import os

class MonitorConfig:
    """监控配置管理类 - 根据环境应用不同的监控策略"""
    
    # 核心业务接口（所有环境都监控）
    CRITICAL_ROUTES = [
        'deepseek_request',
        'sycm_list_database',
        'sycm_view_table',
    ]
    
    # 重要接口（生产和测试环境监控）
    IMPORTANT_ROUTES = [
        'deepseek_public_key',
        'deepseek_chat_history',
        'sycm_load_userinfo',
        'sycm_list_tables',
    ]
    
    # 辅助接口（仅生产环境监控）
    AUXILIARY_ROUTES = [
        'deepseek_update',
        'deepseek_feedback',
        'sycm_access_control_info',
        'deepseek_client_id_save_user_info',
        'deepseek_client_id_auth_user_info',
    ]
    
    @classmethod
    def apply_monitoring(cls, app_globals, environment=None):
        """
        根据环境应用相应的监控策略
        
        Args:
            environment: 'production', 'staging', 'development' 或 None（自动检测）
        """
        if environment is None:
            environment = os.getenv('FLASK_ENV', 'development')
        
        routes_to_monitor = []
        
        # 根据环境确定监控范围
        if environment == 'production':
            routes_to_monitor.extend(cls.CRITICAL_ROUTES)
            routes_to_monitor.extend(cls.IMPORTANT_ROUTES)
            routes_to_monitor.extend(cls.AUXILIARY_ROUTES)
            print("🔥 生产环境：启用完整监控")
            
        elif environment == 'staging':
            routes_to_monitor.extend(cls.CRITICAL_ROUTES)
            routes_to_monitor.extend(cls.IMPORTANT_ROUTES)
            print("🧪 测试环境：启用重要接口监控")
            
        else:  # development
            routes_to_monitor.extend(cls.CRITICAL_ROUTES)
            print("🔧 开发环境：仅监控核心接口")
        
        # 应用监控
        apply_monitor_to_routes(app_globals, routes_to_monitor)
        print(f"📊 {environment} 环境监控配置已应用")

# 环境感知监控的使用示例：
"""
# 在 dpflask.py 文件末尾添加：

# 根据环境自动应用监控配置
MonitorConfig.apply_monitoring(globals())

# 手动指定环境
# MonitorConfig.apply_monitoring(globals(), 'production')

# 注册管理界面
register_routes(app)
"""

# ========================================
# 方法4：带条件的智能监控（高级用法）
# ========================================

def conditional_monitor_routes(app_globals, route_conditions):
    """
    根据条件应用监控装饰器
    
    Args:
        route_conditions: 字典，格式为 {函数名: 条件函数}
    """
    applied_count = 0
    
    for route_name, condition_func in route_conditions.items():
        if route_name in app_globals and callable(app_globals[route_name]):
            if condition_func():
                if not hasattr(app_globals[route_name], '_is_monitored'):
                    app_globals[route_name] = monitor_request(app_globals[route_name])
                    app_globals[route_name]._is_monitored = True
                    applied_count += 1
                    print(f"  ✅ 条件满足，为 {route_name} 添加监控")
                else:
                    print(f"  ⚠️  {route_name} 已有监控装饰器")
            else:
                print(f"  🚫 条件不满足，跳过 {route_name}")
    
    print(f"🎯 条件监控应用完成，处理了 {applied_count} 个路由")

# 条件监控示例：
"""
# 定义条件函数
def is_production():
    return os.getenv('FLASK_ENV') == 'production'

def is_debug_enabled():
    return os.getenv('DEBUG', '').lower() == 'true'

# 定义条件监控规则
CONDITIONAL_ROUTES = {
    'deepseek_request': lambda: True,  # 总是监控
    'deepseek_update': is_production,  # 仅生产环境监控
    'sycm_view_table': is_production,  # 仅生产环境监控
    'debug_endpoint': is_debug_enabled,  # 仅调试模式监控
}

# 应用条件监控
conditional_monitor_routes(globals(), CONDITIONAL_ROUTES)
"""

# ========================================
# 完整的集成示例代码
# ========================================

COMPLETE_INTEGRATION_EXAMPLE = '''
# ================================================
# 在 dpflask.py 文件末尾添加以下完整代码
# ================================================

# 1. 导入监控模块
from route.monitor import monitor_request, get_request_id, get_statistics_summary
from route.routes import register_routes
import os

# 2. 批量装饰器应用函数
def apply_monitor_to_routes(app_globals, route_names):
    """批量为路由函数添加监控装饰器"""
    applied_count = 0
    for route_name in route_names:
        if route_name in app_globals and callable(app_globals[route_name]):
            if not hasattr(app_globals[route_name], '_is_monitored'):
                app_globals[route_name] = monitor_request(app_globals[route_name])
                app_globals[route_name]._is_monitored = True
                applied_count += 1
                print(f"✅ 已为 {route_name} 添加监控")
    print(f"🎯 总计为 {applied_count} 个路由添加了监控")

# 3. 定义需要监控的路由列表
MONITORED_ROUTES = [
    'deepseek_request',
    'deepseek_public_key', 
    'deepseek_chat_history',
    'sycm_list_database',
    'sycm_view_table',
    # 根据需要添加更多路由
]

# 4. 应用监控
print("🚀 正在初始化路由监控系统...")
apply_monitor_to_routes(globals(), MONITORED_ROUTES)

# 5. 注册管理界面
register_routes(app)

# 6. 完成提示
current_env = os.getenv('FLASK_ENV', 'development')
print(f"✨ 路由监控系统初始化完成！")
print(f"🔧 当前环境: {current_env}")
print(f"📊 管理界面: http://localhost:5000/admin/monitor/dashboard")

# 可选：添加一些简单的管理接口
@app.route('/admin/monitor/stats', methods=['GET'])
def get_monitor_stats():
    """获取监控统计信息"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = get_statistics_summary(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        }), 500
'''

# ========================================
# 总结说明
# ========================================

print("""
🎯 批量装饰器的核心优势：

1. ✅ 无需手动修改每个函数定义
   - 原始函数保持不变
   - 所有装饰器在一个地方统一管理

2. ✅ 灵活的监控策略
   - 可以根据环境启用不同的监控范围
   - 支持条件性监控
   - 便于测试和调试

3. ✅ 维护性强
   - 新增监控只需在列表中添加函数名
   - 移除监控只需从列表中删除
   - 避免在代码中到处添加装饰器

4. ✅ 性能优化
   - 避免重复装饰
   - 自动检测已有装饰器
   - 支持条件性启用

📋 推荐使用方式：
- 开发阶段：使用方法1（明确的函数名列表）
- 生产环境：使用方法3（环境感知配置）
- 大型项目：结合多种方法，分模块管理

🔧 集成步骤：
1. 复制 COMPLETE_INTEGRATION_EXAMPLE 中的代码
2. 添加到 dpflask.py 文件末尾
3. 根据需要调整 MONITORED_ROUTES 列表
4. 重启应用即可生效

这样就实现了批量添加监控装饰器，无需手动修改每个函数！
""")

if __name__ == "__main__":
    print(COMPLETE_INTEGRATION_EXAMPLE) 