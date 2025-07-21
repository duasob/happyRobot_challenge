# 🌐 Free Hosting with Custom Domains

## Option 1: Vercel (Recommended) 🚀

### Setup Steps:

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy your app:**
   ```bash
   vercel
   ```

4. **Set environment variables:**
   ```bash
   vercel env add WEBHOOK_API_KEY
   # Enter your API key: UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0
   ```

5. **Add custom domain:**
   - Go to Vercel dashboard
   - Select your project
   - Go to Settings → Domains
   - Add your custom domain

### Your URLs will be:
- **Webhook**: `https://your-domain.vercel.app/webhook/`
- **Carriers**: `https://your-domain.vercel.app/carriers/api/carriers`

---

## Option 2: Netlify Functions

### Setup Steps:

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Create netlify.toml:**
   ```toml
   [build]
     functions = "api"
     publish = "public"

   [[redirects]]
     from = "/webhook/*"
     to = "/.netlify/functions/webhook"
     status = 200

   [[redirects]]
     from = "/carriers/*"
     to = "/.netlify/functions/carriers"
     status = 200
   ```

3. **Deploy:**
   ```bash
   netlify deploy
   ```

---

## Option 3: Railway

### Setup Steps:

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add custom domain in Railway dashboard**

---

## Option 4: Render

### Setup Steps:

1. **Create render.yaml:**
   ```yaml
   services:
     - type: web
       name: webhook-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python api/index.py
       envVars:
         - key: WEBHOOK_API_KEY
           value: UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0
   ```

2. **Connect your GitHub repo to Render**
3. **Add custom domain in Render dashboard**

---

## Option 5: Heroku (Limited Free)

### Setup Steps:

1. **Install Heroku CLI:**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Procfile:**
   ```
   web: python api/index.py
   ```

3. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set WEBHOOK_API_KEY=UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0
   git push heroku main
   ```

4. **Add custom domain:**
   ```bash
   heroku domains:add your-domain.com
   ```

---

## 🎯 Quick Start with Vercel:

```bash
# 1. Install Vercel
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel

# 4. Set API key
vercel env add WEBHOOK_API_KEY

# 5. Your webhook will be live at:
# https://your-project.vercel.app/webhook/
```

## 🔑 API Key for All Deployments:
```
UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0
```

## 📡 Testing Your Deployed Webhook:

```bash
# Test GET request
curl https://your-domain.com/webhook/

# Test POST request
curl -X POST https://your-domain.com/webhook/ \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0" \
  -d '{"event": "test", "data": {"message": "Hello!"}}'
```

## 🌟 Recommendation:

**Vercel** is the best option because:
- ✅ Free tier is generous
- ✅ Custom domains included
- ✅ Great performance
- ✅ Easy deployment
- ✅ Automatic HTTPS
- ✅ Global CDN 