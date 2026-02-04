#!/bin/sh
set -e

echo "Starting MySQL server..."
service mariadb start

echo "Waiting for MySQL to be ready..."
until mysql -u root -e "SELECT 1" >/dev/null 2>&1; do
    sleep 1
done

echo "Setting up database..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS wannanime;"
mysql -u root -e "CREATE USER IF NOT EXISTS 'winky'@'localhost' IDENTIFIED BY 'fake_db_password';"
mysql -u root -e "GRANT ALL PRIVILEGES ON wannanime.* TO 'winky'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"

echo "Loading data from init.sql..."
mysql -u root wannanime < /tmp/init.sql

echo "Removing init.sql..."
rm -f /tmp/init.sql

echo "Starting Flask as user ctf..."
su ctf -c "python3 app.py"
