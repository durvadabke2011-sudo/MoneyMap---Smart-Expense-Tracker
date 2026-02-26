🚀 MoneyMap – Deploy & Database Commands
⚡ QUICKSTART (Windows – VS Code)
Option A — One command setup (recommended)
Just double-click setup.bat

It installs packages, loads the database, and starts the server automatically.

Option B — Step by step commands

Open the MoneyMap folder in VS Code, then open the terminal (`Ctrl + ``):

📦 STEP 1 — Create & Activate Python Virtual Environment
# Create venv (if not already created)
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate
📦 STEP 2 — Install Python Packages
pip install -r requirements.txt

✅ All required packages will be installed in your venv.

🗄️ STEP 3 — Create a dedicated MySQL user (recommended)

Do not use root for your app — this avoids “Access Denied” errors.

Login to MySQL as root:

mysql -u root -p

Then run:

-- Create app user
DROP USER IF EXISTS 'moneymap_user'@'localhost';
CREATE USER 'moneymap_user'@'localhost'
IDENTIFIED WITH mysql_native_password
BY 'moneymap123';

-- Grant privileges
GRANT ALL PRIVILEGES ON moneymap.* TO 'moneymap_user'@'localhost';
FLUSH PRIVILEGES;

This ensures Python can connect without errors.

🗄️ STEP 4 — Load the Database
mysql -u root -p < moneymap.sql

Enter your root MySQL password

This creates the moneymap database and all 14 tables.

Alternative if MySQL is not in PATH (Windows):

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < moneymap.sql
⚙️ STEP 5 — Edit config.py

Update MySQL credentials for your app user:

DB_HOST = 'localhost'
DB_USER = 'moneymap_user'
DB_PASSWORD = 'moneymap123'
DB_NAME = 'moneymap'

SECRET_KEY = 'moneymap_super_secret_2024'

Save the file.

▶️ STEP 6 — Run the App
python app.py

Open browser → http://localhost:5000

Test Register / Login

Dashboard, Budgets, Trips, Accounts, Analysis, Bills, EMI, Subscriptions, Settings → all work

🔧 USEFUL DATABASE COMMANDS
Connect to MySQL
mysql -u root -p
Switch to MoneyMap database
USE moneymap;
See all tables
SHOW TABLES;
Check all users registered
SELECT id, name, email, created_at FROM users;
See recent transactions
SELECT * FROM transactions ORDER BY date DESC LIMIT 20;
Delete all data (keep tables)
DELETE FROM EmiPayments;
DELETE FROM Loans;
DELETE FROM BankTransactions;
DELETE FROM Subscriptions;
DELETE FROM SavingsGoals;
DELETE FROM UserPreferences;
DELETE FROM Bills;
DELETE FROM TripExpenses;
DELETE FROM Trips;
DELETE FROM Accounts;
DELETE FROM Budgets;
DELETE FROM Transactions;
DELETE FROM Categories;
DELETE FROM Users;
Drop and recreate database (full reset)
DROP DATABASE moneymap;

Then re-run:

mysql -u root -p < moneymap.sql
🌐 DEPLOY TO A SERVER (Linux VPS – e.g., AWS / DigitalOcean)
1️⃣ SSH into your server
ssh root@your-server-ip
2️⃣ Install dependencies
sudo apt update
sudo apt install python3 python3-pip mysql-server -y
3️⃣ Start MySQL and set root password
sudo systemctl start mysql
sudo mysql_secure_installation
4️⃣ Upload your project
scp -r MoneyMap/ root@your-server-ip:/var/www/moneymap
5️⃣ Install Python packages & load DB
cd /var/www/moneymap
pip3 install -r requirements.txt
mysql -u root -p < moneymap.sql
6️⃣ Edit config.py with server DB password
nano config.py
7️⃣ Run with Gunicorn (production server)
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
8️⃣ Keep server running after logout
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app &
9️⃣ Open in browser
http://your-server-ip:5000
🛑 STOP THE SERVER
# Windows / Mac / Linux
Ctrl + C
🔁 QUICK REFERENCE CHEAT SHEET
Task	Command
Create & activate venv	python -m venv venv → venv\Scripts\activate
Install packages	pip install -r requirements.txt
Load database	mysql -u root -p < moneymap.sql
Start app	python app.py
Start app (Linux prod)	gunicorn -w 4 -b 0.0.0.0:5000 app:app
Connect to MySQL	mysql -u root -p
View tables	SHOW TABLES;
Reset database	DROP DATABASE moneymap; then re-run SQL file
Full auto setup (Windows)	Double-click setup.bat
Full auto setup (Linux/Mac)	chmod +x setup.sh && ./setup.sh

✅ This version avoids root login errors, ensures Python venv is used, and uses a dedicated MySQL app user (moneymap_user) so your database connections are always successful.