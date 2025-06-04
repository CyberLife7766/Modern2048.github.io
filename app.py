from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash # Import additional Flask modules
from _2048 import Game2048
import os # Import os for secret key
import sqlite3
import uuid
from datetime import datetime
from functools import wraps
import requests
import user_agents  # 用于解析User-Agent

app = Flask(__name__)
app.secret_key = 'windsurf_2048_secret_key' # 使用固定的密钥，避免重启后session失效
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # session有效期为1天
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'windsurf_'

# 管理码
ADMIN_CODE = '!@#$%^'

# 数据库初始化
def get_db_connection():
    conn = sqlite3.connect('game_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# 创建数据库表
def init_db():
    conn = get_db_connection()
    
    # 检查是否需要迁移数据
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game_stats'")
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        # 检查是否需要添加新列
        cursor.execute('PRAGMA table_info(game_stats)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'country' not in columns:
            # 备份旧数据
            conn.execute('CREATE TABLE IF NOT EXISTS game_stats_backup AS SELECT * FROM game_stats')
            
            # 删除旧表并创建新表
            conn.execute('DROP TABLE game_stats')
            
            # 创建新表
            conn.execute('''
            CREATE TABLE game_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                board_size INTEGER NOT NULL,
                target_tile INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                country TEXT,
                region TEXT,
                os TEXT,
                browser TEXT
            )
            ''')
            
            # 恢复旧数据
            conn.execute('''
            INSERT INTO game_stats (id, device_id, score, board_size, target_tile, timestamp)
            SELECT id, device_id, score, board_size, target_tile, timestamp FROM game_stats_backup
            ''')
    else:
        # 创建新表
        conn.execute('''
        CREATE TABLE game_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            board_size INTEGER NOT NULL,
            target_tile INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            country TEXT,
            region TEXT,
            os TEXT,
            browser TEXT
        )
        ''')
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# Initialize game with default settings or from session if available
# This initial game instance will be used until a reset or new game is started
# based on user settings.
game = Game2048()

@app.route('/')
def index():
    # Retrieve settings from session or use defaults
    board_size = session.get('board_size', 4)
    target_tile_value = session.get('target_tile_value', 2048)
    
    global game
    # Re-initialize game with current session settings if not already set
    # or if the settings have changed since the last game instance.
    # This ensures the game always starts with the user's preferred settings.
    if not hasattr(game, 'board_size') or game.board_size != board_size or \
       not hasattr(game, 'target_tile_value') or game.target_tile_value != target_tile_value:
        game = Game2048(board_size=board_size, target_tile_value=target_tile_value)

    return render_template('index.html')

@app.route('/game_state', methods=['GET'])
def get_game_state():
    return jsonify(game.get_state())

@app.route('/move/<direction>', methods=['POST'])
def move(direction):
    if direction not in ['left', 'right', 'up', 'down']:
        return jsonify({'error': 'Invalid direction'}), 400
    
    moved = game.move(direction)
    game_state = game.get_state()
    
    # 如果游戏结束，记录游戏数据
    if game_state['game_over'] or game_state['won']:
        # 获取或创建设备ID
        if 'device_id' not in session:
            session['device_id'] = str(uuid.uuid4())
        
        # 获取IP地址
        ip_address = request.remote_addr
        country = None
        region = None
        
        # 获取位置信息（使用IP-API）
        try:
            ip_info = requests.get(f'http://ip-api.com/json/{ip_address}').json()
            if ip_info.get('status') == 'success':
                country = ip_info.get('country')
                region = ip_info.get('regionName')
        except Exception as e:
            print(f"获取位置信息失败: {e}")
        
        # 获取用户代理信息
        user_agent_string = request.headers.get('User-Agent', '')
        user_agent = user_agents.parse(user_agent_string)
        
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
        browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        
        # 保存游戏数据到数据库
        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO game_stats 
               (device_id, score, board_size, target_tile, timestamp, country, region, os, browser) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (session['device_id'], game.score, game.board_size, game.target_tile_value, 
             datetime.now(), country, region, os_info, browser_info)
        )
        conn.commit()
        conn.close()
    
    return jsonify(game_state)

@app.route('/reset', methods=['POST'])
def reset_game():
    global game
    # Get board_size and target_tile_value from request, with defaults
    board_size = request.json.get('board_size', 4)
    target_tile_value = request.json.get('target_tile_value', 2048)
    
    # Store settings in session for persistence across page loads
    session['board_size'] = board_size
    session['target_tile_value'] = target_tile_value

    # 使用 reset 方法而不是创建新实例
    game.reset(board_size=board_size, target_tile_value=target_tile_value)
    return jsonify(game.get_state())

@app.route('/settings')
def settings():
    return render_template('settings.html')

# 管理员验证装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 打印当前session状态用于调试
        print(f"验证管理员权限，当前session: {session}")
        if not session.get('admin_logged_in', False):
            print("管理员验证失败，重定向到登录页面")
            return redirect(url_for('admin_login'))
        print("管理员验证成功")
        return f(*args, **kwargs)
    return decorated_function

# 管理员登录页面
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    # 检查是否已登录
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        admin_code = request.form.get('admin_code')
        print(f"尝试登录，输入的管理码: {admin_code}")
        
        if admin_code == ADMIN_CODE:
            # 设置session
            session.clear()
            session['admin_logged_in'] = True
            # 强制保存session
            session.modified = True
            
            # 打印session信息用于调试
            print(f"设置session后: {session}")
            print("登录成功，重定向到仪表盘")
            
            return redirect(url_for('admin_dashboard'))
        else:
            print("管理码错误")
            flash('管理码错误')
    
    # 打印当前session状态
    print(f"当前session: {session}")
    return render_template('admin_login.html')

# 管理员退出
@app.route('/admin/logout')
def admin_logout():
    # 清除整个session而不只是单个键
    session.clear()
    session.modified = True
    print("管理员已登出")
    return redirect(url_for('admin_login'))

# 管理员仪表盘
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# 总体统计页面
@app.route('/admin/overall_stats')
@admin_required
def admin_overall_stats():
    conn = get_db_connection()
    
    # 获取总体统计数据
    stats = conn.execute('''
        SELECT COUNT(*) as total_games,
               MAX(score) as highest_score,
               AVG(score) as average_score,
               AVG(board_size) as avg_board_size,
               MAX(board_size) as max_board_size,
               MIN(board_size) as min_board_size,
               COUNT(DISTINCT device_id) as unique_devices
        FROM game_stats
    ''').fetchone()
    
    # 获取按月统计数据
    monthly_stats = conn.execute('''
        SELECT strftime('%Y-%m', timestamp) as month,
               COUNT(*) as games_count,
               AVG(score) as avg_score,
               MAX(score) as max_score
        FROM game_stats
        GROUP BY month
        ORDER BY month DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_overall_stats.html', stats=stats, monthly_stats=monthly_stats)

# 设备统计页面
@app.route('/admin/device_stats')
@admin_required
def admin_device_stats():
    conn = get_db_connection()
    
    # 获取设备统计数据（包含位置、系统和浏览器信息）
    devices = conn.execute('''
        SELECT device_id, 
               COUNT(*) as total_games, 
               MAX(score) as max_score, 
               AVG(score) as avg_score,
               MAX(timestamp) as last_played,
               country,
               region,
               os,
               browser
        FROM game_stats 
        GROUP BY device_id
        ORDER BY total_games DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_device_stats.html', devices=devices)

# 最近游戏记录页面
@app.route('/admin/recent_games')
@admin_required
def admin_recent_games():
    conn = get_db_connection()
    
    # 获取最近50场游戏
    recent_games = conn.execute('''
        SELECT * FROM game_stats 
        ORDER BY timestamp DESC LIMIT 50
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_recent_games.html', recent_games=recent_games)

if __name__ == '__main__':
    app.run(debug=True)
