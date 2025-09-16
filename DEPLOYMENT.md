# 🚀 Deployment Guide for Lead Intent Scoring Service

## 🎯 Recommended Deployment Options

### ⭐ **Option 1: Railway (Best Choice)**

Railway is perfect for Flask applications with databases:

#### **Steps:**
1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Setup**
   ```bash
   railway login
   railway new
   ```

3. **Deploy**
   ```bash
   railway deploy
   ```

4. **Add Environment Variables**
   ```bash
   railway variables set GEMINI_API_KEY=your_api_key_here
   railway variables set FLASK_ENV=production
   ```

5. **Get URL**
   ```bash
   railway domain
   ```

---

### 🔥 **Option 2: Render**

Great alternative with free tier:

#### **Steps:**
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: lead-intent-scoring
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn -w 1 -b 0.0.0.0:$PORT "app:create_app()"
       envVars:
         - key: FLASK_ENV
           value: production
         - key: GEMINI_API_KEY
           sync: false
   ```

3. **Connect GitHub repo to Render dashboard**

---

### 🌊 **Option 3: Heroku**

Classic choice with good documentation:

#### **Steps:**
1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key_here
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

---

### 🐳 **Option 4: Digital Ocean App Platform**

#### **Steps:**
1. **Create app.yaml**
   ```yaml
   name: lead-intent-scoring
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/your-repo
       branch: main
     run_command: gunicorn -w 1 -b 0.0.0.0:$PORT "app:create_app()"
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: FLASK_ENV
       value: production
     - key: GEMINI_API_KEY
       value: your_api_key_here
   ```

2. **Deploy through DO dashboard**

---

## ❌ **Why Not Vercel?**

### **Problems with Vercel for this Project:**
1. **Serverless Limitations**: Functions restart between requests
2. **No Persistent Storage**: SQLite database won't persist
3. **File Upload Issues**: CSV uploads don't work well in serverless
4. **Cold Starts**: Performance issues with ML/AI processing

### **What Would Need to Change for Vercel:**
- Replace SQLite with external database (PostgreSQL, MongoDB)
- Rewrite as individual serverless functions
- Use external storage for file uploads
- Implement stateless architecture

---

## 🎯 **Quick Start with Railway (Recommended)**

### **1-Minute Deploy:**
```bash
# Install Railway
npm install -g @railway/cli

# Login
railway login

# Navigate to your project
cd lead-intent-scoring-service

# Initialize and deploy
railway new
railway deploy

# Add your API key
railway variables set GEMINI_API_KEY=your_actual_api_key

# Get your live URL
railway domain
```

### **Your service will be live at:**
```
https://your-app-name.railway.app
```

### **Test the deployment:**
```bash
curl https://your-app-name.railway.app/health
```

---

## 🔧 **Production Configuration**

### **Environment Variables to Set:**
```bash
FLASK_ENV=production
GEMINI_API_KEY=your_actual_api_key
SECRET_KEY=your_secret_key_here
PORT=5000  # Usually set automatically
```

### **Database Considerations:**
- **Development**: SQLite (current setup)
- **Production**: Consider PostgreSQL for better performance
- **Migration**: Update `SQLALCHEMY_DATABASE_URI` in config

### **Monitoring & Logging:**
- Enable application logging
- Set up health check monitoring
- Configure error tracking (Sentry, etc.)

---

## 🚨 **Post-Deployment Checklist**

✅ **Service Health**: Check `/health` endpoint  
✅ **Environment Variables**: Verify all secrets are set  
✅ **Database**: Confirm database initialization  
✅ **File Uploads**: Test CSV upload functionality  
✅ **AI Integration**: Verify Gemini API connectivity  
✅ **Error Handling**: Test fallback mechanisms  
✅ **Performance**: Monitor response times  
✅ **Scaling**: Configure auto-scaling if needed  

---

## 📞 **Need Help?**

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test locally first
4. Consult platform-specific documentation

**Railway is strongly recommended** for the best experience with this Flask application! 🚀