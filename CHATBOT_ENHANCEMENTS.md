# 🤖 Enhanced Chatbot Features

**Version:** 2.0 - Advanced Query Support
**Date:** November 9, 2025

---

## 📋 Overview

The Dreambook Salon chatbot has been enhanced with advanced natural language processing capabilities, Filipino/Taglish support, and intelligent context-aware responses. The chatbot can now handle specific queries about services, products, dates, and historical analytics.

---

## ✨ New Features

### 1. **Filipino/Taglish Language Support** 🇵🇭

The chatbot now understands both English and Filipino queries naturally.

**Supported Filipino Keywords:**
- `magkano` - how much
- `meron bang` - is there
- `serbisyo` - service
- `presyo` - price
- `sikat` - popular
- `bukas` - open/tomorrow
- `oras` - time
- `saan` - where
- `kita` - income/revenue
- `bilang` - count
- `kulang` - low stock
- `ubos` - out of stock
- `ngayon` - today
- `linggo` - week
- `buwan` - month
- And more...

**Example Queries:**
```
Customer: "Magkano ang haircut?"
Bot: Returns price, duration, and booking info for haircut service

Customer: "Meron bang appointment sa 12/26/2025?"
Bot: Checks availability and shows open slots for that date

Customer: "Gaano katagal ang massage?"
Bot: Returns duration and pricing for massage service
```

---

### 2. **Specific Service/Product Price Queries** 💰

Ask about any service or product by name and get detailed information.

**Supported Patterns:**
- "How much is [service name]?"
- "Magkano ang [service name]?"
- "Price of [service name]"
- "[service name] price?"

**Example Queries:**
```
✅ "How much is the haircut?"
✅ "Magkano ang hair spa?"
✅ "Price of massage"
✅ "facial price?"
✅ "rebonding magkano?"
```

**Bot Response Includes:**
- Service name
- **Price** (highlighted)
- Duration in minutes
- Full description
- Booking prompt

**For Staff (Products/Inventory):**
```
Staff: "How much is shampoo?"
Bot: Shows stock level, threshold, and low stock alerts
```

---

### 3. **Service Duration Queries** ⏱️

Ask how long a specific service takes.

**Supported Patterns:**
- "How long is [service name]?"
- "Gaano katagal ang [service name]?"
- "Duration of [service name]"

**Example Queries:**
```
✅ "How long is the haircut?"
✅ "Gaano katagal ang hair spa?"
✅ "Duration of the facial"
```

**Bot Response Includes:**
- Service name
- **Duration** (highlighted in minutes)
- Price
- Booking prompt

---

### 4. **Date-Specific Availability Queries** 📅

Check if appointments are available on a specific date.

**Supported Date Formats:**
- MM/DD/YYYY (e.g., 12/26/2025)
- MM-DD-YYYY (e.g., 12-26-2025)
- DD/MM/YYYY (e.g., 26/12/2025)
- DD-MM-YYYY (e.g., 26-12-2025)
- Short year: MM/DD/YY (e.g., 12/26/25)

**Supported Patterns:**
- "Meron bang appointment sa [date]?"
- "Available on [date]?"
- "May slot ba sa [date]?"
- "Pwede ba sa [date]?"
- "Book on [date]"

**Example Queries:**
```
✅ "Meron bang appointment sa 12/26/2025?"
✅ "Available on 1/15/2026?"
✅ "May slot ba sa 12-25-2025?"
✅ "Pwede book sa 2/14/2026?"
```

**Bot Response Includes:**
- Date in full format (e.g., December 26, 2025)
- Number of available slots
- Booking instructions (if available)
- Alternative suggestions (if fully booked)
- Past date warnings

**Features:**
- Validates date is in the future
- Shows available slots (max 10 per day)
- Provides step-by-step booking guidance
- Suggests alternatives if fully booked

---

### 5. **Historical Analytics Queries** 📊 (Staff Only)

Staff and admins can ask about past performance using natural date references.

**Supported Time References:**

**Specific Weekdays:**
- "Last Monday", "Last Friday", etc.
- "Nakaraang Lunes", "Nakaraang Biyernes", etc.

**Relative Dates:**
- "Yesterday" / "Kahapon"
- "Last week" / "Nakaraang linggo"
- "Last month" / "Nakaraang buwan"

**Example Queries:**
```
✅ "Revenue last friday"
✅ "How much is our revenue last friday?"
✅ "Appointments yesterday"
✅ "Kita last week"
✅ "Sales nakaraang buwan"
```

**Bot Response Includes:**
- Period name (e.g., "Last Friday")
- Exact date or date range
- Total appointments
- Completed appointments
- **Total revenue**

**Supported Weekdays (English & Filipino):**
- Monday / Lunes
- Tuesday / Martes
- Wednesday / Miyerkules
- Thursday / Huwebes
- Friday / Biyernes
- Saturday / Sabado
- Sunday / Linggo

---

## 🎯 Query Examples by User Type

### **For Customers:**

**Pricing Queries:**
```
"Magkano ang haircut?"
"How much is the hair spa?"
"Price of rebonding"
"Facial presyo?"
```

**Duration Queries:**
```
"How long is the massage?"
"Gaano katagal ang hair treatment?"
"Duration of manicure"
```

**Availability Queries:**
```
"Meron bang appointment sa 12/26/2025?"
"Available on Christmas day?"
"May slot ba sa Valentine's?"
"Pwede book sa 1/1/2026?"
```

**General Queries:**
```
"What services do you offer?"
"Ano ang mga serbisyo ninyo?"
"What are your hours?"
"Anong oras kayo bukas?"
"Where are you located?"
"Saan kayo?"
```

---

### **For Staff/Admin:**

**Revenue Analytics:**
```
"Revenue last friday"
"Kita ngayon"
"Sales yesterday"
"Income last week"
"How much revenue last month?"
```

**Appointment Analytics:**
```
"Appointments today"
"Bookings yesterday"
"How many appointments last monday?"
"Bilang ng appointments this week"
```

**Inventory Queries:**
```
"Stock status"
"Low stock items"
"Out of stock"
"Kulang na items"
"How much is shampoo?" (shows inventory info)
```

**Performance Analytics:**
```
"Top services"
"Best performing services"
"Pinaka mataas na revenue"
"Payment stats"
"Bayad analytics"
```

---

## 🔧 Technical Implementation

### **Query Processing Flow:**

1. **Specific Queries First** (Highest Priority)
   - Service/product price lookup
   - Service duration lookup
   - Date availability check
   - Historical analytics (staff only)

2. **General Intent Patterns** (Fallback)
   - Services, pricing, popular, hours, location, contact
   - Analytics intents (revenue, appointments, inventory)

3. **Default Response** (No Match)
   - Role-based help message
   - Query examples
   - Supported features list

### **Pattern Matching:**

**Price Queries:**
```python
# Matches: "how much is X", "magkano ang X", "price of X"
r'(?:how much|magkano)(?: is| ang| yung)? (?:the |ang )?(.*?)(?:\?|$)'
```

**Duration Queries:**
```python
# Matches: "how long is X", "gaano katagal ang X"
r'(?:how long|gaano katagal)(?: is| ang| yung)? (?:the |ang )?(.*?)(?:\?|$)'
```

**Date Queries:**
```python
# Matches: "meron bang sa MM/DD/YYYY", "available on MM/DD/YYYY"
r'(?:meron bang|may|available)(?: sa| on)? (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
```

**Historical Queries:**
```python
# Matches: "last friday", "nakaraang biyernes"
weekdays = {
    'friday': 4, 'biyernes': 4,
    'monday': 0, 'lunes': 0,
    # ... etc
}
```

### **Fuzzy Matching:**

Service/product lookups use case-insensitive partial matching:
```python
Service.objects.filter(
    Q(name__icontains=search_term) | Q(description__icontains=search_term),
    is_active=True
).first()
```

This allows queries like:
- "hair" → matches "Haircut", "Hair Spa", "Hair Color"
- "cut" → matches "Haircut"
- "massage" → matches "Full Body Massage", "Foot Massage"

---

## 📊 Analytics Features (Staff Only)

### **Time-Based Analytics:**

**Daily:**
- Today's summary
- Yesterday's performance
- Specific weekday (last monday, last friday, etc.)

**Weekly:**
- This week's summary
- Last week's performance

**Monthly:**
- This month's summary
- Last month's performance

### **Analytics Metrics:**

Each analytics query includes:
- **Total Appointments** - All bookings for the period
- **Completed Appointments** - Successfully finished services
- **Revenue** - Total paid amount (₱)
- **Date/Period** - Clear date range display

### **Example Staff Query Flow:**

```
Staff: "revenue last friday"

Bot Response:
📊 **Last Friday Analytics**

Date: November 8, 2025
Total Appointments: 12
Completed: 10
Revenue: ₱15,450.00
```

---

## 🌐 Bilingual Support

### **Mixed Language Queries:**

The chatbot handles code-switching (Taglish) naturally:

```
✅ "Magkano yung haircut?"
✅ "May available ba na slot sa december?"
✅ "Gaano katagal ang hair spa service?"
✅ "Revenue last friday kumusta?"
```

### **Bilingual Responses:**

Many responses include both English and Filipino:

```
Bot: "Would you like to book an appointment? Just let me know!
(Gusto mo bang mag-book? Sabihin mo lang!)"
```

---

## 🚀 Usage Examples

### **Scenario 1: Customer Pricing Inquiry**

```
Customer: "Magkano ang hair spa?"

Bot: 💇 **Hair Spa Treatment**

Price: **₱1,500**
Duration: 90 minutes

Revitalize your hair with our premium spa treatment
including deep conditioning and scalp massage.

Would you like to book this service?
```

### **Scenario 2: Customer Date Check**

```
Customer: "Meron bang appointment sa 12/25/2025?"

Bot: 📅 **Availability for December 25, 2025**

✅ **7 slots available!**

We have openings on this date. You can book an appointment:
1. Click 'Book Now' or 'Plan an appointment'
2. Select December 25, 2025
3. Choose your preferred time slot

Looking forward to pampering you! 💇✨
```

### **Scenario 3: Staff Historical Query**

```
Staff: "revenue last friday"

Bot: 📊 **Last Friday Analytics**

Date: November 8, 2025
Total Appointments: 12
Completed: 10
Revenue: ₱15,450.00
```

### **Scenario 4: Duration Query**

```
Customer: "How long is the massage?"

Bot: ⏱️ **Full Body Massage**

Duration: **60 minutes**
Price: ₱800

Perfect timing for a premium pampering session!
Would you like to book?
```

---

## 🎨 Response Formatting

All bot responses use **Markdown formatting** for better readability:

- **Bold** for emphasis (`**text**`)
- Bullet points for lists
- Emojis for visual clarity
- Clear section headers
- Numbered instructions

**Example:**
```markdown
💇 **Haircut Service**

Price: **₱350**
Duration: 45 minutes

Our expert stylists will give you a fresh, modern look
tailored to your style.

Would you like to book this service?
```

---

## 🔐 Role-Based Access Control

### **Customer Access:**
✅ Services and pricing
✅ Service duration
✅ Popular services
✅ Booking information
✅ Date availability
✅ Hours and location
✅ Contact information
❌ Revenue analytics
❌ Staff analytics
❌ Inventory details (see general info only)

### **Staff/Admin Access:**
✅ All customer features
✅ Revenue analytics (historical and current)
✅ Appointment statistics
✅ Inventory status with stock levels
✅ Top services performance
✅ Payment analytics
✅ Historical queries (last week, last month, etc.)

---

## 📝 Error Handling

### **Invalid Date Format:**
```
Customer: "Available on 99/99/9999?"
Bot: "I couldn't understand the date format '99/99/9999'.
Please use MM/DD/YYYY (e.g., 12/26/2025)"
```

### **Past Date:**
```
Customer: "Meron bang slot sa 1/1/2024?"
Bot: "That date (January 1, 2024) is in the past!
Please choose a future date."
```

### **Service Not Found:**
```
Customer: "How much is flying service?"
Bot: "I couldn't find information about 'flying service'.
Try asking about our available services or check the services page!"
```

### **Unauthorized Access:**
```
Customer: "Revenue last friday"
Bot: "I'm sorry, but analytics information is only available
to staff members. You can ask me about our services, pricing,
or booking information!

(Pasensya na, pero ang analytics ay para lang sa staff.
Magtanong ka tungkol sa aming services, presyo, o booking!)"
```

---

## 🎯 Query Success Rate

The chatbot can now handle:

✅ **Price queries** with fuzzy matching
✅ **Duration queries** with partial service names
✅ **Date availability** in multiple formats
✅ **Historical analytics** with natural time references
✅ **Mixed language** (English + Filipino)
✅ **Typo tolerance** (partial matching)
✅ **Past date validation**
✅ **Role-based permissions**

---

## 🔮 Future Enhancements

Potential additions for future versions:

1. **Time-specific availability:** "Available at 2pm on 12/26/2025?"
2. **Stylist availability:** "Is Maria available on Friday?"
3. **Package deals:** "Show me combo packages"
4. **Loyalty program:** "How many points do I have?"
5. **Voice input:** Speech-to-text for hands-free queries
6. **Multi-language:** Add more Philippine languages
7. **Smart suggestions:** "Customers who booked X also booked Y"
8. **Weather-based:** "Good hair day services for rainy weather"

---

## 📚 Testing Queries

### **Customer Test Queries:**

```
# Pricing
- "Magkano ang haircut?"
- "How much is the rebonding?"
- "Price of hair spa"

# Duration
- "How long is the massage?"
- "Gaano katagal ang facial?"

# Availability
- "Meron bang slot sa 12/26/2025?"
- "Available on New Year?"

# General
- "What services do you have?"
- "Anong oras kayo bukas?"
```

### **Staff Test Queries:**

```
# Historical Revenue
- "Revenue last friday"
- "Kita kahapon"
- "Sales last week"

# Analytics
- "Appointments today"
- "Top services"
- "Inventory status"
- "Low stock items"
```

---

## 🏆 Impact

### **User Experience:**
- **Faster responses** - No need to browse pages for simple info
- **Natural queries** - Ask in your own words, any language
- **Accurate answers** - Database-driven, real-time information
- **24/7 availability** - Instant answers anytime

### **Business Value:**
- **Reduced support load** - Automated FAQ responses
- **Better insights** - Staff can query analytics on-the-go
- **Improved conversion** - Easy access to pricing/availability
- **Customer satisfaction** - Instant, helpful responses

---

**Maintained by:** Claude
**Framework:** Django + Python Regex
**Database:** PostgreSQL/MySQL via Django ORM
**Language Support:** English, Filipino (Tagalog)
