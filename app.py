from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

app = Flask(__name__)
# Use environment variable for session secret key to remain stable in multi-instance containers
app.secret_key = os.environ.get("SESSION_SECRET_KEY", "timber-ember-default-secret-key-1289")

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
        flash(f"Thank you, {name}! Your message has been received. We will contact you at {email} soon.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/category/<name>')
def category(name):
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
        
        addons_list = request.form.getlist('addons')
        addons = ", ".join(addons_list) if addons_list else "None"
        
        estimated_price_raw = request.form.get('estimated_price', '0')
        estimated_price = float(estimated_price_raw.replace('$', '').replace(',', '').strip())
        
        message = request.form.get('message', '')

        if not all([name, email, phone, category_id, wood_type, dimensions, finish]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('configurator', category=category_id))

        # Store quote request specifications in client-side cookie session
        session['quote_data'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'category': category_id,
            'wood_type': wood_type,
            'dimensions': dimensions,
            'finish': finish,
            'addons': addons,
            'estimated_price': estimated_price,
            'message': message
        }

        return redirect(url_for('quote_success'))

    except Exception as e:
        flash(f"An error occurred while submitting your request: {str(e)}", "error")
        return redirect(url_for('configurator'))

@app.route('/quote_success')
def quote_success():
    quote = session.get('quote_data')
    if not quote:
        flash("No active quote request details found.", "warning")
        return redirect(url_for('index'))
        
    cat_title = CATEGORIES_DATA.get(quote['category'], {}).get('title', quote['category'])
    return render_template('quote_success.html', quote=quote, category_title=cat_title)

if __name__ == '__main__':
    # Cloud Run expects the app to bind to PORT environment variable, defaulting to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
