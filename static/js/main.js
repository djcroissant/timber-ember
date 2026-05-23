/* ==========================================================================
   TIMBER & EMBER CORE SCRIPT
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------------------------
    // 1. THEME SWITCHER LOGIC
    // ----------------------------------------------------------------------
    const themeToggle = document.getElementById('theme-toggle');
    
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('color-scheme', newTheme);
        document.querySelector('meta[name="color-scheme"]').setAttribute('content', newTheme);
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Listen for OS system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        // Only adapt if the user hasn't explicitly set a preference
        if (!localStorage.getItem('color-scheme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            document.querySelector('meta[name="color-scheme"]').setAttribute('content', newTheme);
        }
    });

    // ----------------------------------------------------------------------
    // 2. MOBILE NAVIGATION DRAWER
    // ----------------------------------------------------------------------
    const mobileNavToggle = document.getElementById('mobile-nav-toggle');
    const mobileNavDrawer = document.getElementById('mobile-nav-drawer');
    
    if (mobileNavToggle && mobileNavDrawer) {
        mobileNavToggle.addEventListener('click', () => {
            const isOpen = mobileNavDrawer.classList.contains('open');
            if (isOpen) {
                mobileNavDrawer.classList.remove('open');
                mobileNavToggle.setAttribute('aria-expanded', 'false');
                mobileNavDrawer.setAttribute('aria-hidden', 'true');
            } else {
                mobileNavDrawer.classList.add('open');
                mobileNavToggle.setAttribute('aria-expanded', 'true');
                mobileNavDrawer.setAttribute('aria-hidden', 'false');
            }
        });
        
        // Close drawer when clicking outside content area
        mobileNavDrawer.addEventListener('click', (e) => {
            if (e.target === mobileNavDrawer) {
                mobileNavDrawer.classList.remove('open');
                mobileNavToggle.setAttribute('aria-expanded', 'false');
                mobileNavDrawer.setAttribute('aria-hidden', 'true');
            }
        });
    }

    // ----------------------------------------------------------------------
    // 3. INTERACTIVE CONFIGURATOR ENGINE
    // ----------------------------------------------------------------------
    const configContainer = document.querySelector('.configurator-layout');
    
    if (configContainer) {
        // Configurator Pricing Engine State
        const CONFIG_DB = {
            'tables': {
                basePrice: 1200,
                woods: {
                    'Hard Maple': 1.0,
                    'Wild Cherry': 1.1,
                    'White Oak': 1.2,
                    'Black Walnut': 1.5
                },
                pricingRules: {
                    baseLength: 60,
                    lengthRate: 15, // $15 per inch over baseLength
                    baseWidth: 30,
                    widthRate: 20   // $20 per inch over baseWidth
                }
            },
            'cutting-boards': {
                basePrice: 120,
                woods: {
                    'Classic Hard Maple': 1.0,
                    'Maple & Walnut Grid': 1.2,
                    'Walnut & Cherry Blend': 1.3,
                    'Trio Block (Maple/Walnut/Cherry)': 1.4
                },
                pricingRules: {
                    baseLength: 12,
                    lengthRate: 8,
                    baseWidth: 8,
                    widthRate: 10
                }
            },
            'saunas': {
                basePrice: 4800,
                woods: {
                    'Nordic Spruce & Cedar': 0.9,
                    'Western Red Cedar (Knotty)': 1.0,
                    'Clear Western Red Cedar (Select)': 1.4
                },
                pricingRules: {
                    sizes: {
                        '2-Person Barrel': 0,
                        '4-Person Barrel': 1200,
                        '6-Person Barrel': 2200,
                        '8-Person Cabin': 3800
                    }
                }
            }
        };

        // DOM elements
        const tabButtons = document.querySelectorAll('.tab-btn');
        const woodOptionsGrid = document.getElementById('wood-options-grid');
        const dimensionsSection = document.getElementById('dimensions-section');
        const addonsList = document.getElementById('addons-list');
        const finishSelect = document.getElementById('finish-select');
        
        // Summary DOM elements
        const summaryCategory = document.getElementById('summary-category');
        const summaryWood = document.getElementById('summary-wood');
        const summarySize = document.getElementById('summary-size');
        const summaryFinish = document.getElementById('summary-finish');
        const summaryAddons = document.getElementById('summary-addons');
        const summaryPrice = document.getElementById('summary-price');
        
        // Modal & Form DOM elements
        const quoteModal = document.getElementById('quote-modal');
        const openModalBtn = document.getElementById('open-quote-modal');
        const closeModalBtn = document.getElementById('close-quote-modal');
        const modalForm = document.getElementById('modal-quote-form');
        
        // Hidden inputs in form to submit exact configurations
        const formCategory = document.getElementById('form-category');
        const formWood = document.getElementById('form-wood');
        const formDimensions = document.getElementById('form-dimensions');
        const formFinish = document.getElementById('form-finish');
        const formPrice = document.getElementById('form-price');

        // Current user selections state
        let currentCategory = new URLSearchParams(window.location.search).get('category') || 'tables';
        if (!CONFIG_DB[currentCategory]) currentCategory = 'tables';
        
        let currentWood = Object.keys(CONFIG_DB[currentCategory].woods)[0];
        let currentDimensions = {};
        let currentAddons = [];

        // Dynamic elements generator helpers
        function initCategory(cat) {
            currentCategory = cat;
            currentWood = Object.keys(CONFIG_DB[cat].woods)[0];
            currentAddons = [];
            
            // Highlight active tab
            tabButtons.forEach(btn => {
                if (btn.dataset.category === cat) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            // 1. Render Wood species choices
            woodOptionsGrid.innerHTML = '';
            Object.entries(CONFIG_DB[cat].woods).forEach(([woodName, factor], idx) => {
                const card = document.createElement('div');
                card.className = `wood-card ${woodName === currentWood ? 'selected' : ''}`;
                card.dataset.wood = woodName;
                card.innerHTML = `
                    <div class="wood-card-name">${woodName}</div>
                    <div class="wood-card-factor">×${factor.toFixed(1)} Base Rate</div>
                    <div class="wood-card-desc">${getWoodDescription(woodName)}</div>
                `;
                card.addEventListener('click', () => {
                    document.querySelectorAll('.wood-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    currentWood = woodName;
                    updatePrice();
                });
                woodOptionsGrid.appendChild(card);
            });

            // 2. Render dimensions (sliders or size selections)
            dimensionsSection.innerHTML = '';
            if (cat === 'tables') {
                currentDimensions = { length: 72, width: 36, height: 30 };
                dimensionsSection.innerHTML = `
                    <div class="dimension-control">
                        <div class="slider-header">
                            <span>Length (inches)</span>
                            <span id="len-val">72"</span>
                        </div>
                        <input type="range" id="slider-length" min="60" max="120" step="6" value="72" aria-label="Length in inches">
                    </div>
                    <div class="dimension-control">
                        <div class="slider-header">
                            <span>Width (inches)</span>
                            <span id="wid-val">36"</span>
                        </div>
                        <input type="range" id="slider-width" min="30" max="48" step="2" value="36" aria-label="Width in inches">
                    </div>
                    <div class="dimension-control">
                        <div class="slider-header">
                            <span>Height (inches)</span>
                            <span id="hgt-val">30" (Standard Dining)</span>
                        </div>
                        <input type="range" id="slider-height" min="16" max="42" step="2" value="30" aria-label="Height in inches">
                    </div>
                `;
                
                // Add event listeners
                document.getElementById('slider-length').addEventListener('input', (e) => {
                    currentDimensions.length = parseInt(e.target.value);
                    document.getElementById('len-val').textContent = e.target.value + '"';
                    updatePrice();
                });
                document.getElementById('slider-width').addEventListener('input', (e) => {
                    currentDimensions.width = parseInt(e.target.value);
                    document.getElementById('wid-val').textContent = e.target.value + '"';
                    updatePrice();
                });
                document.getElementById('slider-height').addEventListener('input', (e) => {
                    currentDimensions.height = parseInt(e.target.value);
                    let label = e.target.value + '"';
                    if (e.target.value == 30) label += " (Standard Dining)";
                    if (e.target.value == 18) label += " (Coffee Table)";
                    if (e.target.value == 42) label += " (Bar Height)";
                    document.getElementById('hgt-val').textContent = label;
                    updatePrice();
                });

            } else if (cat === 'cutting-boards') {
                currentDimensions = { length: 16, width: 12, thickness: 1.5 };
                dimensionsSection.innerHTML = `
                    <div class="dimension-control">
                        <div class="slider-header">
                            <span>Length (inches)</span>
                            <span id="len-val">16"</span>
                        </div>
                        <input type="range" id="slider-length" min="12" max="24" step="2" value="16" aria-label="Length in inches">
                    </div>
                    <div class="dimension-control">
                        <div class="slider-header">
                            <span>Width (inches)</span>
                            <span id="wid-val">12"</span>
                        </div>
                        <input type="range" id="slider-width" min="8" max="18" step="2" value="12" aria-label="Width in inches">
                    </div>
                    <div class="dimension-control">
                        <div class="slider-header">
                            <span>Thickness</span>
                            <span id="thick-val">1.5" Standard</span>
                        </div>
                        <input type="range" id="slider-thickness" min="1.5" max="2.5" step="0.5" value="1.5" aria-label="Thickness in inches">
                    </div>
                `;
                
                // Add event listeners
                document.getElementById('slider-length').addEventListener('input', (e) => {
                    currentDimensions.length = parseInt(e.target.value);
                    document.getElementById('len-val').textContent = e.target.value + '"';
                    updatePrice();
                });
                document.getElementById('slider-width').addEventListener('input', (e) => {
                    currentDimensions.width = parseInt(e.target.value);
                    document.getElementById('wid-val').textContent = e.target.value + '"';
                    updatePrice();
                });
                document.getElementById('slider-thickness').addEventListener('input', (e) => {
                    const val = parseFloat(e.target.value);
                    currentDimensions.thickness = val;
                    document.getElementById('thick-val').textContent = val.toFixed(1) + '"' + (val === 1.5 ? ' Standard' : ' Premium Block');
                    updatePrice();
                });

            } else if (cat === 'saunas') {
                currentDimensions = { sizeName: '4-Person Barrel' };
                dimensionsSection.innerHTML = `
                    <div class="form-group">
                        <label for="sauna-size-select">Select Sauna Model & Layout</label>
                        <select id="sauna-size-select" aria-label="Select Sauna size model">
                            <option value="2-Person Barrel">2-Person Compact Barrel (6ft diameter x 4ft length)</option>
                            <option value="4-Person Barrel" selected>4-Person Classic Barrel (6ft diameter x 6ft length)</option>
                            <option value="6-Person Barrel">6-Person Standard Barrel (6ft diameter x 8ft length)</option>
                            <option value="8-Person Cabin">8-Person Deluxe Cabin (8ft width x 8ft length Cabin)</option>
                        </select>
                    </div>
                `;
                
                document.getElementById('sauna-size-select').addEventListener('change', (e) => {
                    currentDimensions.sizeName = e.target.value;
                    updatePrice();
                });
            }

            // 3. Render finishes select dropdown choices
            finishSelect.innerHTML = '';
            let finishes = [];
            if (cat === 'tables') {
                finishes = [
                    'Satin Hardwax Oil (Water-resistant, natural look)',
                    'Matte Polyurethane (Maximum defense)',
                    'Gloss Polyurethane (Vibrant look)'
                ];
            } else if (cat === 'cutting-boards') {
                finishes = [
                    'Organic Mineral Oil & Beeswax Conditioner',
                    'Raw Pure Mineral Oil'
                ];
            } else if (cat === 'saunas') {
                finishes = [
                    'Natural Cedar Oil Treatment (Exterior only)',
                    'Unfinished / Raw Cedar Wood'
                ];
            }
            finishes.forEach(fin => {
                const opt = document.createElement('option');
                opt.value = fin.split(' (')[0];
                opt.textContent = fin;
                finishSelect.appendChild(opt);
            });

            // 4. Render addons list checkboxes
            addonsList.innerHTML = '';
            let addons = [];
            if (cat === 'tables') {
                addons = [
                    { id: 'live-edge', name: 'Natural Live Edge', price: 450, desc: 'Keep the natural outer tree contours on table edges.' },
                    { id: 'resin-fill', name: 'Epoxy Knot Fills', price: 200, desc: 'Fills knots/fissures with tinted structural epoxy.' },
                    { id: 'metal-base', name: 'Premium Metal Bases', price: 250, desc: 'Upgrade to heavy gauge steel legs instead of wood bases.' },
                    { id: 'bench', name: 'Matching Wood Bench', price: 400, desc: 'Adds a 3-seater matching dining bench.' }
                ];
            } else if (cat === 'cutting-boards') {
                addons = [
                    { id: 'juice-groove', name: 'Deep Juice Groove', price: 25, desc: 'Grooved border to collect juices.' },
                    { id: 'finger-grips', name: 'Carved Finger Grips', price: 15, desc: 'Recessed handles under edges.' },
                    { id: 'rubber-feet', name: 'Rubber Gripper Feet', price: 10, desc: 'Heavy duty screw-on feet preventing slipping.' },
                    { id: 'engraving', name: 'Laser Engraving / Monogram', price: 40, desc: 'Custom text or initials burned on surface.' }
                ];
            } else if (cat === 'saunas') {
                addons = [
                    { id: 'wood-heater', name: 'Harvia Wood-burning Stove Upgrade', price: 850, desc: 'Replace electric heater with traditional wood stove.' },
                    { id: 'window', name: 'Panoramic Half-Moon Window', price: 1100, desc: 'Rear wall double glazed viewing acrylic.' },
                    { id: 'shingles', name: 'Outdoor Shingle Roof Kit', price: 450, desc: 'Adds asphalt protective roof shingles.' },
                    { id: 'backrests', name: 'Ergonomic Bench Backrests', price: 250, desc: 'Provides contoured red cedar back slats.' }
                ];
            }
            
            addons.forEach(add => {
                const wrapper = document.createElement('label');
                wrapper.className = 'checkbox-label';
                wrapper.innerHTML = `
                    <input type="checkbox" name="addons-check" value="${add.name}" data-price="${add.price}">
                    <div class="option-info">
                        <span class="option-name">${add.name}</span>
                        <span class="option-desc">${add.desc}</span>
                    </div>
                    <span class="option-price">+$${add.price}</span>
                `;
                
                wrapper.querySelector('input').addEventListener('change', (e) => {
                    const isChecked = e.target.checked;
                    if (isChecked) {
                        currentAddons.push({ name: add.name, price: add.price });
                    } else {
                        currentAddons = currentAddons.filter(a => a.name !== add.name);
                    }
                    updatePrice();
                });
                
                addonsList.appendChild(wrapper);
            });

            updatePrice();
        }

        function getWoodDescription(wood) {
            const descMap = {
                'Black Walnut': 'Rich chocolate tones, swirly grain.',
                'White Oak': 'Durable, honey-colored wheat hues.',
                'Hard Maple': 'Clean, bright, exceptionally dense.',
                'Wild Cherry': 'Warm, amber-pink grain that darkens.',
                'Classic Hard Maple': 'Durable and highly hygienic.',
                'Maple & Walnut Grid': 'A high-contrast grid pattern.',
                'Walnut & Cherry Blend': 'Warm contrasting stripes.',
                'Trio Block (Maple/Walnut/Cherry)': '3-tone end grain mosaic.',
                'Nordic Spruce & Cedar': 'Affordable spruce walls + cedar benches.',
                'Western Red Cedar (Knotty)': 'Highly aromatic, rot-resistant.',
                'Clear Western Red Cedar (Select)': 'Sleek, knot-free selected boards.'
            };
            return descMap[wood] || 'Premium grade construction material.';
        }

        function updatePrice() {
            let basePrice = CONFIG_DB[currentCategory].basePrice;
            let sizeCost = 0;
            let sizeStr = '';
            
            // Sizing Pricing Calculations
            if (currentCategory === 'tables') {
                const rules = CONFIG_DB['tables'].pricingRules;
                const lenOver = Math.max(0, currentDimensions.length - rules.baseLength);
                const widOver = Math.max(0, currentDimensions.width - rules.baseWidth);
                sizeCost = (lenOver * rules.lengthRate) + (widOver * rules.widthRate);
                sizeStr = `${currentDimensions.length}"L × ${currentDimensions.width}"W × ${currentDimensions.height}"H`;
            } else if (currentCategory === 'cutting-boards') {
                const rules = CONFIG_DB['cutting-boards'].pricingRules;
                const lenOver = Math.max(0, currentDimensions.length - rules.baseLength);
                const widOver = Math.max(0, currentDimensions.width - rules.baseWidth);
                let thickCost = 0;
                if (currentDimensions.thickness === 2.0) thickCost = 30;
                if (currentDimensions.thickness === 2.5) thickCost = 60;
                
                sizeCost = (lenOver * rules.lengthRate) + (widOver * rules.widthRate) + thickCost;
                sizeStr = `${currentDimensions.length}"L × ${currentDimensions.width}"W × ${currentDimensions.thickness.toFixed(1)}"T`;
            } else if (currentCategory === 'saunas') {
                const sizes = CONFIG_DB['saunas'].pricingRules.sizes;
                sizeCost = sizes[currentDimensions.sizeName] || 0;
                sizeStr = currentDimensions.sizeName;
            }

            // Wood Multiplier
            const woodFactor = CONFIG_DB[currentCategory].woods[currentWood] || 1.0;
            
            // Addons Pricing Sum
            const addonsTotal = currentAddons.reduce((sum, item) => sum + item.price, 0);
            
            // Combined Calculation
            const finalEstimate = (basePrice + sizeCost) * woodFactor + addonsTotal;
            
            // Update Summary Display
            summaryCategory.textContent = currentCategory.charAt(0).toUpperCase() + currentCategory.slice(1).replace('-', ' ');
            summaryWood.textContent = currentWood;
            summarySize.textContent = sizeStr;
            summaryFinish.textContent = finishSelect.value;
            
            if (currentAddons.length > 0) {
                summaryAddons.innerHTML = currentAddons.map(a => `<li>${a.name} (+$${a.price})</li>`).join('');
            } else {
                summaryAddons.innerHTML = '<li>No addons selected</li>';
            }
            
            summaryPrice.textContent = `$${finalEstimate.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

            // Sync selections to hidden fields for Form submissions
            formCategory.value = currentCategory;
            formWood.value = currentWood;
            formDimensions.value = sizeStr;
            formFinish.value = finishSelect.value;
            formPrice.value = `$${finalEstimate.toFixed(2)}`;
        }

        // Add action listeners to Category tabs
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                initCategory(btn.dataset.category);
            });
        });
        
        finishSelect.addEventListener('change', updatePrice);

        // Modal triggers
        if (openModalBtn && quoteModal && closeModalBtn) {
            openModalBtn.addEventListener('click', () => {
                quoteModal.classList.add('open');
                quoteModal.setAttribute('aria-hidden', 'false');
            });
            
            closeModalBtn.addEventListener('click', () => {
                quoteModal.classList.remove('open');
                quoteModal.setAttribute('aria-hidden', 'true');
            });
            
            // Click outside close modal
            quoteModal.addEventListener('click', (e) => {
                if (e.target === quoteModal) {
                    quoteModal.classList.remove('open');
                    quoteModal.setAttribute('aria-hidden', 'true');
                }
            });
        }

        // Initial setup run
        initCategory(currentCategory);
    }
});
