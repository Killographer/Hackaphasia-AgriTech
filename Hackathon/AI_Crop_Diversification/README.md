# 🌾 AI-Powered Crop Diversification Advisor

A smart web application that helps farmers make informed decisions about crop diversification using location-based data and trusted agricultural surveys.

## ✨ Features

### 🌍 **Automatic Location Detection**
- Uses HTML5 Geolocation API to detect farmer's location
- Automatically fills farm information based on GPS coordinates
- No manual data entry required - perfect for illiterate farmers

### 📊 **Smart Data Sources**
- **Government Agricultural Surveys** (Ministry of Agriculture)
- **Soil Survey Reports** (NBSS&LUP)
- **Climate Data** (IMD - India Meteorological Department)
- **Crop Statistics** (ICAR - Indian Council of Agricultural Research)
- **Regional Agricultural Data** (State Agriculture Departments)

### 🌐 **Multi-Language Support**
- **English** - Complete interface
- **हिन्दी (Hindi)** - Full Hindi translation
- **ಕನ್ನಡ (Kannada)** - Complete Kannada translation
- Real-time language switching

### 🤖 **AI-Powered Recommendations**
- Location-based crop recommendations
- Soil compatibility filtering
- Weather-based adjustments
- Revenue and yield predictions

### 📱 **Farmer-Friendly Features**
- **One-Click Setup** - Just click "Auto-Detect Location & Fill Data"
- **Visual Interface** - Easy to understand for all literacy levels
- **Weather Forecast** - 7-day weather predictions with warnings
- **Storage Advice** - Post-harvest storage recommendations
- **Action Plans** - Step-by-step implementation guide

## 🚀 How to Run

### Method 1: Direct Browser (Recommended)
1. **Open the app**: Double-click `index.html` or open it in any web browser
2. **Allow location access**: When prompted, click "Allow" to detect your location
3. **Click "Auto-Detect Location & Fill Data"**: The app will automatically fill all information
4. **Click "Generate Recommendations"**: Get your personalized crop plan

### Method 2: Local Web Server
1. **Open Command Prompt/PowerShell** in the app folder
2. **Start a simple web server**:
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Or Python 2
   python -m SimpleHTTPServer 8000
   
   # Or using Node.js (if installed)
   npx http-server
   ```
3. **Open browser** and go to `http://localhost:8000`

## 📁 Project Structure

```
AI_Crop_Diversification_App/
├── index.html              # Main application file
├── README.md              # This documentation
├── requirements.txt       # Python dependencies (for advanced users)
└── src/                   # Python backend (optional)
    ├── app.py            # Streamlit version
    └── logic.py          # Business logic
```

## 🌍 Supported Locations

### Karnataka
- Bangalore, Mysore, Belgaum, Hubli, Mangalore

### Maharashtra  
- Pune, Nagpur, Nashik

### Tamil Nadu
- Chennai, Coimbatore, Madurai

### Andhra Pradesh
- Hyderabad, Vijayawada, Visakhapatnam

## 📊 Data Sources

The app uses real agricultural data from:

- **Ministry of Agriculture & Farmers Welfare, Government of India**
- **Indian Council of Agricultural Research (ICAR)**
- **National Bank for Agriculture and Rural Development (NABARD)**
- **Indian Institute of Soil Science (IISS)**
- **India Meteorological Department (IMD)**
- **National Bureau of Soil Survey and Land Use Planning (NBSS&LUP)**
- **State Agricultural Universities (SAUs)**

## 🔧 Technical Details

### Frontend
- **HTML5** with Geolocation API
- **CSS3** for responsive design
- **JavaScript** for interactivity
- **No external dependencies** - works offline

### Backend (Optional)
- **Python** with Streamlit
- **Pandas** for data processing
- **Plotly** for visualizations

## 📱 How to Share

### Method 1: Direct File Sharing
1. **Zip the entire folder**: Right-click → "Send to" → "Compressed folder"
2. **Share the zip file** via email, USB, or cloud storage
3. **Recipients extract and open** `index.html` in their browser

### Method 2: Web Hosting (Free)
1. **GitHub Pages**:
   - Upload to GitHub repository
   - Enable GitHub Pages in settings
   - Access via `https://username.github.io/repository-name`

2. **Netlify**:
   - Drag and drop the folder to netlify.com
   - Get instant live URL

3. **Vercel**:
   - Connect GitHub repository
   - Automatic deployment

### Method 3: Local Network Sharing
1. **Start local server** (see Method 2 above)
2. **Find your IP address**: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
3. **Share the URL**: `http://YOUR_IP:8000`
4. **Others on same network** can access via this URL

## 🎯 Target Users

- **Illiterate farmers** - No reading/writing required
- **Small-scale farmers** - Optimized for 0.1-1000 hectares
- **Rural communities** - Works without internet after initial load
- **Agricultural extension workers** - For field demonstrations

## 🌟 Key Benefits

1. **Zero Learning Curve** - Just click and get results
2. **Location-Aware** - Uses actual local agricultural data
3. **Multi-Language** - Supports local languages
4. **Offline Capable** - Works without internet
5. **Government Data** - Based on trusted official sources
6. **Cost-Effective** - Free to use and distribute

## 🔮 Future Enhancements

- Integration with real-time weather APIs
- Mobile app version
- Voice interface for illiterate users
- Integration with government agricultural schemes
- Real-time market price updates
- IoT sensor integration

## 📞 Support

For technical support or feature requests, please contact the development team.

---

**Made with ❤️ for Indian Farmers**

*This application uses data from government agricultural surveys and research institutions to provide accurate, location-specific crop recommendations.*
