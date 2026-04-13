# Gaza Vaccination Map / خريطة التطعيم في غزة

Interactive web map displaying vaccination data for health facilities across Gaza.

خريطة ويب تفاعلية تعرض بيانات التطعيم للمنشآت الصحية في قطاع غزة.

## Features / المميزات

- **Interactive Map** / خريطة تفاعلية: 121 health facilities with geographic locations
- **Data Filtering** / فلترة البيانات: Filter by vaccination statistics, age groups, and organizations
- **Bilingual Support** / دعم لغتين: Arabic and English interface
- **Aggregated Statistics** / إحصائيات مجمعة: Vaccination data grouped by facility

## Data Metrics / مؤشرات البيانات

- Total children vaccinated / إجمالي الأطفال المطعمين
- Vaccination status (on schedule, defaulter, zero dose) / حالة التطعيم
- Age groups: 0-12 months, 12-24 months, 24+ months / الفئات العمرية
- MUAC screening results / نتائج فحص محيط منتصف الذراع

## Usage / الاستخدام

Simply open `index.html` in a web browser to view the map.

افتح ملف `index.html` في متصفح الويب لعرض الخريطة.

## GitHub Pages Deployment / نشر على GitHub Pages

To deploy this map on GitHub Pages:

1. Go to your repository Settings
2. Navigate to Pages section
3. Under "Source", select "Deploy from a branch"
4. Select the `master` branch and `/ (root)` folder
5. Click Save
6. Your map will be available at: `https://[username].github.io/[repository-name]/`

## Technical Stack / التقنيات المستخدمة

- **QGIS2Web**: Map generation from QGIS
- **Leaflet.js**: Interactive map library
- **NoUiSlider**: Range filter controls
- **Python**: Data processing and aggregation

## Data Processing / معالجة البيانات

The vaccination data was:
1. Extracted from Excel records (S123 survey data)
2. Aggregated by health facility name using GROUP BY operations
3. Matched with geographic coordinates from CSV
4. Converted to GeoJSON format for web display

تمت معالجة بيانات التطعيم من خلال:
1. استخراج من سجلات Excel (بيانات استبيان S123)
2. التجميع حسب اسم المنشأة الصحية
3. المطابقة مع الإحداثيات الجغرافية
4. التحويل إلى صيغة GeoJSON للعرض على الويب

## Files / الملفات

- `index.html` - Main map interface
- `data/location_point_unified_corrected_1.js` - GeoJSON data with 121 facilities
- `aggregated_data.json` - Aggregated vaccination statistics
- `create_geojson.py` - Script to generate GeoJSON from CSV and aggregated data
- `parse_excel.py` - Script to aggregate Excel data by facility

## Statistics / الإحصائيات

- **121 facilities** mapped successfully / منشأة تم رسمها بنجاح
- **125 unique facilities** in source data / منشأة فريدة في البيانات الأصلية
- **98% match rate** between coordinates and statistics / نسبة مطابقة

## Organizations / المنظمات

Data includes facilities operated by:
- MoH (Ministry of Health / وزارة الصحة)
- UNRWA
- MSF (Médecins Sans Frontières)
- PRCS (Palestinian Red Crescent Society)

---

**Note**: This map is for visualization and analysis purposes. Data represents aggregated vaccination records from health facility surveys.

**ملاحظة**: هذه الخريطة لأغراض العرض والتحليل. البيانات تمثل سجلات التطعيم المجمعة من مسوحات المنشآت الصحية.
