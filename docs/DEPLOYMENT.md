# Deployment Guide

Quick deployment options for your James Clear TRMNL plugin.

## Option 1: Railway (Recommended - Easiest)

Railway provides free tier and automatic deployments from GitHub.

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy to Railway**:
   - Go to https://railway.app
   - Create new project from GitHub repo
   - Railway auto-detects Python and deploys
   - Get your public URL (e.g., `your-app.railway.app`)

3. **Set Environment Variables** (if needed):
   - Add any sensitive config through Railway dashboard

4. **Run Initial Scrape**:
   ```bash
   # In Railway's terminal or locally then upload quotes.json
   python scraper.py
   ```

## Option 2: Render

Free tier available, similar to Railway.

1. Create account at https://render.com
2. New > Web Service
3. Connect GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT server:app`

## Option 3: DigitalOcean Droplet

For more control, use a VPS.

1. **Create Droplet** ($6/month):
   - Ubuntu 22.04
   - Basic plan
   - SSH key setup

2. **SSH into server**:
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Install dependencies**:
   ```bash
   apt update
   apt install python3 python3-pip git
   ```

4. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd james-clear-trmnl-plugin
   pip3 install -r requirements.txt
   python3 scraper.py  # Initial scrape
   ```

5. **Run with systemd**:
   
   Create `/etc/systemd/system/trmnl-james-clear.service`:
   ```ini
   [Unit]
   Description=TRMNL James Clear Plugin
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/james-clear-trmnl-plugin
   ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 server:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   systemctl enable trmnl-james-clear
   systemctl start trmnl-james-clear
   ```

6. **Setup updater service**:
   
   Create `/etc/systemd/system/trmnl-james-clear-updater.service`:
   ```ini
   [Unit]
   Description=TRMNL James Clear Quote Updater
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/james-clear-trmnl-plugin
   ExecStart=/usr/bin/python3 updater.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   systemctl enable trmnl-james-clear-updater
   systemctl start trmnl-james-clear-updater
   ```

7. **Setup nginx reverse proxy** (optional but recommended):
   ```bash
   apt install nginx
   ```

   Create `/etc/nginx/sites-available/trmnl-james-clear`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   Enable site:
   ```bash
   ln -s /etc/nginx/sites-available/trmnl-james-clear /etc/nginx/sites-enabled/
   systemctl restart nginx
   ```

## Option 4: Docker

Use Docker for consistent deployments.

1. **Build image**:
   ```bash
   docker build -t james-clear-trmnl .
   ```

2. **Run initial scrape**:
   ```bash
   docker run --rm -v $(pwd)/quotes.json:/app/quotes.json james-clear-trmnl python scraper.py
   ```

3. **Run with docker-compose**:
   ```bash
   docker-compose up -d
   ```

## After Deployment

1. **Get your plugin URL**: 
   - Railway: `https://your-app.railway.app/plugin`
   - Render: `https://your-app.onrender.com/plugin`
   - DigitalOcean: `http://your-droplet-ip:5000/plugin` (or domain)

2. **Test it**:
   ```bash
   curl -X POST https://your-url/plugin \
     -d "user_uuid=test" \
     -H "Content-Type: application/x-www-form-urlencoded"
   ```

3. **Register with TRMNL**:
   - Go to https://usetrmnl.com
   - Settings > Developer
   - Create Private Plugin
   - Add your plugin URL
   - Add to playlist

## Webhook Setup (Optional)

For newsletter integration via Zapier:

1. **Create Zapier account** (free tier works)

2. **Create Zap**:
   - Trigger: Gmail - New Email
   - Filter: From "james@jamesclear.com" AND Subject contains "3-2-1"
   
3. **Add Webhook Action**:
   - Action: Webhooks by Zapier - POST
   - URL: `https://your-server.com/webhook/newsletter`
   - Payload Type: JSON
   - Data:
     ```json
     {
       "quotes": [
         "Extract quote 1 from email body",
         "Extract quote 2 from email body",
         "Extract quote 3 from email body"
       ]
     }
     ```

4. **Test Zap** and turn on!

## Monitoring

Check server health:
```bash
curl https://your-url/health
```

Check quote stats:
```bash
curl https://your-url/stats
```

## Updating

To update your deployment:

**Railway/Render**: Push to GitHub, auto-deploys

**DigitalOcean**:
```bash
ssh root@your-droplet-ip
cd james-clear-trmnl-plugin
git pull
systemctl restart trmnl-james-clear
systemctl restart trmnl-james-clear-updater
```

**Docker**:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Server won't start
- Check logs: `journalctl -u trmnl-james-clear -f`
- Verify quotes.json exists
- Check port 5000 isn't already in use

### TRMNL can't connect
- Verify URL is publicly accessible
- Check firewall allows inbound port 5000 (or 80/443 if using nginx)
- Test with curl from another machine

### Quotes not updating
- Check updater service: `systemctl status trmnl-james-clear-updater`
- Verify scraper works: `python3 scraper.py`
- Check for errors in logs
