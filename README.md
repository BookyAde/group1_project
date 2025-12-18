# 📊 Data Warehouse Analytics Platform  
**Data Engineering Class B - Final Project**  
*Team: Data Warehouse Team*

## 🎯 Project Overview

A comprehensive data analytics platform built with **Streamlit** and **Supabase** that demonstrates real-world data engineering concepts. This application provides a complete end-to-end solution for data ingestion, storage, processing, and visualization, designed specifically for our Data Engineering class presentation.

### 🏆 **Key Achievements**
- **Production-ready** web application with 4 interactive pages
- **Full Supabase integration** for cloud data storage
- **6+ visualization types** with interactive Plotly charts
- **Real-time data processing** and caching
- **Professional UI/UX** with custom themes
- **Complete documentation** and deployment guide

## ✨ **Live Features**

### 📈 **Interactive Analytics Dashboard**
- **Real-time Metrics**: Live dataset counts, row totals, processing stats
- **Data Quality Monitoring**: Completeness gauges and quality indicators
- **Recent Activity Feed**: Timestamped uploads and operations
- **Quick Actions**: One-click navigation to all platform features

### 🎨 **Advanced Data Visualization**
| Chart Type | Use Case | Features |
|------------|----------|----------|
| **Line Chart** | Time series analysis | Date-based trends, custom colors |
| **Bar Chart** | Categorical comparison | Grouped data, average calculations |
| **Scatter Plot** | Correlation analysis | X/Y axis selection, color coding |
| **Histogram** | Distribution analysis | Adjustable bins, statistical overlays |
| **Box Plot** | Outlier detection | Grouping options, quartile display |
| **Area Chart** | Cumulative trends | Filled areas, time-based aggregation |

### 📁 **Data Management System**
- **Multi-format Support**: CSV, Excel, JSON file uploads
- **Smart Preview**: First 20 rows with column type detection
- **Metadata Tracking**: File size, row count, upload timestamp
- **Sample Generation**: Intelligent data creation based on file patterns

### ⚙️ **System Configuration**
- **Theme Selection**: 4 color schemes (Gold & Black, Dark, Light, Blue)
- **Supabase Monitoring**: Live connection status and health checks
- **Cache Management**: Manual cache clearing and optimization
- **Export System**: Download logs and configuration settings

## 🏗️ **Technical Architecture**

### **System Diagram**
```
┌─────────────────┐    ┌──────────────┐    ┌────────────────┐
│   User Browser  │────│  Streamlit   │────│   Supabase     │
│   (Frontend)    │    │  (Python)    │    │  (PostgreSQL)  │
└─────────────────┘    └──────────────┘    └────────────────┘
         │                      │                     │
         │                      │              ┌──────┴──────┐
         │                      │              │  REST API   │
         │               ┌──────▼──────┐       │  Realtime   │
         └───────────────│   Pandas    │       │  Storage    │
                         │   Plotly    │       └─────────────┘
                         │   Requests  │
                         └─────────────┘
```

### **Folder Structure**
```
data-warehouse-platform/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── .gitignore                      # Version control exclusions
│
├── .streamlit/                     # Streamlit configuration
│   ├── config.toml                 # Application settings
│   └── secrets.toml                # Secure credentials (local only)
│
├── frontend/                       # Streamlit application
│   ├── pages/                      # Multi-page interface
│   │   ├── 0_🏠_Dashboard.py       # Home page with KPIs
│   │   ├── 1_📊_Analytics.py       # Data visualization suite
│   │   ├── 2_📁_Data_Management.py # File upload and management
│   │   └── 3_⚙️_Settings.py        # System configuration
│   │
│   ├── components/                 # Reusable UI components
│   │   ├── sidebar.py             # Navigation menu
│   │   └── theme.py               # Theme management system
│   │
│   └── utils/                      # Utility functions
│       ├── config.py              # Configuration loader
│       └── api_client.py          # Supabase API communication
│
└── README.md                       # This documentation
```

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser
- Supabase account (free tier)

### **Installation Steps**

#### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/data-warehouse-platform.git
cd data-warehouse-platform
```

#### **2. Create Virtual Environment** (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Set Up Supabase Database**
1. Create a free project at [supabase.com](https://supabase.com)
2. Navigate to SQL Editor
3. Execute the following SQL:

```sql
-- Create datasets table
CREATE TABLE datasets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    filename TEXT NOT NULL,
    rows INTEGER DEFAULT 0,
    size_mb DECIMAL(10,2) DEFAULT 0,
    status TEXT DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample data for testing
INSERT INTO datasets (filename, rows, size_mb) VALUES
    ('sales_data_2024.csv', 1250, 2.1),
    ('customer_analytics.json', 543, 0.8),
    ('monthly_transactions.xlsx', 3124, 4.5);
```

#### **5. Configure Application Secrets**
Create `.streamlit/secrets.toml`:

```toml
# Supabase Configuration
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-anon-key-here"

# Application Settings
DEBUG_MODE = true
MAX_UPLOAD_SIZE_MB = 10
AUTO_REFRESH_SECONDS = 30
```

#### **6. Launch Application**
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📊 **Application Walkthrough**

### **🏠 Dashboard Page**
**Purpose**: System overview and quick access
- **Real-time Metrics Panel**: Shows total datasets, rows processed, success rate
- **Activity Timeline**: Recent uploads and processing events
- **Data Quality Gauge**: Visual indicator of data completeness
- **Quick Action Buttons**: Direct navigation to key features

### **📊 Analytics Page**
**Purpose**: Interactive data exploration and visualization

#### **Data Selection**
- Dropdown menu of all uploaded datasets
- Smart preview of first 20 rows
- Column statistics and data types

#### **Visualization Options**
1. **Line Chart**
   - Time series analysis
   - Date-based trend visualization
   - Custom Y-axis metric selection

2. **Bar Chart**
   - Categorical data comparison
   - Grouped and stacked options
   - Average calculation by category

3. **Scatter Plot**
   - Correlation analysis between two numeric columns
   - Optional color coding by categorical data
   - Trendline overlay with correlation coefficient

4. **Histogram**
   - Distribution analysis
   - Adjustable bin count (5-100 bins)
   - Statistical overlays (mean, median lines)

5. **Box Plot**
   - Outlier detection
   - Interquartile range visualization
   - Optional grouping by categories

6. **Area Chart**
   - Cumulative trend visualization
   - Filled area under curve
   - Time-based aggregation

#### **Statistical Insights**
- **Correlation Matrix**: Heatmap showing relationships between all numeric columns
- **Data Quality Report**: Null values, duplicates, completeness percentage
- **Summary Statistics**: Mean, median, standard deviation for all numeric columns

### **📁 Data Management Page**
**Purpose**: Dataset ingestion and management

#### **File Upload Interface**
- Drag-and-drop file uploader
- Supported formats: CSV, Excel (xlsx, xls), JSON
- File size validation (configurable limit)
- Real-time progress indicators

#### **Dataset Management**
- **List View**: All datasets with metadata
- **Preview Function**: First/last N rows display
- **Metadata Display**: File size, row count, upload time
- **Delete Function**: Remove datasets from system

#### **Smart Data Generation**
For demonstration purposes, the system can generate sample data based on filename patterns:
- `*sales*` → Sales data with date, amount, region, product
- `*user*` → User analytics with sessions, devices, countries
- `*transaction*` → Financial data with amounts, categories, timestamps

### **⚙️ Settings Page**
**Purpose**: System configuration and monitoring

#### **Connection Status**
- **Supabase Health Check**: Live connection testing
- **Database Statistics**: Table counts, storage usage
- **API Response Times**: Performance monitoring

#### **Appearance Settings**
- **Theme Selection**: 4 color schemes with instant preview
- **Layout Options**: Container width, sidebar position
- **Display Settings**: Font size, density preferences

#### **System Configuration**
- **Auto-refresh**: Enable/disable and set interval
- **Cache Management**: Manual cache clearing
- **Log Export**: Download system logs for debugging
- **Reset Options**: Restore default settings

#### **Advanced Features**
- **API Timeout Configuration**: Adjust request timeouts
- **Session Management**: Session duration settings
- **Export Configuration**: Default export formats

## 🔧 **Technical Implementation Details**

### **Data Flow Architecture**
```
1. User Upload → 2. File Validation → 3. Metadata Extraction → 
4. Supabase Storage → 5. Data Processing → 6. Visualization → 
7. User Interaction → 8. Real-time Update
```

### **Key Libraries and Their Roles**
| Library | Version | Purpose | Implementation |
|---------|---------|---------|----------------|
| **Streamlit** | 1.28+ | Web framework | Page routing, UI components, session state |
| **Pandas** | 2.0+ | Data processing | DataFrame operations, data cleaning, analysis |
| **Plotly** | 5.17+ | Visualization | Interactive charts, statistical graphs |
| **Supabase** | 1.0+ | Database | Cloud storage, REST API communication |
| **Requests** | 2.31+ | HTTP client | API calls to Supabase backend |

### **Performance Optimizations**
1. **Intelligent Caching**: Streamlit `@st.cache_data` decorator with TTL
2. **Lazy Loading**: Data loads on-demand, not at application start
3. **Batch Processing**: Efficient handling of large datasets
4. **Connection Pooling**: Reusable Supabase API connections
5. **Progressive Rendering**: Charts render as data becomes available

### **Error Handling Strategy**
- **Graceful Degradation**: Features fail gracefully with user feedback
- **Retry Logic**: Automatic retries for transient network issues
- **Validation Layers**: Multiple validation points for data integrity
- **User-Friendly Messages**: Clear, actionable error messages
- **Logging System**: Comprehensive logging for debugging

## 🎨 **UI/UX Design Philosophy**

### **Theme System**
```python
# Gold & Black Theme (Default)
PRIMARY_COLOR = "#FFD700"  # Gold
BACKGROUND_COLOR = "#0F0F0F"  # Dark background
TEXT_COLOR = "#FFFFFF"  # White text
ACCENT_COLOR = "#1A1A1A"  # Dark accents
```

### **Responsive Design Principles**
- **Mobile-First**: All components work on mobile devices
- **Flexible Layouts**: Adapts to different screen sizes
- **Touch-Friendly**: Large buttons and interactive elements
- **Performance Optimized**: Fast loading even on slow connections

### **Accessibility Features**
- **High Contrast Mode**: Support for visually impaired users
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Compatibility**: Proper ARIA labels
- **Color Blind Friendly**: Color schemes tested for accessibility

## 🔌 **Supabase Integration Details**

### **Database Schema**
```sql
-- Extended schema for production use
CREATE TABLE datasets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_type VARCHAR(10),
    rows INTEGER DEFAULT 0,
    size_mb DECIMAL(10,2) DEFAULT 0.00,
    columns INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for performance
CREATE INDEX idx_datasets_uploaded_at ON datasets(uploaded_at DESC);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_filename ON datasets(filename);
```

### **API Endpoints Used**
```python
# Core Supabase API calls
GET    /rest/v1/datasets           # List all datasets
POST   /rest/v1/datasets           # Create new dataset
GET    /rest/v1/datasets?id=eq.{id} # Get specific dataset
PATCH  /rest/v1/datasets?id=eq.{id} # Update dataset
DELETE /rest/v1/datasets?id=eq.{id} # Delete dataset
```

### **Security Considerations**
1. **API Key Protection**: Stored in Streamlit secrets, not in code
2. **CORS Configuration**: Properly configured in Supabase dashboard
3. **Row Level Security**: Can be enabled for production use
4. **Input Sanitization**: All user inputs are validated

## 📈 **Sample Data Structure**

### **Sales Dataset Example**
```csv
Date,Region,Product,Units_Sold,Revenue,Profit_Margin
2024-01-01,North,Product_A,150,12500.50,0.25
2024-01-02,South,Product_B,142,11800.75,0.22
2024-01-03,East,Product_A,168,13200.25,0.27
2024-01-04,West,Product_C,95,8450.00,0.19
```

### **Generated Analytics Output**
- **Trend Analysis**: Monthly sales growth of 12.5%
- **Top Performer**: Product A with 42% of total revenue
- **Regional Insights**: North region leads with 35% market share
- **Correlation**: Strong positive correlation (0.82) between units sold and revenue

## 🚀 **Deployment Options**

### **Local Development**
```bash
# Development mode with hot reload
streamlit run app.py --server.runOnSave true

# Custom port
streamlit run app.py --server.port 8502

# Enable detailed logging
streamlit run app.py --logger.level debug
```

### **Streamlit Cloud Deployment**
1. Push code to GitHub repository
2. Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub repository
4. Configure secrets in Streamlit Cloud dashboard
5. Deploy with one click

### **Configuration File (.streamlit/config.toml)**
```toml
[theme]
primaryColor = "#FFD700"
backgroundColor = "#0F0F0F"
secondaryBackgroundColor = "#1A1A1A"
textColor = "#FFFFFF"
font = "sans serif"

[browser]
gatherUsageStats = false

[server]
maxUploadSize = 10
enableCORS = true
enableXsrfProtection = true
```

## 🐛 **Troubleshooting Guide**

### **Common Issues and Solutions**

#### **Issue 1: "No datasets found in Supabase"**
**Symptoms**: Empty dataset list, no data in analytics
**Solutions**:
1. Check `.streamlit/secrets.toml` exists and has correct credentials
2. Verify Supabase project is active and database is running
3. Check browser console for CORS errors
4. Run connection test in Settings page

#### **Issue 2: Blank or broken charts**
**Symptoms**: Charts display without data or error messages
**Solutions**:
1. Ensure dataset has numeric columns for visualization
2. Check for NaN or infinite values in data
3. Clear browser cache and refresh page
4. Try different chart type to isolate issue

#### **Issue 3: File upload failures**
**Symptoms**: Upload progress hangs or shows errors
**Solutions**:
1. Check file size (limit: 10MB default)
2. Verify file format (CSV, Excel, JSON supported)
3. Check network connectivity to Supabase
4. Review browser console for specific error messages

#### **Issue 4: Slow performance**
**Symptoms**: Laggy interface, slow chart rendering
**Solutions**:
1. Reduce dataset size for demonstration
2. Enable caching in Settings
3. Close unused browser tabs
4. Check network speed to Supabase servers

### **Debug Mode**
Enable debug information by adding to `config.py`:
```python
DEBUG = True
LOG_LEVEL = "DEBUG"
```

## 🎓 **Learning Outcomes**

### **Data Engineering Concepts Demonstrated**
1. **Data Ingestion**: File upload, validation, and parsing
2. **Data Storage**: Cloud database management with Supabase
3. **Data Processing**: Transformation, cleaning, and aggregation
4. **Data Visualization**: Interactive charts and dashboards
5. **System Design**: Scalable, maintainable architecture

### **Technical Skills Developed**
- **Streamlit Application Development**: Multi-page apps, session state, caching
- **Cloud Database Integration**: REST APIs, authentication, real-time updates
- **Data Visualization**: Plotly charts, interactive features, statistical overlays
- **Python Programming**: Pandas data manipulation, error handling, optimization
- **Version Control**: Git workflow, collaboration, documentation

### **Soft Skills Enhanced**
- **Team Collaboration**: Distributed development, code reviews
- **Project Management**: Timeline management, feature prioritization
- **Problem Solving**: Debugging complex issues, finding creative solutions
- **Presentation Skills**: Demonstrating technical concepts clearly

## 🔮 **Future Enhancements**

### **Short-term Improvements**
- [ ] User authentication and authorization
- [ ] Advanced ETL pipeline with transformation rules
- [ ] Scheduled report generation
- [ ] Email notifications for processing completion

### **Medium-term Goals**
- [ ] Machine learning integration for predictions
- [ ] Real-time data streaming support
- [ ] Collaborative features for team usage
- [ ] Advanced data quality checks and alerts

### **Long-term Vision**
- [ ] Multi-tenant architecture for organizations
- [ ] Advanced analytics with custom Python/R scripts
- [ ] API for third-party integrations
- [ ] Mobile application companion

## 👥 **Team Contributions**

### **Team Members**
- **[Your Name]**: Project Lead, Full-stack Development
- **[Teammate 1]**: Database Design, Supabase Integration
- **[Teammate 2]**: Data Visualization, UI/UX Design
- **[Teammate 3]**: Documentation, Testing, Quality Assurance

### **Development Timeline**
| Week | Milestone | Key Deliverables |
|------|-----------|------------------|
| 1 | Project Setup | Requirements, Architecture, Git repo |
| 2 | Core Features | Dashboard, Basic Analytics |
| 3 | Advanced Features | All visualizations, Data management |
| 4 | Polish & Testing | Bug fixes, Performance optimization |
| 5 | Documentation | README, Presentation materials |

## 📚 **Additional Resources**

### **Learning Materials**
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Supabase Documentation](https://supabase.com/docs)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)

### **Sample Datasets for Testing**
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [Google Dataset Search](https://datasetsearch.research.google.com/)
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/)

### **Useful Tools**
- [Postman](https://www.postman.com/) - API testing
- [DB Diagram](https://dbdiagram.io/) - Database schema design
- [Figma](https://www.figma.com/) - UI/UX prototyping

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Data Engineering Class B Instructors** for guidance and support
- **Streamlit Team** for creating an amazing framework
- **Supabase Team** for providing excellent cloud database services
- **Plotly Team** for powerful visualization libraries
- **Open Source Community** for invaluable resources and inspiration

## 🆘 **Support**

For questions, issues, or contributions:
1. Check the [GitHub Issues](https://github.com/yourusername/data-warehouse-platform/issues)
2. Review the [Documentation](docs/) folder
3. Contact the team via class communication channels

---

**Data Warehouse Team - Data Engineering Class B**  
*"Transforming Data into Decisions"*  
*December 2024*