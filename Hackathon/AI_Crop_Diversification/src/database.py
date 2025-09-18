import sqlite3
import json
import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

class FarmerDatabase:
    """Database class for storing farmer data and market tracking information"""
    
    def __init__(self, db_path: str = "farmer_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create farmers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                region TEXT NOT NULL,
                district TEXT NOT NULL,
                farm_area REAL NOT NULL,
                plot_length REAL NOT NULL,
                plot_width REAL NOT NULL,
                soil_texture TEXT,
                soil_moisture TEXT,
                soil_compaction TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create crop_selections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                crop_name TEXT NOT NULL,
                area_percentage REAL NOT NULL,
                expected_yield REAL,
                expected_revenue REAL,
                growth_duration INTEGER,
                season TEXT,
                selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES farmers (id)
            )
        ''')
        
        # Create market_prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                district TEXT NOT NULL,
                crop_name TEXT NOT NULL,
                price_per_ton REAL NOT NULL,
                price_date DATE NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create farming_plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farming_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                plan_name TEXT NOT NULL,
                duration_months INTEGER NOT NULL,
                season TEXT NOT NULL,
                plan_data TEXT, -- JSON data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES farmers (id)
            )
        ''')
        
        # Create farm_layouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farm_layouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                layout_name TEXT NOT NULL,
                plot_dimensions TEXT, -- JSON data
                layout_data TEXT, -- JSON data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES farmers (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_farmer(self, farmer_data: Dict[str, Any]) -> int:
        """Add a new farmer to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO farmers (name, region, district, farm_area, plot_length, plot_width, 
                               soil_texture, soil_moisture, soil_compaction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            farmer_data.get('name', 'Unknown'),
            farmer_data.get('region'),
            farmer_data.get('district'),
            farmer_data.get('farm_area'),
            farmer_data.get('plot_length'),
            farmer_data.get('plot_width'),
            farmer_data.get('soil_texture'),
            farmer_data.get('soil_moisture'),
            farmer_data.get('soil_compaction')
        ))
        
        farmer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return farmer_id
    
    def add_crop_selection(self, farmer_id: int, crop_data: Dict[str, Any]):
        """Add crop selection for a farmer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crop_selections (farmer_id, crop_name, area_percentage, expected_yield, 
                                       expected_revenue, growth_duration, season)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            farmer_id,
            crop_data.get('crop_name'),
            crop_data.get('area_percentage'),
            crop_data.get('expected_yield'),
            crop_data.get('expected_revenue'),
            crop_data.get('growth_duration'),
            crop_data.get('season')
        ))
        
        conn.commit()
        conn.close()
    
    def add_market_price(self, region: str, district: str, crop_name: str, 
                        price_per_ton: float, source: str = "Manual Entry"):
        """Add market price data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_prices (region, district, crop_name, price_per_ton, price_date, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (region, district, crop_name, price_per_ton, datetime.date.today(), source))
        
        conn.commit()
        conn.close()
    
    def get_market_prices(self, region: str = None, district: str = None, 
                         crop_name: str = None, days: int = 30) -> pd.DataFrame:
        """Get market price data with filters"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT region, district, crop_name, price_per_ton, price_date, source
            FROM market_prices
            WHERE price_date >= date('now', '-{} days')
        '''.format(days)
        
        params = []
        if region:
            query += " AND region = ?"
            params.append(region)
        if district:
            query += " AND district = ?"
            params.append(district)
        if crop_name:
            query += " AND crop_name = ?"
            params.append(crop_name)
        
        query += " ORDER BY price_date DESC, crop_name"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def add_farming_plan(self, farmer_id: int, plan_name: str, duration_months: int, 
                        season: str, plan_data: Dict[str, Any]):
        """Add a farming plan for a farmer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO farming_plans (farmer_id, plan_name, duration_months, season, plan_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (farmer_id, plan_name, duration_months, season, json.dumps(plan_data)))
        
        conn.commit()
        conn.close()
    
    def add_farm_layout(self, farmer_id: int, layout_name: str, 
                       plot_dimensions: Dict[str, Any], layout_data: Dict[str, Any]):
        """Add a farm layout for a farmer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO farm_layouts (farmer_id, layout_name, plot_dimensions, layout_data)
            VALUES (?, ?, ?, ?)
        ''', (farmer_id, layout_name, json.dumps(plot_dimensions), json.dumps(layout_data)))
        
        conn.commit()
        conn.close()
    
    def get_farmer_data(self, farmer_id: int) -> Dict[str, Any]:
        """Get complete farmer data including all related information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get farmer basic info
        cursor.execute('SELECT * FROM farmers WHERE id = ?', (farmer_id,))
        farmer = cursor.fetchone()
        
        if not farmer:
            conn.close()
            return None
        
        # Get crop selections
        cursor.execute('SELECT * FROM crop_selections WHERE farmer_id = ?', (farmer_id,))
        crops = cursor.fetchall()
        
        # Get farming plans
        cursor.execute('SELECT * FROM farming_plans WHERE farmer_id = ?', (farmer_id,))
        plans = cursor.fetchall()
        
        # Get farm layouts
        cursor.execute('SELECT * FROM farm_layouts WHERE farmer_id = ?', (farmer_id,))
        layouts = cursor.fetchall()
        
        conn.close()
        
        return {
            'farmer': farmer,
            'crops': crops,
            'plans': plans,
            'layouts': layouts
        }
    
    def get_market_trends(self, region: str, district: str, crop_name: str) -> Dict[str, Any]:
        """Get market trends for a specific crop in a region/district"""
        df = self.get_market_prices(region, district, crop_name, days=90)
        
        if df.empty:
            return {'trend': 'no_data', 'average_price': 0, 'price_change': 0}
        
        # Calculate trends
        latest_price = df.iloc[0]['price_per_ton']
        oldest_price = df.iloc[-1]['price_per_ton']
        average_price = df['price_per_ton'].mean()
        
        price_change = ((latest_price - oldest_price) / oldest_price) * 100 if oldest_price > 0 else 0
        
        trend = 'up' if price_change > 5 else 'down' if price_change < -5 else 'stable'
        
        return {
            'trend': trend,
            'average_price': round(average_price, 2),
            'price_change': round(price_change, 2),
            'latest_price': latest_price,
            'data_points': len(df)
        }
    
    def generate_farmer_report(self, farmer_id: int) -> Dict[str, Any]:
        """Generate a comprehensive report for a farmer"""
        farmer_data = self.get_farmer_data(farmer_id)
        
        if not farmer_data:
            return None
        
        # Calculate total expected revenue
        total_revenue = sum(crop[4] for crop in farmer_data['crops'])  # expected_revenue column
        
        # Get market trends for selected crops
        market_trends = {}
        for crop in farmer_data['crops']:
            crop_name = crop[2]  # crop_name column
            trends = self.get_market_trends(
                farmer_data['farmer'][2],  # region
                farmer_data['farmer'][3],  # district
                crop_name
            )
            market_trends[crop_name] = trends
        
        return {
            'farmer_info': farmer_data['farmer'],
            'crop_selections': farmer_data['crops'],
            'farming_plans': farmer_data['plans'],
            'farm_layouts': farmer_data['layouts'],
            'total_expected_revenue': total_revenue,
            'market_trends': market_trends,
            'report_generated': datetime.datetime.now().isoformat()
        }

# Sample data population functions
def populate_sample_market_data(db: FarmerDatabase):
    """Populate database with sample market data"""
    regions = ['Karnataka', 'Maharashtra', 'Tamil Nadu', 'Andhra Pradesh']
    districts = {
        'Karnataka': ['Bangalore Urban', 'Mysore', 'Belgaum', 'Hubli-Dharwad'],
        'Maharashtra': ['Pune', 'Nagpur', 'Nashik', 'Mumbai'],
        'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli'],
        'Andhra Pradesh': ['Hyderabad', 'Vijayawada', 'Visakhapatnam', 'Guntur']
    }
    crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Groundnut', 'Soybean']
    
    import random
    
    for region in regions:
        for district in districts[region]:
            for crop in crops:
                # Generate random price data for the last 30 days
                base_price = random.randint(20000, 60000)
                for days_ago in range(30):
                    price_date = datetime.date.today() - datetime.timedelta(days=days_ago)
                    price_variation = random.uniform(0.8, 1.2)
                    price = base_price * price_variation
                    
                    db.add_market_price(region, district, crop, price, "Sample Data")

if __name__ == "__main__":
    # Initialize database and populate with sample data
    db = FarmerDatabase()
    populate_sample_market_data(db)
    print("Database initialized with sample data!")
