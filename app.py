from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import stripe
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
# Use environment variable for session secret key to remain stable in multi-instance containers
app.secret_key = os.environ.get("SESSION_SECRET_KEY")

# Get Stripe secret key
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
client = stripe.StripeClient(STRIPE_SECRET_KEY)

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

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Since the checkout form works asynchronously, we grab JSON data sent from the browser
        data = request.get_json() or {}
        
        # 1. Extract the unique woodworking specs from your interactive customizer
        category_id = data.get('category', 'tables')
        wood_type = data.get('wood_type', 'Unknown Species')
        dimensions = data.get('dimensions', 'Custom Dimensions')
        finish = data.get('finish', 'Standard Finish')
        addons = data.get('addons', 'None Selected')
        
        # 2. Get the customer details entered in the modal
        customer_name = data.get('name', 'Valued Patron')
        customer_email = data.get('email')
        customer_phone = data.get('phone', '')
        customer_message = data.get('message', '')
        
        # Extract the price string from the frontend (e.g., "$1,520.00"), clean it, and make it a float
        raw_price = data.get('estimated_price', '0')
        cleaned_price = float(raw_price.replace('$', '').replace(',', '').strip())
        
        # Stripe processes all transactions in the smallest currency unit (CENTS)
        # Example: $1,200.00 becomes 120000 cents
        unit_amount_cents = int(cleaned_price * 100)

        # Look up the human-readable product title from your CATEGORIES_DATA dictionary
        category_title = CATEGORIES_DATA.get(category_id, {}).get('title', 'Custom Furniture Build')

        # 3. Request the secure transaction wrapper from Stripe
        session = client.v1.checkout.sessions.create(
            params={
                'ui_mode': 'embedded_page', # Tells Stripe to embed right inside your site layout
                'mode': 'payment',           # Indicates a one-time purchase
                'customer_email': customer_email, # Pre-fills the customer's email in the form
                
                'line_items': [{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{category_title} ({wood_type})",
                            'description': f"Specs: {dimensions} | Finish: {finish}",
                        },
                        'unit_amount': unit_amount_cents,
                    },
                    'quantity': 1,
                }],
                
                # Automatically sets the return path using whatever domain your app runs on
                'return_url': request.host_url + 'checkout/return?session_id={CHECKOUT_SESSION_ID}',
                
                # CRITICAL STEP: Store your custom build requirements in Stripe's metadata.
                # This guarantees that the table dimensions are permanently linked to the receipt!
                'metadata': {
                    'customer_name': customer_name,
                    'customer_phone': customer_phone,
                    'category_id': category_id,
                    'wood_type': wood_type,
                    'dimensions': dimensions,
                    'finish': finish,
                    'addons': addons,
                    'workshop_notes': customer_message
                }
            },
        )
        
        # Return the client secret key to your JavaScript frontend
        return jsonify(clientSecret=session.client_secret)
        
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/quote_success')
def quote_success():
    quote = session.get('quote_data')
    if not quote:
        flash("No active quote request details found.", "warning")
        return redirect(url_for('index'))
        
    cat_title = CATEGORIES_DATA.get(quote['category'], {}).get('title', quote['category'])
    return render_template('quote_success.html', quote=quote, category_title=cat_title)

@app.route('/checkout/return')
def checkout_return():
    # 1. This endpoint simply serves up the clean return landing template page
    return render_template('return.html')

@app.route('/session-status', methods=['GET'])
def session_status():
    try:
        # 2. Extract the checkout session ID passed from the URL parameter query string
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify(error="Missing required session_id parameter"), 400
            
        # 3. Retrieve the official transaction state straight from Stripe's servers
        session = client.v1.checkout.sessions.retrieve(session_id)

        # Convert the entire Stripe object recursively into a standard Python dict
        session_dict = session.to_dict()
        
        # 4. Return the status, email, and the custom woodworking specifications metadata
        return jsonify(
            status=session.status, 
            customer_email=session.customer_details.email if session.customer_details else None,
            metadata=session_dict.get('metadata', {})
        )
    except Exception as e:
        print("❌ STRIPE ERROR LOG:", str(e))
        return jsonify(error=str(e)), 400

if __name__ == '__main__':
    # Cloud Run expects the app to bind to PORT environment variable, defaulting to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
