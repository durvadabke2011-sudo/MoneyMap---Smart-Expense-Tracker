-- ═══════════════════════════════════════════════════════════════
-- MoneyMap Database Schema
-- ═══════════════════════════════════════════════════════════════

-- Create Database
CREATE DATABASE IF NOT EXISTS moneymap;
USE moneymap;

-- ═══════════════════════════════════════════════════════════════
-- FEATURES & PAGE MAPPING
-- ═══════════════════════════════════════════════════════════════
-- 📊 Dashboard       → Transactions, LoginHistory, Users
-- 📈 Investments     → Investments
-- 📊 Analysis        → Transactions, Categories
-- 🗂️  Categories      → Categories
-- 💰 Budgets         → Budgets, Transactions
-- 🧾 Accounts        → Accounts
-- 🔔 Bills           → Bills
-- 📺 Subscriptions   → Subscriptions
-- ✈️  Trips          → Trips, TripExpenses
-- 🧮 EMI Tracker     → Loans, EmiPayments
-- ⚙️  Settings       → UserPreferences
-- 👥 Admin Stats     → Users, LoginHistory, all tables
-- ═══════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- USERS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Dashboard, Admin Stats, Settings
-- Tracks: User registration, last login, last activity
CREATE TABLE IF NOT EXISTS Users (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    email          VARCHAR(150) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login     DATETIME,
    last_activity  DATETIME
);

-- ─────────────────────────────────────────────────────────────────
-- LOGIN HISTORY TABLE (NEW)
-- ─────────────────────────────────────────────────────────────────
-- Used by: Dashboard, Admin Stats
-- Tracks: Every user login with timestamp and IP
CREATE TABLE IF NOT EXISTS LoginHistory (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    login_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address  VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- CATEGORIES TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Categories Page, Dashboard, Analysis
-- Tracks: Income/Expense categories created by users
CREATE TABLE IF NOT EXISTS Categories (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name    VARCHAR(100) NOT NULL,
    type    ENUM('income','expense') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- TRANSACTIONS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Dashboard, Analysis, Budgets
-- Tracks: All income and expense transactions
CREATE TABLE IF NOT EXISTS Transactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    category_id INT,
    type        ENUM('income','expense') NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    note        VARCHAR(255),
    date        DATE NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)     REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────────────────────────
-- BUDGETS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Budgets Page, Dashboard
-- Tracks: Monthly budget limits by category
CREATE TABLE IF NOT EXISTS Budgets (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    category_id INT,
    month       VARCHAR(7) NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (user_id)     REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- TRIPS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Trips Page, Dashboard
-- Tracks: Trip details and budget allocation
CREATE TABLE IF NOT EXISTS Trips (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    destination  VARCHAR(150) NOT NULL,
    start_date   DATE NOT NULL,
    end_date     DATE NOT NULL,
    budget       DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- TRIP EXPENSES TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Trips Page
-- Tracks: Individual trip expenses (linked to trips)
CREATE TABLE IF NOT EXISTS TripExpenses (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    trip_id  INT NOT NULL,
    note     VARCHAR(255),
    amount   DECIMAL(12,2) NOT NULL,
    date     DATE NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES Trips(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- ACCOUNTS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Accounts Page, Dashboard
-- Tracks: Cash, Card, UPI accounts and balances
CREATE TABLE IF NOT EXISTS Accounts (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name    VARCHAR(100) NOT NULL,
    type    ENUM('cash','card','upi') NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- BILLS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Bills Page, Dashboard
-- Tracks: Recurring bill reminders with due dates
CREATE TABLE IF NOT EXISTS Bills (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id   INT NOT NULL,
    name      VARCHAR(150) NOT NULL,
    amount    DECIMAL(12,2) NOT NULL,
    due_day   INT NOT NULL,
    category  VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- LOANS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: EMI Tracker Page, Dashboard
-- Tracks: Loan details and EMI calculations
CREATE TABLE IF NOT EXISTS Loans (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    loan_name   VARCHAR(150) DEFAULT 'My Loan',
    principal   DECIMAL(12,2) NOT NULL,
    rate        DECIMAL(5,2)  NOT NULL,
    tenure      INT NOT NULL,
    emi         DECIMAL(12,2),
    total_int   DECIMAL(12,2),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- EMI PAYMENTS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: EMI Tracker Page
-- Tracks: Individual EMI payment records (linked to loans)
CREATE TABLE IF NOT EXISTS EmiPayments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    loan_id     INT NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    paid_date   DATE NOT NULL,
    note        VARCHAR(255),
    FOREIGN KEY (loan_id) REFERENCES Loans(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- BANK TRANSACTIONS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Accounts Page (for bank sync feature)
-- Tracks: Bank statement transactions (credit/debit)
CREATE TABLE IF NOT EXISTS BankTransactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    description VARCHAR(255),
    amount      DECIMAL(12,2) NOT NULL,
    type        ENUM('credit','debit') NOT NULL,
    date        DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- SUBSCRIPTIONS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Subscriptions Page, Dashboard
-- Tracks: Monthly subscription services and costs
CREATE TABLE IF NOT EXISTS Subscriptions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    name        VARCHAR(150) NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    renewal_day INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- SAVINGS GOALS TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Dashboard, Settings
-- Tracks: User savings goals and progress
CREATE TABLE IF NOT EXISTS SavingsGoals (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    name        VARCHAR(150) NOT NULL,
    target      DECIMAL(12,2) NOT NULL,
    saved       DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- USER PREFERENCES TABLE
-- ─────────────────────────────────────────────────────────────────
-- Used by: Settings Page, Dashboard
-- Tracks: User preferences (currency, theme, language)
CREATE TABLE IF NOT EXISTS UserPreferences (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id  INT UNIQUE NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    theme    VARCHAR(20) DEFAULT 'light',
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- INVESTMENTS TABLE (NEW)
-- ─────────────────────────────────────────────────────────────────
-- Used by: Investments Page, Dashboard
-- Tracks: Stock, Mutual Fund, Crypto, and other investments
CREATE TABLE IF NOT EXISTS Investments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    name        VARCHAR(150) NOT NULL,
    type        VARCHAR(100) NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    current_val DECIMAL(12,2) NOT NULL,
    invest_date DATE NOT NULL,
    note        VARCHAR(255),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ═══════════════════════════════════════════════════════════════
-- INDEXES FOR PERFORMANCE
-- ═══════════════════════════════════════════════════════════════
CREATE INDEX idx_user_id_transactions ON Transactions(user_id);
CREATE INDEX idx_user_id_investments ON Investments(user_id);
CREATE INDEX idx_user_id_budgets ON Budgets(user_id);
CREATE INDEX idx_user_id_accounts ON Accounts(user_id);
CREATE INDEX idx_user_id_bills ON Bills(user_id);
CREATE INDEX idx_user_email ON Users(email);
CREATE INDEX idx_login_user ON LoginHistory(user_id);
CREATE INDEX idx_login_time ON LoginHistory(login_time);

-- ═══════════════════════════════════════════════════════════════
-- SAMPLE DATA (Optional - Uncomment to add test data)
-- ═══════════════════════════════════════════════════════════════
-- INSERT INTO Users (name, email, password, created_at, last_login) VALUES
-- ('John Doe', 'john@example.com', 'hashed_password_here', NOW(), NOW()),
-- ('Jane Smith', 'jane@example.com', 'hashed_password_here', NOW(), NOW());

-- ═══════════════════════════════════════════════════════════════
-- USER ANALYTICS QUERIES
-- ═══════════════════════════════════════════════════════════════

-- 1. Get all users with activity stats
SELECT 
    u.id, 
    u.name, 
    u.email, 
    u.created_at, 
    u.last_login,
    (SELECT COUNT(*) FROM Transactions WHERE user_id=u.id) as transaction_count,
    (SELECT COUNT(*) FROM LoginHistory WHERE user_id=u.id) as login_count,
    (SELECT COUNT(*) FROM Investments WHERE user_id=u.id) as investment_count
FROM Users u 
ORDER BY u.last_login DESC;

-- 2. Get user overview (All data in one query)
SELECT 
    u.id,
    u.name,
    u.email,
    u.created_at,
    u.last_login,
    COUNT(DISTINCT lh.id) as login_count,
    COUNT(DISTINCT t.id) as transaction_count,
    COUNT(DISTINCT i.id) as investment_count,
    COUNT(DISTINCT b.id) as budget_count,
    COUNT(DISTINCT a.id) as account_count,
    COUNT(DISTINCT tr.id) as trip_count,
    COUNT(DISTINCT bi.id) as bill_count,
    COUNT(DISTINCT l.id) as loan_count,
    COUNT(DISTINCT s.id) as subscription_count
FROM Users u 
LEFT JOIN LoginHistory lh ON u.id = lh.user_id
LEFT JOIN Transactions t ON u.id = t.user_id
LEFT JOIN Investments i ON u.id = i.user_id
LEFT JOIN Budgets b ON u.id = b.user_id
LEFT JOIN Accounts a ON u.id = a.user_id
LEFT JOIN Trips tr ON u.id = tr.user_id
LEFT JOIN Bills bi ON u.id = bi.user_id
LEFT JOIN Loans l ON u.id = l.user_id
LEFT JOIN Subscriptions s ON u.id = s.user_id
GROUP BY u.id
ORDER BY u.last_login DESC;

-- 3. Get daily active users (DAU)
SELECT DATE(login_time) as date, COUNT(DISTINCT user_id) as active_users 
FROM LoginHistory 
GROUP BY DATE(login_time) 
ORDER BY date DESC 
LIMIT 30;

-- 4. Get user status summary
SELECT 
    CASE 
        WHEN last_login IS NULL THEN 'Never Logged In'
        WHEN last_login >= DATE_SUB(NOW(), INTERVAL 1 DAY) THEN 'Active Today'
        WHEN last_login >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 'Active This Week'
        WHEN last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 'Active This Month'
        ELSE 'Inactive'
    END as user_status,
    COUNT(*) as count
FROM Users
GROUP BY user_status
ORDER BY count DESC;

-- 5. Get users by feature usage
SELECT 
    'Transactions' as feature,
    COUNT(DISTINCT user_id) as user_count
FROM Transactions
UNION ALL
SELECT 
    'Investments',
    COUNT(DISTINCT user_id)
FROM Investments
UNION ALL
SELECT 
    'Budgets',
    COUNT(DISTINCT user_id)
FROM Budgets
UNION ALL
SELECT 
    'Accounts',
    COUNT(DISTINCT user_id)
FROM Accounts
UNION ALL
SELECT 
    'Bills',
    COUNT(DISTINCT user_id)
FROM Bills
UNION ALL
SELECT 
    'Trips',
    COUNT(DISTINCT user_id)
FROM Trips
UNION ALL
SELECT 
    'Loans',
    COUNT(DISTINCT user_id)
FROM Loans
UNION ALL
SELECT 
    'Subscriptions',
    COUNT(DISTINCT user_id)
FROM Subscriptions;

-- 6. Get users with most transactions
SELECT 
    u.id, 
    u.name, 
    u.email,
    COUNT(t.id) as transaction_count,
    SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END) as total_income,
    SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END) as total_expense,
    SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END) - SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END) as net_balance
FROM Users u 
LEFT JOIN Transactions t ON u.id = t.user_id 
GROUP BY u.id 
ORDER BY transaction_count DESC;

-- 7. Get users with investments and returns
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(i.id) as investment_count,
    SUM(i.amount) as total_invested,
    SUM(i.current_val) as current_value,
    (SUM(i.current_val) - SUM(i.amount)) as total_gain_loss,
    ROUND(((SUM(i.current_val) - SUM(i.amount)) / SUM(i.amount) * 100), 2) as return_percentage
FROM Users u 
LEFT JOIN Investments i ON u.id = i.user_id 
WHERE i.id IS NOT NULL
GROUP BY u.id 
ORDER BY total_gain_loss DESC;

-- 8. Get users with budgets and spending
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(b.id) as budget_count,
    SUM(b.amount) as total_budget_set,
    (SELECT SUM(amount) FROM Transactions WHERE user_id=u.id AND type='expense') as total_spent,
    SUM(b.amount) - (SELECT SUM(amount) FROM Transactions WHERE user_id=u.id AND type='expense') as remaining_budget
FROM Users u 
LEFT JOIN Budgets b ON u.id = b.user_id 
WHERE b.id IS NOT NULL
GROUP BY u.id 
ORDER BY total_budget_set DESC;

-- 9. Get users with loans and EMI tracking
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(l.id) as loan_count,
    SUM(l.principal) as total_principal,
    SUM(l.emi) as monthly_emi,
    SUM(l.total_int) as total_interest
FROM Users u 
LEFT JOIN Loans l ON u.id = l.user_id 
WHERE l.id IS NOT NULL
GROUP BY u.id 
ORDER BY total_principal DESC;

-- 10. Get login history with frequency analysis
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(lh.id) as total_logins,
    MAX(lh.login_time) as last_login,
    MIN(lh.login_time) as first_login,
    DATEDIFF(CURDATE(), DATE(MAX(lh.login_time))) as days_since_last_login
FROM Users u 
LEFT JOIN LoginHistory lh ON u.id = lh.user_id 
GROUP BY u.id 
ORDER BY days_since_last_login ASC;

-- 11. Get user engagement score (Comprehensive)
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(DISTINCT DATE(lh.login_time)) as active_days,
    COUNT(lh.id) as total_logins,
    COUNT(t.id) as transactions,
    COUNT(i.id) as investments,
    COUNT(b.id) as budgets,
    COUNT(a.id) as accounts,
    ROUND((COUNT(lh.id) + COUNT(t.id) * 2 + COUNT(i.id) * 3 + COUNT(b.id) * 1.5 + COUNT(a.id)) / 10, 2) as engagement_score
FROM Users u 
LEFT JOIN LoginHistory lh ON u.id = lh.user_id AND lh.login_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
LEFT JOIN Transactions t ON u.id = t.user_id AND t.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
LEFT JOIN Investments i ON u.id = i.user_id AND i.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
LEFT JOIN Budgets b ON u.id = b.user_id
LEFT JOIN Accounts a ON u.id = a.user_id
GROUP BY u.id 
ORDER BY engagement_score DESC;

-- 12. Get total platform statistics
SELECT 
    (SELECT COUNT(*) FROM Users) as total_users,
    (SELECT COUNT(DISTINCT user_id) FROM LoginHistory WHERE DATE(login_time) = CURDATE()) as active_today,
    (SELECT COUNT(DISTINCT user_id) FROM LoginHistory WHERE login_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)) as active_week,
    (SELECT COUNT(DISTINCT user_id) FROM LoginHistory WHERE login_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as active_month,
    (SELECT COUNT(*) FROM Users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)) as new_users_week,
    (SELECT COUNT(*) FROM Transactions) as total_transactions,
    (SELECT COUNT(*) FROM Investments) as total_investments,
    (SELECT SUM(amount) FROM Investments) as total_invested_amount,
    (SELECT SUM(current_val) FROM Investments) as current_investment_value;

-- 13. Get revenue insights by tracking transaction types
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(CASE WHEN t.type = 'income' THEN 1 END) as income_entries,
    COUNT(CASE WHEN t.type = 'expense' THEN 1 END) as expense_entries,
    SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END) as total_income,
    SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END) as total_expenses,
    (SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END) - SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END)) as net_savings
FROM Users u 
LEFT JOIN Transactions t ON u.id = t.user_id 
GROUP BY u.id 
ORDER BY net_savings DESC;

-- 14. Get accounts summary per user
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(a.id) as total_accounts,
    COUNT(CASE WHEN a.type = 'cash' THEN 1 END) as cash_accounts,
    COUNT(CASE WHEN a.type = 'card' THEN 1 END) as card_accounts,
    COUNT(CASE WHEN a.type = 'upi' THEN 1 END) as upi_accounts,
    SUM(a.balance) as total_balance
FROM Users u 
LEFT JOIN Accounts a ON u.id = a.user_id 
GROUP BY u.id 
ORDER BY total_balance DESC;

-- 15. Get subscription costs per user
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(s.id) as subscription_count,
    SUM(s.amount) as monthly_subscription_cost,
    SUM(s.amount) * 12 as annual_subscription_cost
FROM Users u 
LEFT JOIN Subscriptions s ON u.id = s.user_id 
WHERE s.id IS NOT NULL
GROUP BY u.id 
ORDER BY monthly_subscription_cost DESC;

-- ═══════════════════════════════════════════════════════════════
-- DEFAULT CATEGORIES & SETUP DATA
-- ═══════════════════════════════════════════════════════════════

-- NOTE: These are sample default categories. Users can create their own.
-- If you want to auto-assign these to new users, modify the registration logic in auth.py

-- ─────────────────────────────────────────────────────────────────
-- TRANSACTION CATEGORIES (Dashboard & Analysis & Budgets)
-- ─────────────────────────────────────────────────────────────────
-- NOTE: Subscriptions, Bills, and EMI categories are NOT included here
-- because they have dedicated pages (Subscriptions, Bills, EMI Tracker)
-- Users manage those separately on their specific pages

-- Income Categories (6 total)
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Salary', 'income');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Freelance', 'income');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Bonus', 'income');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Investment Returns', 'income');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Gifts', 'income');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Other Income', 'income');

-- Expense Categories (13 total - excludes dedicated page categories)
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Food & Dining', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Transportation', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Shopping', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Utilities', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Healthcare', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Entertainment', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Education', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Insurance', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Home & Rent', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Personal Care', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Phone & Internet', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Gifts & Donations', 'expense');
-- INSERT INTO Categories (user_id, name, type) VALUES (1, 'Other Expense', 'expense');

-- ─────────────────────────────────────────────────────────────────
-- INVESTMENT TYPES (Investments Page)
-- ─────────────────────────────────────────────────────────────────
-- Available Investment Types (used in Investments.type field):
-- - Stocks
-- - Mutual Funds
-- - Bonds
-- - Crypto
-- - PPF (Public Provident Fund)
-- - FD (Fixed Deposit)
-- - Gold
-- - Real Estate
-- - Other

-- ─────────────────────────────────────────────────────────────────
-- BILL REMINDERS (Bills Page)
-- ─────────────────────────────────────────────────────────────────
-- Available Bill Categories:
-- DEFAULT BILLS:
-- - Electricity
-- - Water
-- - Internet
-- - Mobile Bill
-- - Gas
-- - Insurance (Health)
-- - Insurance (Vehicle)
-- - Insurance (Home)
-- - House Rent
-- - Property Tax
-- - EMI (Loan)
-- - Other

-- ─────────────────────────────────────────────────────────────────
-- SUBSCRIPTION TYPES (Subscriptions Page)
-- ─────────────────────────────────────────────────────────────────
-- Available Subscription Categories:
-- - Netflix
-- - Amazon Prime
-- - Disney+
-- - Spotify
-- - Cloud Storage (Google Drive, OneDrive, iCloud)
-- - Gym Membership
-- - News Subscriptions
-- - Software/Tools
-- - Banking Services
-- - Entertainment
-- - Learning (Udemy, Coursera)
-- - Other

-- ─────────────────────────────────────────────────────────────────
-- TRIP EXPENSE TYPES (Trips Page)
-- ─────────────────────────────────────────────────────────────────
-- Available Trip Expense Categories:
-- - Hotel/Accommodation
-- - Food & Dining
-- - Transportation
-- - Activities & Entertainment
-- - Shopping
-- - Guides & Tours
-- - Insurance & Emergency
-- - Miscellaneous

-- ─────────────────────────────────────────────────────────────────
-- BUDGET CATEGORIES (Budgets Page)
-- ─────────────────────────────────────────────────────────────────
-- Budget Categories (Same as Transaction Expense Categories - excludes dedicated page categories):
-- - Food & Dining
-- - Transportation
-- - Shopping
-- - Utilities
-- - Healthcare
-- - Entertainment
-- - Education
-- - Insurance
-- - Home & Rent
-- - Personal Care
-- - Phone & Internet
-- - Gifts & Donations
-- - Other Expense

-- ═══════════════════════════════════════════════════════════════
-- DEFAULT CATEGORIES BY PAGE - QUICK REFERENCE
-- ═══════════════════════════════════════════════════════════════

-- 📊 DASHBOARD & ANALYSIS (Transaction Categories)
--    Income (6):  Salary, Freelance, Bonus, Investment Returns, Gifts, Other Income
--    Expense (13): Food & Dining, Transportation, Shopping, Utilities, Healthcare, Entertainment,
--                  Education, Insurance, Home & Rent, Personal Care, Phone & Internet, 
--                  Gifts & Donations, Other Expense

-- 💰 BUDGETS (Expense Categories Only)
--    Uses same expense categories as Dashboard/Analysis (13 categories)

-- 📈 INVESTMENTS
--    Types (9): Stocks, Mutual Funds, Bonds, Crypto, PPF, FD, Gold, Real Estate, Other

-- 🔔 BILLS (Dedicated Page - User creates bill types here)
--    Types: Electricity, Water, Internet, Mobile, Gas, Insurance (Health/Vehicle/Home), 
--           House Rent, Property Tax, Other

-- 📺 SUBSCRIPTIONS (Dedicated Page - User creates subscription types here)
--    Types: Netflix, Amazon Prime, Disney+, Spotify, Cloud Storage, Gym, News, Software,
--           Banking, Entertainment, Learning, Other

-- ✈️  TRIPS (Dedicated Page - User creates trip expense types here)
--    Types: Hotel/Accommodation, Food & Dining, Transportation, Activities & Entertainment,
--           Shopping, Guides & Tours, Insurance & Emergency, Miscellaneous

-- 🧮 EMI TRACKER (Dedicated Page - User manages loans and EMI payments here)
--    No pre-defined categories - users create loan entries

-- ═══════════════════════════════════════════════════════════════
-- IMPLEMENTATION DETAILS
-- ═══════════════════════════════════════════════════════════════
-- ✅ Transaction Categories: Auto-created for all users during registration (auth.py)
-- ✅ Investment Types: Dropdown in investment.html (hardcoded)
-- ✅ Bills: User-created through Bills page
-- ✅ Subscriptions: User-created through Subscriptions page
-- ✅ Trips: User-created through Trips page
-- ✅ EMI Tracker: User-created through EMI Tracker page
-- ✅ Budgets: Uses Transaction expense categories automatically
