from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Database setup
def init_db():
    conn = sqlite3.connect('clicks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_agent TEXT,
            platform TEXT,
            redirect_url TEXT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            platform TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if platform column exists in links table, if not add it
    cursor.execute("PRAGMA table_info(links)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'platform' not in columns:
        cursor.execute('ALTER TABLE links ADD COLUMN platform TEXT DEFAULT "Web"')
        print("Added platform column to links table")
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Static login credentials
ADMIN_EMAIL = "adminqr@barabise.com"
ADMIN_PASSWORD = "BaraBise@2255"

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if 'logged_in' in session:
        return redirect(url_for('stats'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('stats'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/redirect')
def redirect_page():
    # Get all saved links from database
    conn = sqlite3.connect('clicks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, url, platform FROM links ORDER BY created_at DESC')
    links = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', links=links)

@app.route('/track', methods=['POST'])
def track_click():
    try:
        data = request.get_json()
        user_agent = data.get('user_agent', '')
        platform = data.get('platform', '')
        redirect_url = data.get('redirect_url', '')
        ip_address = request.remote_addr
        
        # Insert click data into database
        conn = sqlite3.connect('clicks.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clicks (user_agent, platform, redirect_url, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_agent, platform, redirect_url, ip_address))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/stats')
@login_required
def stats():
    try:
        conn = sqlite3.connect('clicks.db')
        cursor = conn.cursor()
        
        # Get total clicks
        cursor.execute('SELECT COUNT(*) FROM clicks')
        total_clicks = cursor.fetchone()[0]
        
        # Get clicks by platform
        cursor.execute('''
            SELECT platform, COUNT(*) as count 
            FROM clicks 
            GROUP BY platform 
            ORDER BY count DESC
        ''')
        platform_stats = cursor.fetchall()
        
        # Get recent clicks with pagination
        page = request.args.get('page', 1, type=int)
        per_page = 5
        offset = (page - 1) * per_page
        
        cursor.execute('''
            SELECT platform, redirect_url, timestamp 
            FROM clicks 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        recent_clicks = cursor.fetchall()
        
        # Get total count for pagination
        cursor.execute('SELECT COUNT(*) FROM clicks')
        total_clicks_count = cursor.fetchone()[0]
        total_pages = (total_clicks_count + per_page - 1) // per_page
        
        # Get all saved links
        cursor.execute('SELECT id, name, url, platform, created_at FROM links ORDER BY created_at DESC')
        saved_links = cursor.fetchall()
        
        # Get platform-specific click counts
        cursor.execute('''
            SELECT platform, COUNT(*) as count 
            FROM clicks 
            WHERE platform IN ('Android', 'iOS', 'Desktop/Other')
            GROUP BY platform
        ''')
        platform_click_counts = cursor.fetchall()
        
        # Get link-specific click counts
        cursor.execute('''
            SELECT redirect_url, platform, COUNT(*) as count 
            FROM clicks 
            GROUP BY redirect_url, platform
            ORDER BY count DESC
        ''')
        link_click_counts = cursor.fetchall()
        
        conn.close()
        
        return render_template('stats.html', 
                             total_clicks=total_clicks,
                             platform_stats=platform_stats,
                             recent_clicks=recent_clicks,
                             saved_links=saved_links,
                             platform_click_counts=platform_click_counts,
                             link_click_counts=link_click_counts,
                             user_email=session.get('email', ''),
                             current_page=page,
                             total_pages=total_pages,
                             total_clicks_count=total_clicks_count)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/add_link', methods=['POST'])
@login_required
def add_link():
    try:
        name = request.form['name']
        url = request.form['url']
        platform = request.form['platform']
        
        if not name or not url or not platform:
            flash('Name, URL, and platform are required.', 'error')
            return redirect(url_for('stats'))
        
        conn = sqlite3.connect('clicks.db')
        cursor = conn.cursor()
        
        # Check if we already have 3 links
        cursor.execute('SELECT COUNT(*) FROM links')
        link_count = cursor.fetchone()[0]
        
        if link_count >= 3:
            flash('Maximum 3 links allowed. Please delete a link first.', 'error')
            conn.close()
            return redirect(url_for('stats'))
        
        cursor.execute('INSERT INTO links (name, url, platform) VALUES (?, ?, ?)', (name, url, platform))
        conn.commit()
        conn.close()
        
        flash('Link added successfully!', 'success')
        return redirect(url_for('stats'))
    except Exception as e:
        flash(f'Error adding link: {str(e)}', 'error')
        return redirect(url_for('stats'))

@app.route('/delete_link/<int:link_id>')
@login_required
def delete_link(link_id):
    try:
        conn = sqlite3.connect('clicks.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM links WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()
        
        flash('Link deleted successfully!', 'success')
        return redirect(url_for('stats'))
    except Exception as e:
        flash(f'Error deleting link: {str(e)}', 'error')
        return redirect(url_for('stats'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
