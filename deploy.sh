#!/bin/bash

# Barabise QR Production Deployment Script

echo "🚀 Setting up Barabise QR Production Environment..."

# Set the project directory
PROJECT_DIR="/var/www/html/barabiseqr"

# Navigate to project directory
cd $PROJECT_DIR

echo "📁 Setting up directory permissions..."

# Set proper ownership
sudo chown -R www-data:www-data $PROJECT_DIR

# Set proper permissions
sudo chmod -R 755 $PROJECT_DIR

# Make sure the database file has proper permissions
if [ -f "clicks.db" ]; then
    sudo chown www-data:www-data clicks.db
    sudo chmod 664 clicks.db
    echo "✅ Database permissions set"
else
    echo "📊 Creating database file..."
    sudo touch clicks.db
    sudo chown www-data:www-data clicks.db
    sudo chmod 664 clicks.db
    echo "✅ Database file created with proper permissions"
fi

# Set permissions for static and templates directories
sudo chmod -R 755 static/
sudo chmod -R 755 templates/

echo "🔧 Setting up WSGI configuration..."

# Make wsgi.py executable
sudo chmod +x wsgi.py

echo "🔄 Restarting Apache..."

# Restart Apache to apply changes
sudo systemctl restart apache2

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Check Apache error logs: sudo tail -f /var/log/apache2/qr_barabise_error.log"
echo "2. Check Apache access logs: sudo tail -f /var/log/apache2/qr_barabise_access.log"
echo "3. Test your application in browser"
echo ""
echo "🔍 If you still see errors, check:"
echo "- Database file permissions: ls -la clicks.db"
echo "- Directory permissions: ls -la"
echo "- Apache configuration: sudo apache2ctl configtest"
