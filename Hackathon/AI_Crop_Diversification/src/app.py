import os

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

from logic import load_data, compute_scores, diversify_portfolio, disease_warnings_for_crop
from database import FarmerDatabase


st.set_page_config(page_title="Crop Diversification Advisor", layout="wide")

# Language selection
language = st.sidebar.selectbox("🌐 Language / भाषा / ಭಾಷೆ", ["English", "हिन्दी", "ಕನ್ನಡ"])

# Language translations
translations = {
    "English": {
        "title": "AI-Powered Crop Diversification Advisor",
        "subtitle": "Offline, rule-based MVP – no large models or external APIs",
        "region": "Region",
        "district": "District",
        "season": "Season", 
        "max_crops": "Max crops",
        "farm_area": "Farm area (hectares)",
        "plot_length": "Plot Length (meters)",
        "plot_width": "Plot Width (meters)",
        "growth_duration": "Growth Duration (months)",
        "site_specifics": "Site specifics",
        "override_soil": "Override soil for my field",
        "soil_ph": "Soil pH",
        "drainage": "Drainage",
        "organic_matter": "Organic matter %",
        "irrigation": "Irrigation",
        "irrigation_equivalent": "Irrigation equivalent (mm)",
        "saved_seed": "Using saved seed?",
        "flood_prone": "Field gets waterlogged in monsoon?",
        "recommendations": "Recommended diversified plan",
        "total_revenue": "Estimated total seasonal revenue",
        "farm_layout": "Farm Field Layout Visualization",
        "crop_gallery": "Recommended Crops Gallery",
        "realistic_layout": "Realistic Farm Plot Layout",
        "area_comparison": "Area Allocation Comparison",
        "disease_warnings": "Crop health warnings and prevention",
        "data_sources": "Data Sources & References",
        "soil_condition": "Soil Condition",
        "soil_texture": "Soil Texture",
        "soil_moisture": "Soil Moisture",
        "soil_compaction": "Soil Compaction",
        "weather_forecast": "Weather Forecast",
        "storage_advice": "Storage Advice",
        "conclusion": "Conclusion & Recommendations",
        "weather_warnings": "Weather Warnings"
    },
    "हिन्दी": {
        "title": "AI-संचालित फसल विविधीकरण सलाहकार",
        "subtitle": "ऑफलाइन, नियम-आधारित MVP – कोई बड़े मॉडल या बाहरी API नहीं",
        "region": "क्षेत्र",
        "district": "जिला",
        "season": "मौसम",
        "max_crops": "अधिकतम फसलें",
        "farm_area": "खेत का क्षेत्रफल (हेक्टेयर)",
        "plot_length": "प्लॉट की लंबाई (मीटर)",
        "plot_width": "प्लॉट की चौड़ाई (मीटर)",
        "growth_duration": "विकास अवधि (महीने)",
        "site_specifics": "स्थान-विशिष्ट जानकारी",
        "override_soil": "मेरे खेत के लिए मिट्टी को ओवरराइड करें",
        "soil_ph": "मिट्टी का pH",
        "drainage": "जल निकासी",
        "organic_matter": "कार्बनिक पदार्थ %",
        "irrigation": "सिंचाई",
        "irrigation_equivalent": "सिंचाई समतुल्य (mm)",
        "saved_seed": "सहेजे गए बीज का उपयोग कर रहे हैं?",
        "flood_prone": "मानसून में खेत में पानी भर जाता है?",
        "recommendations": "अनुशंसित विविधीकृत योजना",
        "total_revenue": "अनुमानित कुल मौसमी राजस्व",
        "farm_layout": "खेत लेआउट विज़ुअलाइज़ेशन",
        "crop_gallery": "अनुशंसित फसलों की गैलरी",
        "realistic_layout": "यथार्थवादी खेत प्लॉट लेआउट",
        "area_comparison": "क्षेत्र आवंटन तुलना",
        "disease_warnings": "फसल स्वास्थ्य चेतावनियां और रोकथाम",
        "data_sources": "डेटा स्रोत और संदर्भ",
        "soil_condition": "मिट्टी की स्थिति",
        "soil_texture": "मिट्टी की बनावट",
        "soil_moisture": "मिट्टी की नमी",
        "soil_compaction": "मिट्टी का संघनन",
        "weather_forecast": "मौसम पूर्वानुमान",
        "storage_advice": "भंडारण सलाह",
        "conclusion": "निष्कर्ष और सिफारिशें",
        "weather_warnings": "मौसम चेतावनियां"
    },
    "ಕನ್ನಡ": {
        "title": "AI-ಶಕ್ತಿಯುತ ಬೆಳೆ ವೈವಿಧ್ಯೀಕರಣ ಸಲಹೆಗಾರ",
        "subtitle": "ಆಫ್ಲೈನ್, ನಿಯಮ-ಆಧಾರಿತ MVP – ದೊಡ್ಡ ಮಾದರಿಗಳು ಅಥವಾ ಬಾಹ್ಯ API ಗಳಿಲ್ಲ",
        "region": "ಪ್ರದೇಶ",
        "district": "ಜಿಲ್ಲೆ",
        "season": "ಋತು",
        "max_crops": "ಗರಿಷ್ಠ ಬೆಳೆಗಳು",
        "farm_area": "ಕೃಷಿ ಭೂಮಿ (ಹೆಕ್ಟೇರ್)",
        "plot_length": "ಪ್ಲಾಟ್ ಉದ್ದ (ಮೀಟರ್)",
        "plot_width": "ಪ್ಲಾಟ್ ಅಗಲ (ಮೀಟರ್)",
        "growth_duration": "ಬೆಳವಣಿಗೆ ಅವಧಿ (ತಿಂಗಳು)",
        "site_specifics": "ಸ್ಥಳ-ನಿರ್ದಿಷ್ಟ ಮಾಹಿತಿ",
        "override_soil": "ನನ್ನ ಕ್ಷೇತ್ರಕ್ಕೆ ಮಣ್ಣನ್ನು ಬದಲಾಯಿಸಿ",
        "soil_ph": "ಮಣ್ಣಿನ pH",
        "drainage": "ನೀರಿನ ಹರಿವು",
        "organic_matter": "ಸಾವಯವ ವಸ್ತು %",
        "irrigation": "ನೀರಾವರಿ",
        "irrigation_equivalent": "ನೀರಾವರಿ ಸಮಾನ (mm)",
        "saved_seed": "ಉಳಿಸಿದ ಬೀಜ ಬಳಸುತ್ತೀರಾ?",
        "flood_prone": "ಮಳೆಗಾಲದಲ್ಲಿ ಕ್ಷೇತ್ರ ನೀರಿನಲ್ಲಿ ಮುಳುಗುತ್ತದೆಯೇ?",
        "recommendations": "ಶಿಫಾರಸು ಮಾಡಿದ ವೈವಿಧ್ಯೀಕೃತ ಯೋಜನೆ",
        "total_revenue": "ಅಂದಾಜು ಒಟ್ಟು ಋತುಮಾನದ ಆದಾಯ",
        "farm_layout": "ಕೃಷಿ ಕ್ಷೇತ್ರ ವಿನ್ಯಾಸ ದೃಶ್ಯೀಕರಣ",
        "crop_gallery": "ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳ ಗ್ಯಾಲರಿ",
        "realistic_layout": "ಯಥಾರ್ಥ ಕೃಷಿ ಪ್ಲಾಟ್ ವಿನ್ಯಾಸ",
        "area_comparison": "ವಿಸ್ತೀರ್ಣ ಹಂಚಿಕೆ ಹೋಲಿಕೆ",
        "disease_warnings": "ಬೆಳೆ ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆಗಳು ಮತ್ತು ತಡೆಗಟ್ಟುವಿಕೆ",
        "data_sources": "ಡೇಟಾ ಮೂಲಗಳು ಮತ್ತು ಉಲ್ಲೇಖಗಳು",
        "soil_condition": "ಮಣ್ಣಿನ ಸ್ಥಿತಿ",
        "soil_texture": "ಮಣ್ಣಿನ ರಚನೆ",
        "soil_moisture": "ಮಣ್ಣಿನ ತೇವಾಂಶ",
        "soil_compaction": "ಮಣ್ಣಿನ ಸಂಕೋಚನ",
        "weather_forecast": "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ",
        "storage_advice": "ಸಂಗ್ರಹಣೆ ಸಲಹೆ",
        "conclusion": "ತೀರ್ಮಾನ ಮತ್ತು ಶಿಫಾರಸುಗಳು",
        "weather_warnings": "ಹವಾಮಾನ ಎಚ್ಚರಿಕೆಗಳು"
    }
}

t = translations[language]

st.title(t["title"])
st.caption(t["subtitle"])

base_path = os.getcwd()
data = load_data(base_path)

# Initialize database
db = FarmerDatabase()

# District data for each state
district_data = {
    "Karnataka": [
        "Bangalore Urban", "Bangalore Rural", "Mysore", "Belgaum", "Hubli-Dharwad", 
        "Mangalore", "Gulbarga", "Davanagere", "Bellary", "Bijapur", "Tumkur", 
        "Shimoga", "Raichur", "Bidar", "Hassan", "Chitradurga", "Kolar", "Mandya", 
        "Chikmagalur", "Udupi", "Chamrajanagar", "Dakshina Kannada", "Uttara Kannada", 
        "Koppal", "Gadag", "Yadgir", "Bagalkot", "Vijayapura", "Kalaburagi", "Ballari"
    ],
    "Maharashtra": [
        "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Amravati", 
        "Kolhapur", "Sangli", "Malegaon", "Jalgaon", "Akola", "Latur", "Ahmednagar", 
        "Chandrapur", "Parbhani", "Ichalkaranji", "Jalna", "Amalner", "Bhiwandi", 
        "Ulhasnagar", "Sangamner", "Dhule", "Ahmadnagar", "Miraj", "Latur", "Satara", 
        "Beed", "Yavatmal", "Kamptee", "Gondia", "Barshi", "Achalpur", "Osmanabad", 
        "Nanded", "Wardha", "Udgir", "Hinganghat", "Washim", "Amalner"
    ],
    "Tamil Nadu": [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", 
        "Tiruppur", "Ranipet", "Erode", "Thoothukudi", "Dindigul", "Thanjavur", 
        "Vellore", "Kanchipuram", "Krishnagiri", "Namakkal", "Karur", "Tiruvallur", 
        "Tiruvannamalai", "Villupuram", "Cuddalore", "Pudukkottai", "Sivaganga", 
        "Ramanathapuram", "Virudhunagar", "Theni", "Dharmapuri", "Tiruppur", "Perambalur", 
        "Ariyalur", "Nagapattinam", "Tiruvarur", "Tiruchirappalli", "Karur", "Namakkal"
    ],
    "Andhra Pradesh": [
        "Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", 
        "Tirupati", "Kadapa", "Anantapur", "Chittoor", "Ongole", "Nandyal", "Eluru", 
        "Machilipatnam", "Tenali", "Proddatur", "Chilakaluripet", "Kadiri", "Dharmavaram", 
        "Gudivada", "Narasaraopet", "Tadipatri", "Mangalagiri", "Tadepalligudem", 
        "Srikakulam", "Vizianagaram", "Parvathipuram", "Bobbili", "Nuzvid", "Repalle", 
        "Palakollu", "Bhimavaram", "Nidadavole", "Tanuku", "Amalapuram", "Rajam", 
        "Srikalahasti", "Tirupati", "Chittoor", "Puttur", "Kadapa", "Proddatur", 
        "Nandyal", "Kurnool", "Adoni", "Nandikotkur", "Yemmiganur", "Dhone", "Banaganapalle"
    ]
}

# Crop images functionality removed as requested

col1, col2, col3, col4 = st.columns(4)
with col1:
    region = st.selectbox(t["region"], options=["Please select region"] + sorted(data["regions"]["region"].unique()))
with col2:
    if region and region != "Please select region":
        district = st.selectbox(t["district"], options=["Please select district"] + district_data.get(region, []))
    else:
        district = st.selectbox(t["district"], options=["Please select district"], disabled=True)
with col3:
    season = st.selectbox(t["season"], options=["Please select season"] + sorted(data["climate"]["season"].unique()))
with col4:
    max_crops = st.slider(t["max_crops"], min_value=3, max_value=8, value=5)

col1, col2, col3, col4 = st.columns(4)
with col1:
    farm_area = st.number_input(t["farm_area"], min_value=0.1, max_value=1000.0, value=5.0, step=0.1)
with col2:
    plot_length = st.number_input(t["plot_length"], min_value=10.0, max_value=1000.0, value=100.0, step=1.0)
with col3:
    plot_width = st.number_input(t["plot_width"], min_value=10.0, max_value=1000.0, value=50.0, step=1.0)
with col4:
    growth_duration = st.selectbox(t["growth_duration"], options=["Please select duration", "3", "6", "9", "12", "24"])

st.divider()

with st.expander("Show input data (for transparency)", expanded=False):
    st.subheader("Crops")
    st.dataframe(data["crops"], use_container_width=True)
    st.subheader("Regions")
    st.dataframe(data["regions"], use_container_width=True)
    st.subheader("Soil")
    st.dataframe(data["soil"], use_container_width=True)
    st.subheader("Climate")
    st.dataframe(data["climate"], use_container_width=True)

st.subheader(t["site_specifics"])
soil_col1, soil_col2, soil_col3, soil_col4 = st.columns(4)
with soil_col1:
    use_override = st.checkbox(t["override_soil"], value=False)
with soil_col2:
    ph = st.number_input(t["soil_ph"], min_value=4.5, max_value=9.0, value=float(data["soil"].loc[data["soil"]["region"] == region].iloc[0]["ph"]) if region in set(data["soil"]["region"]) else 6.5, step=0.1)
with soil_col3:
    drainage = st.selectbox(t["drainage"], options=["poor", "moderate", "well"], index=["poor", "moderate", "well"].index(str(data["soil"].loc[data["soil"]["region"] == region].iloc[0]["drainage"])) if region in set(data["soil"]["region"]) else 1)
with soil_col4:
    organic_matter = st.number_input(t["organic_matter"], min_value=0.2, max_value=6.0, value=float(data["soil"].loc[data["soil"]["region"] == region].iloc[0]["organic_matter_pct"]) if region in set(data["soil"]["region"]) else 2.0, step=0.1)

irrig_col1, irrig_col2, irrig_col3 = st.columns(3)
with irrig_col1:
    irrigation = st.selectbox(t["irrigation"], options=["rainfed", "canal/well", "drip"])
with irrig_col2:
    extra_rain_mm = st.number_input(t["irrigation_equivalent"], min_value=0.0, max_value=1000.0, value=0.0, step=10.0, help="Approximate seasonal mm supplied by irrigation")
with irrig_col3:
    saved_seed = st.checkbox(t["saved_seed"], value=False)

flood_prone = st.checkbox(t["flood_prone"], value=False)

# Soil Condition Assessment
st.subheader(t["soil_condition"])
soil_cond_col1, soil_cond_col2, soil_cond_col3 = st.columns(3)

with soil_cond_col1:
    soil_texture = st.selectbox(
        t["soil_texture"], 
        options=["Sandy", "Loamy", "Clayey", "Silty", "Mixed"],
        help="How does your soil feel when you squeeze it?"
    )

with soil_cond_col2:
    soil_moisture = st.selectbox(
        t["soil_moisture"],
        options=["Dry", "Slightly Moist", "Moist", "Wet", "Waterlogged"],
        help="Current moisture level of your soil"
    )

with soil_cond_col3:
    soil_compaction = st.selectbox(
        t["soil_compaction"],
        options=["Loose/Airy", "Moderately Firm", "Firm", "Very Firm", "Hard"],
        help="How compacted is your soil?"
    )

# Validate required fields
if region == "Please select region" or season == "Please select season" or growth_duration == "Please select duration":
    st.error("Please select region, season, and growth duration to continue.")
    st.stop()

soil_override = {"ph": ph, "drainage": drainage, "organic_matter_pct": organic_matter} if use_override else None

scored = compute_scores(
    region=region,
    season=season,
    crops_df=data["crops"],
    soil_df=data["soil"],
    climate_df=data["climate"],
    regions_df=data["regions"],
    market_df=data.get("market"),
    soil_override=soil_override,
    extra_rain_mm=extra_rain_mm,
)

recs = diversify_portfolio(scored, max_crops=max_crops)

st.subheader(t["recommendations"])
rec_df = pd.DataFrame([
    {
        "Crop": r.crop,
        "Score": round(r.score, 3),
        "Area Share %": round(r.area_share_pct, 1),
        "Expected Yield (t/ha)": round(r.expected_yield_t_ha, 2),
        "Expected Revenue (/ha)": round(r.expected_revenue_per_ha, 0),
    }
    for r in recs
])
st.dataframe(rec_df, use_container_width=True)

total_revenue = (rec_df["Expected Revenue (/ha)"] * (rec_df["Area Share %"] / 100.0) * farm_area).sum()
st.metric(label=t["total_revenue"], value=f"{int(total_revenue):,}")

# Crop Selection Section
st.subheader("🌾 Crop Selection & Planning")
st.write("Select your preferred crops from the recommendations above:")

# Create checkboxes for crop selection
selected_crops = []
for i, rec in enumerate(recs):
    if st.checkbox(f"{rec.crop} - {rec.area_share_pct:.1f}% area, ₹{rec.expected_revenue_per_ha:,.0f}/ha", key=f"crop_{i}"):
        selected_crops.append({
            'crop_name': rec.crop,
            'area_percentage': rec.area_share_pct,
            'expected_yield': rec.expected_yield_t_ha,
            'expected_revenue': rec.expected_revenue_per_ha,
            'growth_duration': int(growth_duration),
            'season': season
        })

if selected_crops:
    st.success(f"Selected {len(selected_crops)} crops for your farming plan!")
    
    # Save farmer data to database
    farmer_data = {
        'name': 'Farmer User',  # In real app, get from user input
        'region': region,
        'district': district if district != "Please select district" else "Unknown",
        'farm_area': farm_area,
        'plot_length': plot_length,
        'plot_width': plot_width,
        'soil_texture': soil_texture,
        'soil_moisture': soil_moisture,
        'soil_compaction': soil_compaction
    }
    
    farmer_id = db.add_farmer(farmer_data)
    
    # Save crop selections
    for crop_data in selected_crops:
        db.add_crop_selection(farmer_id, crop_data)
    
    # Generate detailed farm layout
    generate_detailed_farm_layout(selected_crops, farm_area, plot_length, plot_width)
    
    # Generate systematic farming plan
    generate_systematic_farming_plan(selected_crops, int(growth_duration), season)
    
    # Generate market tracking
    generate_market_tracking(region, district if district != "Please select district" else "Unknown", selected_crops)
else:
    st.warning("Please select at least one crop to see detailed planning and layout options.")

# Weather Forecast Section
st.subheader(f"🌤️ {t['weather_forecast']}")

# Simulate weather data (in real app, this would come from weather API)
import random
import datetime

# Generate 7-day weather forecast
weather_data = []
for i in range(7):
    date = datetime.date.today() + datetime.timedelta(days=i)
    temp_min = random.randint(15, 25)
    temp_max = random.randint(25, 35)
    humidity = random.randint(40, 80)
    rainfall = random.randint(0, 20) if random.random() < 0.3 else 0
    wind_speed = random.randint(5, 20)
    
    weather_data.append({
        "Date": date.strftime("%Y-%m-%d"),
        "Min Temp (°C)": temp_min,
        "Max Temp (°C)": temp_max,
        "Humidity (%)": humidity,
        "Rainfall (mm)": rainfall,
        "Wind Speed (km/h)": wind_speed
    })

weather_df = pd.DataFrame(weather_data)
st.dataframe(weather_df, use_container_width=True)

# Weather warnings
st.subheader(f"⚠️ {t['weather_warnings']}")
warnings = []

for _, row in weather_df.iterrows():
    if row["Rainfall (mm)"] > 15:
        warnings.append(f"🌧️ Heavy rainfall expected on {row['Date']} - Consider protecting crops")
    if row["Max Temp (°C)"] > 35:
        warnings.append(f"🌡️ High temperature warning on {row['Date']} - Ensure adequate irrigation")
    if row["Wind Speed (km/h)"] > 15:
        warnings.append(f"💨 Strong winds expected on {row['Date']} - Check crop support structures")

if warnings:
    for warning in warnings:
        st.warning(warning)
else:
    st.success("No significant weather warnings for the next 7 days")

# Visual Area Allocation
st.subheader(f"🌾 {t['farm_layout']}")

# Create farm field grid visualization
def create_farm_field_plot(recs, farm_area):
    # Calculate total grid size (approximate)
    grid_size = 20  # 20x20 grid for better visualization
    
    # Create crop color mapping
    crop_colors = {
        'Wheat': '#DAA520',
        'Rice': '#228B22', 
        'Maize': '#FFD700',
        'Chickpea': '#8B4513',
        'Soybean': '#32CD32',
        'Groundnut': '#D2691E',
        'Mustard': '#FFD700',
        'Cotton': '#F5F5DC',
        'Sorghum': '#8B4513',
        'Millet': '#DAA520',
        'Vegetables': '#32CD32',
        'Fruits': '#FF6347'
    }
    
    # Create grid data
    grid_data = []
    crop_legend = {}
    current_pos = 0
    
    for i, rec in enumerate(recs):
        crop_name = rec.crop
        area_share = rec.area_share_pct
        # Calculate number of grid cells for this crop
        cells_for_crop = int((area_share / 100.0) * (grid_size * grid_size))
        
        # Add cells to grid
        for cell in range(cells_for_crop):
            row = current_pos // grid_size
            col = current_pos % grid_size
            if row < grid_size:  # Make sure we don't exceed grid
                grid_data.append({
                    'row': row,
                    'col': col,
                    'crop': crop_name,
                    'color': crop_colors.get(crop_name, '#CCCCCC')
                })
                current_pos += 1
        
        # Store legend info
        crop_legend[crop_name] = {
            'color': crop_colors.get(crop_name, '#CCCCCC'),
            'area_share': area_share,
            'cells': cells_for_crop
        }
    
    return grid_data, crop_legend

# Generate farm field data
grid_data, crop_legend = create_farm_field_plot(recs, farm_area)

# Create farm field visualization
fig = go.Figure()

# Add grid cells
for cell in grid_data:
    fig.add_trace(go.Scatter(
        x=[cell['col']],
        y=[cell['row']],
        mode='markers',
        marker=dict(
            size=15,
            color=cell['color'],
            line=dict(width=1, color='white'),
            symbol='square'
        ),
        name=cell['crop'],
        showlegend=False,
        hovertemplate=f"<b>{cell['crop']}</b><br>" +
                     f"Position: ({cell['col']}, {cell['row']})<br>" +
                     f"<extra></extra>"
    ))

# Update layout to look like a farm field
fig.update_layout(
    title="Your Farm Field Layout (Each square represents a plot section)",
    xaxis=dict(
        title="Field Width",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False,
        range=[-1, 21]
    ),
    yaxis=dict(
        title="Field Length", 
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False,
        range=[-1, 21],
        scaleanchor="x",
        scaleratio=1
    ),
    plot_bgcolor='#f0f8f0',  # Light green background
    paper_bgcolor='#f0f8f0',
    height=600,
    showlegend=False
)

# Add field boundary
fig.add_shape(
    type="rect",
    x0=-0.5, y0=-0.5, x1=19.5, y1=19.5,
    line=dict(color="darkgreen", width=3),
    fillcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

# Create legend
st.subheader("📋 Crop Legend")
legend_cols = st.columns(min(len(crop_legend), 4))
for i, (crop_name, info) in enumerate(crop_legend.items()):
    with legend_cols[i % 4]:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div style="width: 20px; height: 20px; background-color: {info['color']}; 
                        border: 1px solid white; margin-right: 10px;"></div>
            <div>
                <strong>{crop_name}</strong><br>
                <small>{info['area_share']:.1f}% of farm</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Crop Information Summary
st.subheader(f"🌾 {t['crop_gallery']}")

# Create columns for crop information
cols = st.columns(min(len(recs), 4))
for i, rec in enumerate(recs):
    with cols[i % 4]:
        crop_name = rec.crop
        area_share = rec.area_share_pct
        expected_yield = rec.expected_yield_t_ha
        expected_revenue = rec.expected_revenue_per_ha
        
        st.write(f"🌾 **{crop_name}**")
        st.write(f"**Area:** {area_share:.1f}%")
        st.write(f"**Yield:** {expected_yield:.1f} t/ha")
        st.write(f"**Revenue:** ₹{expected_revenue:,.0f}/ha")
        
        # Calculate actual area in hectares
        actual_area = (area_share / 100.0) * farm_area
        st.write(f"**Your Area:** {actual_area:.2f} hectares")

# Realistic Farm Plot Layout
st.subheader(f"🚜 {t['realistic_layout']}")

def create_realistic_farm_layout(recs, farm_area):
    """Create a more realistic farm layout with rectangular plots"""
    # Calculate plot dimensions based on farm area
    total_plots = len(recs)
    
    # Create plot layout data
    plot_data = []
    colors = ['#DAA520', '#228B22', '#FFD700', '#8B4513', '#32CD32', '#D2691E', '#FF6347', '#F5F5DC']
    
    for i, rec in enumerate(recs):
        crop_name = rec.crop
        area_share = rec.area_share_pct
        actual_area = (area_share / 100.0) * farm_area
        
        # Create rectangular plot
        plot_width = 2 + (area_share / 20)  # Width based on area share
        plot_height = 1.5 + (area_share / 25)  # Height based on area share
        
        # Position plots in a grid
        row = i // 3
        col = i % 3
        
        x_center = col * 4 + 2
        y_center = row * 3 + 1.5
        
        plot_data.append({
            'crop': crop_name,
            'area_share': area_share,
            'actual_area': actual_area,
            'x_center': x_center,
            'y_center': y_center,
            'width': plot_width,
            'height': plot_height,
            'color': colors[i % len(colors)]
        })
    
    return plot_data

# Generate realistic farm layout
plot_data = create_realistic_farm_layout(recs, farm_area)

# Create farm plot visualization
fig_farm = go.Figure()

# Add farm plots as rectangles
for plot in plot_data:
    # Add rectangle for the plot
    fig_farm.add_shape(
        type="rect",
        x0=plot['x_center'] - plot['width']/2,
        y0=plot['y_center'] - plot['height']/2,
        x1=plot['x_center'] + plot['width']/2,
        y1=plot['y_center'] + plot['height']/2,
        line=dict(color="darkgreen", width=2),
        fillcolor=plot['color'],
        opacity=0.7
    )
    
    # Add crop label
    fig_farm.add_annotation(
        x=plot['x_center'],
        y=plot['y_center'],
        text=f"<b>{plot['crop']}</b><br>{plot['area_share']:.1f}%<br>{plot['actual_area']:.2f} ha",
        showarrow=False,
        font=dict(size=10, color="white"),
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="white",
        borderwidth=1
    )

# Update layout
fig_farm.update_layout(
    title="Farm Plot Layout (Realistic View)",
    xaxis=dict(
        title="Farm Width",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False,
        range=[0, 12]
    ),
    yaxis=dict(
        title="Farm Length",
        showgrid=True,
        gridcolor='lightgray', 
        zeroline=False,
        range=[0, 8],
        scaleanchor="x",
        scaleratio=1
    ),
    plot_bgcolor='#f0f8f0',
    paper_bgcolor='#f0f8f0',
    height=500,
    showlegend=False
)

# Add farm boundary
fig_farm.add_shape(
    type="rect",
    x0=0.2, y0=0.2, x1=11.8, y1=7.8,
    line=dict(color="darkgreen", width=4),
    fillcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig_farm, use_container_width=True)

# Area allocation bar chart
st.subheader(f"📊 {t['area_comparison']}")
fig_bar = px.bar(
    rec_df, 
    x="Crop", 
    y="Area Share %",
    title="Area Share Percentage by Crop",
    color="Area Share %",
    color_continuous_scale="viridis"
)
fig_bar.update_layout(height=400)
st.plotly_chart(fig_bar, use_container_width=True) 

with st.expander("Why these recommendations? (scoring breakdown)"):
    show_cols = [
        "crop",
        "group",
        "soil_ph_score",
        "drainage_score",
        "water_score",
        "temp_score",
        "market_score",
        "base_score",
    ]
    st.dataframe(scored[show_cols].sort_values("base_score", ascending=False).reset_index(drop=True))

# Second-priority alternatives: flag top picks with high supply pressure
if data.get("market") is not None:
    mkt = data["market"]
    top_crop_names = [r.crop for r in recs]
    oversupplied = []
    for name in top_crop_names:
        row = mkt.loc[(mkt["region"] == region) & (mkt["crop"] == name)]
        if not row.empty:
            demand = float(row.iloc[0]["demand_index"]) 
            supply = float(row.iloc[0]["supply_index"]) 
            if supply >= demand * 1.15:  # oversupply threshold
                oversupplied.append(name)

    if oversupplied:
        st.subheader("Second-priority alternatives (oversupply detected)")
        alt_pool = (
            scored[~scored["crop"].isin(top_crop_names)]
            .copy()
            .sort_values("base_score", ascending=False)
        )
        # prefer crops where demand >= supply
        alt_pool = alt_pool.merge(
            mkt.loc[mkt["region"] == region, ["crop", "demand_index", "supply_index"]],
            on="crop",
            how="left",
        )
        alt_pool["balance"] = (alt_pool["demand_index"] / alt_pool["supply_index"]).fillna(1.0)
        alt_pool = alt_pool.sort_values(["balance", "base_score"], ascending=[False, False])

        suggested = alt_pool.head(len(oversupplied))[["crop", "group", "base_score", "demand_index", "supply_index", "balance"]]
        st.dataframe(suggested.reset_index(drop=True), use_container_width=True)

# Disease warnings for recommended crops
st.subheader(t["disease_warnings"])
soil_row = (data["soil"].loc[data["soil"]["region"] == region].iloc[0]).copy()
if use_override:
    soil_row["ph"] = ph
    soil_row["drainage"] = drainage
    soil_row["organic_matter_pct"] = organic_matter
climate_row = (data["climate"].loc[(data["climate"]["region"] == region) & (data["climate"]["season"] == season)].iloc[0]).copy()
climate_row["forecast_rain_mm"] = float(climate_row["forecast_rain_mm"]) + float(extra_rain_mm)

warn_rows = []
for r in recs:
    warns = disease_warnings_for_crop(
        crop=r.crop,
        region=region,
        season=season,
        soil_row=soil_row,
        climate_row=climate_row,
        irrigation=irrigation,
        user_flags={"saved_seed": saved_seed, "flood_prone": flood_prone},
    )
    for w in warns:
        warn_rows.append({"Crop": r.crop, "Disease": w["disease"], "Risk": w["risk"], "Prevention": w["prevention"]})

if warn_rows:
    warn_df = pd.DataFrame(warn_rows)
    st.dataframe(warn_df, use_container_width=True)
else:
    st.write("No notable disease risks detected based on provided conditions.")

# Storage Recommendations
st.subheader(f"📦 {t['storage_advice']}")

storage_recommendations = {
    "Wheat": {
        "storage_conditions": "Cool, dry place with good ventilation",
        "temperature": "15-20°C",
        "humidity": "Below 60%",
        "duration": "Up to 2 years",
        "tips": "Store in airtight containers, check for pests regularly"
    },
    "Rice": {
        "storage_conditions": "Cool, dry, well-ventilated area",
        "temperature": "10-15°C",
        "humidity": "Below 50%",
        "duration": "Up to 1 year",
        "tips": "Keep away from direct sunlight, use food-grade containers"
    },
    "Maize": {
        "storage_conditions": "Dry, well-ventilated storage",
        "temperature": "Below 20°C",
        "humidity": "Below 60%",
        "duration": "6-12 months",
        "tips": "Ensure proper drying before storage, monitor for mold"
    },
    "Chickpea": {
        "storage_conditions": "Cool, dry place",
        "temperature": "10-20°C",
        "humidity": "Below 60%",
        "duration": "Up to 2 years",
        "tips": "Store in breathable bags, avoid plastic containers"
    },
    "Soybean": {
        "storage_conditions": "Cool, dry, well-ventilated",
        "temperature": "Below 20°C",
        "humidity": "Below 60%",
        "duration": "6-12 months",
        "tips": "Ensure proper drying, check for insect damage"
    },
    "Groundnut": {
        "storage_conditions": "Cool, dry place",
        "temperature": "Below 20°C",
        "humidity": "Below 60%",
        "duration": "6-12 months",
        "tips": "Store in shell or unshelled, avoid moisture"
    },
    "Mustard": {
        "storage_conditions": "Dry, well-ventilated area",
        "temperature": "Below 25°C",
        "humidity": "Below 60%",
        "duration": "Up to 1 year",
        "tips": "Store in airtight containers, protect from pests"
    },
    "Cotton": {
        "storage_conditions": "Dry, well-ventilated warehouse",
        "temperature": "Below 30°C",
        "humidity": "Below 60%",
        "duration": "Up to 1 year",
        "tips": "Store in bales, protect from moisture and pests"
    },
    "Sorghum": {
        "storage_conditions": "Cool, dry place",
        "temperature": "Below 20°C",
        "humidity": "Below 60%",
        "duration": "6-12 months",
        "tips": "Ensure proper drying, store in breathable containers"
    },
    "Millet": {
        "storage_conditions": "Cool, dry, well-ventilated",
        "temperature": "Below 20°C",
        "humidity": "Below 60%",
        "duration": "6-12 months",
        "tips": "Store in airtight containers, check for pests"
    },
    "Vegetables": {
        "storage_conditions": "Refrigerated or cool storage",
        "temperature": "2-8°C",
        "humidity": "High (80-90%)",
        "duration": "1-2 weeks",
        "tips": "Store in perforated bags, consume quickly"
    },
    "Fruits": {
        "storage_conditions": "Cool, well-ventilated area",
        "temperature": "5-15°C",
        "humidity": "High (80-90%)",
        "duration": "1-4 weeks",
        "tips": "Store separately, check for ripeness daily"
    }
}

# Display storage recommendations for recommended crops
for rec in recs:
    crop_name = rec.crop
    if crop_name in storage_recommendations:
        with st.expander(f"Storage advice for {crop_name}", expanded=False):
            storage = storage_recommendations[crop_name]
            st.write(f"**Storage Conditions:** {storage['storage_conditions']}")
            st.write(f"**Temperature:** {storage['temperature']}")
            st.write(f"**Humidity:** {storage['humidity']}")
            st.write(f"**Storage Duration:** {storage['duration']}")
            st.write(f"**Tips:** {storage['tips']}")

# Final Conclusion Page
st.subheader(f"📋 {t['conclusion']}")

# Summary of all findings
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Farm Area", f"{farm_area:.1f} hectares")
    st.metric("Number of Crops", len(recs))
    st.metric("Expected Revenue", f"₹{int(total_revenue):,}")

with col2:
    st.metric("Region", region)
    st.metric("Season", season)
    st.metric("Soil pH", f"{ph:.1f}")

with col3:
    st.metric("Soil Texture", soil_texture)
    st.metric("Soil Moisture", soil_moisture)
    st.metric("Soil Compaction", soil_compaction)

# Key recommendations summary
st.subheader("Key Recommendations Summary")
recommendations_summary = []

for i, rec in enumerate(recs, 1):
    actual_area = (rec.area_share_pct / 100.0) * farm_area
    recommendations_summary.append({
        "Rank": i,
        "Crop": rec.crop,
        "Area (hectares)": f"{actual_area:.2f}",
        "Area (%)": f"{rec.area_share_pct:.1f}%",
        "Expected Yield (t/ha)": f"{rec.expected_yield_t_ha:.1f}",
        "Expected Revenue (₹/ha)": f"₹{rec.expected_revenue_per_ha:,.0f}"
    })

summary_df = pd.DataFrame(recommendations_summary)
st.dataframe(summary_df, use_container_width=True)

# Action items
st.subheader("Action Items")
st.write("1. **Prepare your fields** according to the recommended crop layout")
st.write("2. **Monitor weather conditions** and take necessary precautions")
st.write("3. **Follow storage guidelines** for each crop after harvest")
st.write("4. **Implement disease prevention** measures as suggested")
st.write("5. **Regular soil testing** to maintain optimal conditions")

# Next steps
st.subheader("Next Steps")
st.write("• **Week 1-2:** Field preparation and soil conditioning")
st.write("• **Week 3-4:** Planting according to recommended schedule")
st.write("• **Ongoing:** Monitor crop health and weather conditions")
st.write("• **Harvest:** Follow storage recommendations for each crop")

st.success("🎉 Your personalized crop diversification plan is ready! Follow these recommendations for optimal results.")

st.caption("This is a transparent, interpretable baseline. You can later replace parts of the scoring with small local models trained on your own data, still keeping everything offline.")

with st.expander(t["data_sources"], expanded=False):
    st.subheader("Government & Agricultural Sources")
    
    st.write("**Crop Data & Economics:**")
    st.write("• Ministry of Agriculture & Farmers Welfare, Government of India")
    st.write("• Indian Council of Agricultural Research (ICAR)")
    st.write("• National Bank for Agriculture and Rural Development (NABARD)")
    st.write("• Agricultural Statistics at a Glance (Government of India)")
    
    st.write("**Soil & Climate Data:**")
    st.write("• Indian Institute of Soil Science (IISS)")
    st.write("• India Meteorological Department (IMD)")
    st.write("• National Bureau of Soil Survey and Land Use Planning (NBSS&LUP)")
    st.write("• Karnataka State Department of Agriculture")
    
    st.write("**Market & Price Data:**")
    st.write("• Agricultural Marketing Information Network (AGMARKNET)")
    st.write("• Commission for Agricultural Costs and Prices (CACP)")
    st.write("• Karnataka State Agricultural Marketing Board")
    st.write("• National Commodity & Derivatives Exchange (NCDEX)")
    
    st.write("**Disease Information:**")
    st.write("• Indian Agricultural Research Institute (IARI)")
    st.write("• All India Coordinated Research Project (AICRP)")
    st.write("• State Agricultural Universities (SAUs)")
    st.write("• Plant Protection, Quarantine & Storage Directorate")
    
    st.info("📝 **Note:** This is a hackathon MVP with sample data. For production use, integrate with real-time APIs from these government sources.")


