from __future__ import annotations
from typing import List, Dict, Tuple
from faker import Faker
from faker.providers import BaseProvider
import random
from decimal import Decimal

class CommerceProvider(BaseProvider):
    """
    Enhanced Faker provider for realistic e-commerce data like Amazon products.
    Generates product names, descriptions, prices, ratings, and more.
    """

    # ---------- Product Categories ----------
    categories = {
        "Electronics": {
            "subcategories": ["Smartphones", "Laptops", "Headphones", "Cameras", "Smart Home", "Gaming"],
            "base_nouns": ["Phone", "Laptop", "Tablet", "Monitor", "Speaker", "Camera", "Router", "Charger", 
                          "Headphones", "Earbuds", "Keyboard", "Mouse", "Webcam", "Hub", "Drive", "Controller"],
            "adjectives": ["Wireless", "Bluetooth", "USB-C", "Fast-Charging", "HD", "4K", "Smart", "Portable",
                          "Noise-Canceling", "Gaming", "Professional", "Compact", "High-Speed", "Waterproof"],
            "materials": ["Aluminum", "Carbon-Fiber", "Titanium", "Plastic", "Metal", "Glass", "Silicone"],
            "brands": ["TechFlow", "ElectroMax", "DigitalPro", "SmartTech", "PowerLink", "SoundWave"]
        },
        "Home & Kitchen": {
            "subcategories": ["Kitchen Appliances", "Home Decor", "Bedding", "Storage", "Cleaning", "Furniture"],
            "base_nouns": ["Blender", "Coffee-Maker", "Toaster", "Pan", "Knife-Set", "Cutting-Board", "Organizer",
                          "Basket", "Pillow", "Blanket", "Curtains", "Lamp", "Mirror", "Shelf", "Chair", "Table"],
            "adjectives": ["Stainless-Steel", "Non-Stick", "Dishwasher-Safe", "Heat-Resistant", "Stackable",
                          "Foldable", "Multi-Purpose", "Easy-Clean", "Scratch-Resistant", "BPA-Free"],
            "materials": ["Stainless-Steel", "Ceramic", "Glass", "Bamboo", "Silicone", "Plastic", "Wood", "Cotton"],
            "brands": ["HomeChef", "KitchenPro", "ComfortHome", "ModernLiving", "CozySpace", "ChefMaster"]
        },
        "Clothing": {
            "subcategories": ["Men's", "Women's", "Kids", "Shoes", "Accessories", "Activewear"],
            "base_nouns": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Hoodie", "Sneakers", "Boots",
                          "Shorts", "Skirt", "Blouse", "Pants", "Hat", "Scarf", "Belt", "Socks", "Underwear"],
            "adjectives": ["Comfortable", "Breathable", "Stretch", "Moisture-Wicking", "Slim-Fit", "Relaxed-Fit",
                          "Vintage", "Casual", "Formal", "Athletic", "Lightweight", "Warm", "Stylish"],
            "materials": ["Cotton", "Polyester", "Denim", "Wool", "Cashmere", "Linen", "Spandex", "Leather"],
            "brands": ["StyleMax", "ComfortWear", "TrendSet", "ActiveLife", "ClassicFit", "UrbanStyle"]
        },
        "Beauty & Personal Care": {
            "subcategories": ["Skincare", "Makeup", "Hair Care", "Oral Care", "Fragrances", "Personal Hygiene"],
            "base_nouns": ["Serum", "Moisturizer", "Cleanser", "Shampoo", "Conditioner", "Lipstick", "Foundation",
                          "Toothbrush", "Perfume", "Lotion", "Cream", "Oil", "Mask", "Scrub", "Soap"],
            "adjectives": ["Organic", "Natural", "Hypoallergenic", "Anti-Aging", "Hydrating", "Nourishing",
                          "Long-Lasting", "Waterproof", "SPF", "Gentle", "Deep-Cleansing", "Volumizing"],
            "materials": ["Hyaluronic-Acid", "Vitamin-C", "Retinol", "Collagen", "Argan-Oil", "Aloe-Vera"],
            "brands": ["GlowSkin", "PureBeauty", "NaturalGlow", "BeautyMax", "SkinCare Pro", "RadiantLife"]
        },
        "Sports & Outdoors": {
            "subcategories": ["Fitness", "Outdoor Recreation", "Sports Equipment", "Camping", "Water Sports"],
            "base_nouns": ["Yoga-Mat", "Dumbbell", "Resistance-Band", "Tent", "Sleeping-Bag", "Backpack",
                          "Water-Bottle", "Bike", "Helmet", "Gloves", "Shoes", "Jacket", "Rope", "Cooler"],
            "adjectives": ["Waterproof", "Lightweight", "Durable", "Portable", "Anti-Slip", "Quick-Dry",
                          "UV-Protection", "Insulated", "Adjustable", "Professional", "Heavy-Duty"],
            "materials": ["Neoprene", "Ripstop-Nylon", "Gore-Tex", "Polyester", "Aluminum", "Stainless-Steel"],
            "brands": ["OutdoorPro", "FitLife", "AdventureGear", "SportMax", "NatureTrek", "ActivePro"]
        }
    }

    # ---------- Common elements ----------
    general_adjectives = [
        "Premium", "Deluxe", "Professional", "Essential", "Ultimate", "Advanced", "Basic", "Standard",
        "Heavy-Duty", "Commercial-Grade", "Eco-Friendly", "Sustainable", "Innovative", "Classic",
        "Modern", "Vintage", "Retro", "Minimalist", "Luxury", "Budget-Friendly", "Value-Pack"
    ]

    suffixes = ["Pro", "Max", "Plus", "Lite", "Mini", "Ultra", "XL", "2.0", "3000", "Elite", "Premium", ""]
    
    # ---------- Description components ----------
    feature_templates = [
        "Features {feature} technology",
        "Includes {feature} design",
        "Built with {feature} construction",
        "Equipped with {feature} system",
        "Enhanced with {feature} coating"
    ]

    benefit_templates = [
        "Perfect for {use_case}",
        "Ideal for {use_case}",
        "Great for {use_case}",
        "Designed for {use_case}",
        "Essential for {use_case}"
    ]

    quality_phrases = [
        "premium quality", "exceptional durability", "superior performance", "outstanding value",
        "professional grade", "commercial quality", "long-lasting design", "trusted reliability",
        "innovative engineering", "precision crafted", "expertly designed", "carefully constructed"
    ]

    use_cases = [
        "everyday use", "professional applications", "home and office", "travel and commuting",
        "outdoor adventures", "fitness enthusiasts", "busy lifestyles", "entertainment",
        "creative projects", "family activities", "special occasions", "gift giving"
    ]

    # ---------- Price ranges by category ----------
    price_ranges = {
        "Electronics": (15.99, 2999.99),
        "Home & Kitchen": (8.99, 899.99),
        "Clothing": (12.99, 299.99),
        "Beauty & Personal Care": (6.99, 199.99),
        "Sports & Outdoors": (19.99, 799.99)
    }

    def product_random_category(self) -> str:
        """Return a random product category."""
        return self.random_element(list(self.categories.keys()))

    def product_random_subcategory(self, category: str = None) -> str:
        """Return a random subcategory for the given category."""
        if not category:
            category = self.product_random_category()
        return self.random_element(self.categories[category]["subcategories"])

    def brand_name(self, category: str = None) -> str:
        """Generate a realistic brand name."""
        if category and category in self.categories:
            return self.random_element(self.categories[category]["brands"])
        
        # Fallback to generic brand generation
        prefixes = ["Tech", "Pro", "Ultra", "Smart", "Elite", "Prime", "Max", "Digital", "Power", "Super"]
        suffixes = ["Works", "Labs", "Tech", "Pro", "Max", "Plus", "Solutions", "Systems", "Co", "Inc"]
        return f"{self.random_element(prefixes)}{self.random_element(suffixes)}"

    def product_name(self, category: str = None, include_brand: bool = True) -> str:
        """Generate a realistic product name."""
        if not category:
            category = self.product_random_category()
        
        cat_data = self.categories[category]
        parts = []
        
        # Optional brand name
        if include_brand and self.random_element([True, False, False]):  # 33% chance
            parts.append(self.brand_name(category))
        
        # Core product components
        if self.random_element([True, False]):  # 50% chance for adjective
            if self.random_element([True, False]):  # Category-specific vs general
                parts.append(self.random_element(cat_data["adjectives"]))
            else:
                parts.append(self.random_element(self.general_adjectives))
        
        # Material (less common)
        if self.random_element([True, False, False, False]):  # 25% chance
            parts.append(self.random_element(cat_data["materials"]))
        
        # Base noun (always present)
        parts.append(self.random_element(cat_data["base_nouns"]))
        
        # Suffix (sometimes)
        suffix = self.random_element(self.suffixes)
        if suffix and self.random_element([True, False, False]):  # 33% chance
            parts.append(suffix)
        
        return " ".join(parts)

    def product_description(self, name: str = None, category: str = None, length: str = "medium") -> str:
        """Generate a realistic product description."""
        if not name:
            name = self.product_name(category)
        if not category:
            category = self.product_random_category()
        
        cat_data = self.categories[category]
        sentences = []
        
        # Opening sentence
        quality = self.random_element(self.quality_phrases)
        material = self.random_element(cat_data["materials"]).lower().replace("-", " ")
        sentences.append(f"The {name} combines {quality} with {material} construction.")
        
        # Feature sentence
        if length in ["medium", "long"]:
            feature = self.random_element(cat_data["adjectives"]).lower().replace("-", " ")
            feature_template = self.random_element(self.feature_templates)
            sentences.append(feature_template.format(feature=feature) + ".")
        
        # Benefit sentence
        use_case = self.random_element(self.use_cases)
        benefit_template = self.random_element(self.benefit_templates)
        sentences.append(benefit_template.format(use_case=use_case) + ".")
        
        # Additional details for long descriptions
        if length == "long":
            additional_features = [
                "Easy to clean and maintain",
                "Backed by manufacturer warranty",
                "Available in multiple colors",
                "Lightweight yet durable design",
                "Suitable for all skill levels",
                "Compact storage when not in use"
            ]
            sentences.append(self.random_element(additional_features) + ".")
        
        return " ".join(sentences)

    def product_price(self, category: str = None) -> Decimal:
        """Generate a realistic price for the category."""
        if not category:
            category = self.product_random_category()
        
        min_price, max_price = self.price_ranges.get(category, (9.99, 299.99))
        
        # Generate price with realistic endings (.99, .49, .95, .00)
        price = round(random.uniform(min_price, max_price), 2)
        endings = [0.99, 0.49, 0.95, 0.00]
        price = int(price) + self.random_element(endings)
        
        return Decimal(str(price))

    def product_rating(self) -> float:
        """Generate a realistic product rating (1.0 to 5.0)."""
        # Bias towards higher ratings like real marketplaces
        weights = [1, 2, 5, 15, 25]  # 1-star to 5-star weights
        rating = random.choices(range(1, 6), weights=weights)[0]
        
        # Add decimal precision
        decimal_part = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) / 10
        return min(5.0, rating + decimal_part)

    def product_review_count(self) -> int:
        """Generate a realistic number of reviews."""
        # Most products have few reviews, some have many
        ranges = [(0, 10), (11, 50), (51, 200), (201, 1000), (1001, 10000)]
        weights = [30, 40, 20, 8, 2]
        
        chosen_range = random.choices(ranges, weights=weights)[0]
        return random.randint(chosen_range[0], chosen_range[1])

    def product_sku(self) -> str:
        """Generate a realistic SKU/model number."""
        patterns = [
            f"{self.random_element(['B', 'A', 'M', 'P', 'X'])}{random.randint(100000, 999999)}",
            f"{self.random_element(['PRO', 'MAX', 'ULT'])}-{random.randint(1000, 9999)}",
            f"{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(10, 99)}",
            f"{self.random_element(['HD', 'XL', 'LX'])}{random.randint(100, 999)}"
        ]
        return self.random_element(patterns)

    def product_bundle(self, category: str = None, count: int = None) -> List[Dict]:
        """Generate a bundle of related products."""
        if not count:
            count = random.randint(2, 5)
        
        bundle = []
        for _ in range(count):
            product = {
                "name": self.product_name(category),
                "price": self.product_price(category),
                "sku": self.product_sku()
            }
            bundle.append(product)
        
        return bundle

    def full_product(self, category: str = None) -> Dict:
        """Generate a complete product with all details."""
        if not category:
            category = self.product_random_category()
        
        name = self.product_name(category)
        return {
            "name": name,
            "category": category,
            "subcategory": self.product_random_subcategory(category),
            "brand": self.brand_name(category),
            "description": self.product_description(name, category),
            "price": self.product_price(category),
            "rating": self.product_rating(),
            "review_count": self.product_review_count(),
            "sku": self.product_sku(),
            "in_stock": self.random_element([True] * 9 + [False])  # 90% in stock
        }

# ---------- Enhanced demo ----------
if __name__ == "__main__":
    fake = Faker()
    fake.add_provider(CommerceProvider)

    print("=== Sample Products ===\n")
    
    for category in ["Electronics", "Home & Kitchen", "Clothing"]:
        print(f"--- {category} ---")
        product = fake.full_product(category)
        
        print(f"Name: {product['name']}")
        print(f"Brand: {product['brand']}")
        print(f"Price: ${product['price']}")
        print(f"Rating: {product['rating']:.1f} ⭐ ({product['review_count']} reviews)")
        print(f"SKU: {product['sku']}")
        print(f"Description: {product['description']}")
        print(f"Stock: {'✅ In Stock' if product['in_stock'] else '❌ Out of Stock'}")
        print("-" * 60)
        print()

    print("=== Product Bundle Example ===")
    bundle = fake.product_bundle("Electronics", 3)
    for i, item in enumerate(bundle, 1):
        print(f"{i}. {item['name']} - ${item['price']} (SKU: {item['sku']})")