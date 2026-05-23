from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_PATH = 'timber_ember.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Categories data dictionary to populate pages and validation
CATEGORIES_DATA = {
    'tables': {
        'id': 'tables',
        'title': 'Custom Dining & Coffee Tables',
        'tagline': 'Heirloom-quality tables crafted to anchor your space for generations.',
        'hero_image': 'table_walnut.png',
        'description': 'Every table is a unique piece of art. Hand-selected slabs, robust traditional joinery, and premium finishes come together to create a stunning centerpiece for your dining room, office, or living area. We offer live-edge, clean-cut, round, and conference tables tailored precisely to your dimensions.',
        'wood_options': [
            {'name': 'Black Walnut', 'price_factor': 1.5, 'description': 'Rich dark brown tones with swirly, dramatic grain. The gold standard of hardwoods.'},
            {'name': 'White Oak', 'price_factor': 1.2, 'description': 'Exceptional durability with a clean, straight grain and neutral honey hues.'},
            {'name': 'Hard Maple', 'price_factor': 1.0, 'description': 'Bright, cream-colored, and incredibly dense. Best for sleek modern designs.'},
            {'name': 'Wild Cherry', 'price_factor': 1.1, 'description': 'Warm reddish-pink tones that darken beautifully with age and sunlight exposure.'}
        ],
        'details': [
            'Sourced from local, sustainably harvested timber',
            'Kiln-dried to 6-8% moisture content to prevent wrapping or cracking',
            'Finished with natural, VOC-free hardwax oils or commercial-grade matte polyurethane',
            'Supported by custom-fabricated solid steel or matching hardwood bases'
        ],
        'base_price': 1200
    },
    'cutting-boards': {
        'id': 'cutting-boards',
        'title': 'Artisanal End-Grain Cutting Boards',
        'tagline': 'Premium culinary workspaces designed to preserve your knife edges and elevate your kitchen.',
        'hero_image': 'board_cherry.png',
        'description': 'Our cutting boards are crafted using end-grain construction—the preferred surface of professional chefs. By aligning the wood fibers vertically, end-grain boards allow knife blades to slide between fibers rather than cutting through them, keeping your blades sharp and keeping the board pristine for decades.',
        'wood_options': [
            {'name': 'Walnut & Cherry Blend', 'price_factor': 1.3, 'description': 'Stunning dark and reddish-warm geometric patterns.'},
            {'name': 'Maple & Walnut Grid', 'price_factor': 1.2, 'description': 'High-contrast checkerboard style for a modern culinary aesthetic.'},
            {'name': 'Classic Hard Maple', 'price_factor': 1.0, 'description': 'Pure, durable, and naturally antimicrobial maple blocks.'},
            {'name': 'Trio Block (Maple/Walnut/Cherry)', 'price_factor': 1.4, 'description': 'A complex, multi-toned geometric design showcasing three gorgeous timbers.'}
        ],
        'details': [
            'True end-grain construction for maximum durability and knife protection',
            'Assembled with FDA-approved, food-safe waterproof glue',
            'Includes deep juice grooves, carved finger grips, and non-slip rubber feet',
            'Pre-conditioned with food-grade mineral oil and organic beeswax'
        ],
        'base_price': 120
    },
    'saunas': {
        'id': 'saunas',
        'title': 'Custom Cedar Saunas',
        'tagline': 'Personal backyard sanctuaries engineered for thermal excellence and deep relaxation.',
        'hero_image': 'sauna_cedar.png',
        'description': 'Transform your home wellness routine with a bespoke outdoor or indoor sauna. Constructed from aromatic Western Red Cedar, our saunas are available in barrel, cabin, or custom styles. Designed with premium insulation, safety glass, and your choice of wood-burning or electric heating elements, they offer a lifetime of rejuvenation.',
        'wood_options': [
            {'name': 'Western Red Cedar (Knotty)', 'price_factor': 1.0, 'description': 'Aromatic, highly moisture-resistant, and rich in rustic cedar characters.'},
            {'name': 'Clear Western Red Cedar (Select)', 'price_factor': 1.4, 'description': 'Premium grade without knots, providing a sleek, smooth, high-end design.'},
            {'name': 'Nordic Spruce & Cedar', 'price_factor': 0.9, 'description': 'Spruce walls with red cedar benches for an authentic Scandinavian tone.'}
        ],
        'details': [
            '100% natural, rot-resistant Western Red Cedar wood',
            'Tempered double-pane safety glass doors and windows',
            'Premium Harvia heaters (Finland) with built-in or digital controls',
            'Designed with ergonomic benches and integrated LED accent lighting'
        ],
        'base_price': 4800
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Here we just flash a message since it's a contact form, but we can log it
        flash(f"Thank you, {name}! Your message has been received. We will contact you at {email} soon.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/category/<name>')
def category(name):
    # Normalize name (replace underscores with hyphens if needed)
    name = name.lower()
    if name not in CATEGORIES_DATA:
        flash("Category not found.", "warning")
        return redirect(url_for('index'))
    return render_template('category.html', category=CATEGORIES_DATA[name])

@app.route('/configurator')
def configurator():
    selected_cat = request.args.get('category', 'tables')
    if selected_cat not in CATEGORIES_DATA:
        selected_cat = 'tables'
    return render_template('configurator.html', categories=CATEGORIES_DATA, selected_category=selected_cat)

@app.route('/submit_quote', methods=['POST'])
def submit_quote():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        category_id = request.form.get('category')
        wood_type = request.form.get('wood_type')
        dimensions = request.form.get('dimensions')
        finish = request.form.get('finish')
        
        # Get selected addons
        addons_list = request.form.getlist('addons')
        addons = ", ".join(addons_list) if addons_list else "None"
        
        # Get estimated price
        estimated_price_raw = request.form.get('estimated_price', '0')
        estimated_price = float(estimated_price_raw.replace('$', '').replace(',', '').strip())
        
        message = request.form.get('message', '')

        # Basic server-side validation
        if not all([name, email, phone, category_id, wood_type, dimensions, finish]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('configurator', category=category_id))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quotes (name, email, phone, category, wood_type, dimensions, finish, addons, estimated_price, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
        ''', (name, email, phone, category_id, wood_type, dimensions, finish, addons, estimated_price, message))
        
        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for('quote_success', quote_id=quote_id))

    except Exception as e:
        flash(f"An error occurred while submitting your request: {str(e)}", "error")
        return redirect(url_for('configurator'))

@app.route('/quote_success/<int:quote_id>')
def quote_success(quote_id):
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,)).fetchone()
    conn.close()
    
    if not quote:
        flash("Quote details not found.", "warning")
        return redirect(url_for('index'))
        
    # Get human-readable category name
    cat_title = CATEGORIES_DATA.get(quote['category'], {}).get('title', quote['category'])
    return render_template('quote_success.html', quote=quote, category_title=cat_title)

@app.route('/dashboard')
def dashboard():
    status_filter = request.args.get('status', 'All')
    category_filter = request.args.get('category', 'All')
    
    query = 'SELECT * FROM quotes'
    conditions = []
    params = []
    
    if status_filter != 'All':
        conditions.append('status = ?')
        params.append(status_filter)
        
    if category_filter != 'All':
        conditions.append('category = ?')
        params.append(category_filter)
        
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        
    query += ' ORDER BY created_at DESC'
    
    conn = get_db_connection()
    quotes = conn.execute(query, params).fetchall()
    conn.close()
    
    # Calculate some dashboard stats for premium dashboard feel
    conn = get_db_connection()
    total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    pending_quotes = conn.execute("SELECT COUNT(*) FROM quotes WHERE status = 'Pending'").fetchone()[0]
    approved_quotes = conn.execute("SELECT COUNT(*) FROM quotes WHERE status = 'In Progress'").fetchone()[0]
    total_value = conn.execute("SELECT SUM(estimated_price) FROM quotes WHERE status != 'Cancelled'").fetchone()[0] or 0
    conn.close()
    
    stats = {
        'total': total_quotes,
        'pending': pending_quotes,
        'in_progress': approved_quotes,
        'value': total_value
    }
    
    return render_template('dashboard.html', 
                           quotes=quotes, 
                           stats=stats, 
                           selected_status=status_filter, 
                           selected_category=category_filter,
                           categories_data=CATEGORIES_DATA)

@app.route('/dashboard/update_status/<int:quote_id>', methods=['POST'])
def update_status(quote_id):
    status = request.form.get('status')
    if status in ['Pending', 'In Progress', 'Completed', 'Cancelled']:
        conn = get_db_connection()
        conn.execute('UPDATE quotes SET status = ? WHERE id = ?', (status, quote_id))
        conn.commit()
        conn.close()
        flash(f"Quote #{quote_id} status updated to '{status}'.", "success")
    else:
        flash("Invalid status selected.", "error")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Running locally
    app.run(debug=True, port=5000)
