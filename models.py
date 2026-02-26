from database import query


def create_tables():
    """Create all tables if they don't exist."""

    query("""
        CREATE TABLE IF NOT EXISTS Users (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            name           VARCHAR(100) NOT NULL,
            email          VARCHAR(150) UNIQUE NOT NULL,
            password       VARCHAR(255) NOT NULL,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login     DATETIME,
            last_activity  DATETIME
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS LoginHistory (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            login_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address  VARCHAR(50),
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS Categories (
            id      INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name    VARCHAR(100) NOT NULL,
            type    ENUM('income','expense') NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
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
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS Budgets (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            category_id INT,
            month       VARCHAR(7) NOT NULL,
            amount      DECIMAL(12,2) NOT NULL,
            FOREIGN KEY (user_id)     REFERENCES Users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS Trips (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            user_id      INT NOT NULL,
            destination  VARCHAR(150) NOT NULL,
            start_date   DATE NOT NULL,
            end_date     DATE NOT NULL,
            budget       DECIMAL(12,2) DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS TripExpenses (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            trip_id  INT NOT NULL,
            note     VARCHAR(255),
            amount   DECIMAL(12,2) NOT NULL,
            date     DATE NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES Trips(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS Accounts (
            id      INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name    VARCHAR(100) NOT NULL,
            type    ENUM('cash','card','upi') NOT NULL,
            balance DECIMAL(12,2) DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS Bills (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            user_id   INT NOT NULL,
            name      VARCHAR(150) NOT NULL,
            amount    DECIMAL(12,2) NOT NULL,
            due_day   INT NOT NULL,
            category  VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
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
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS EmiPayments (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            loan_id     INT NOT NULL,
            amount      DECIMAL(12,2) NOT NULL,
            paid_date   DATE NOT NULL,
            note        VARCHAR(255),
            FOREIGN KEY (loan_id) REFERENCES Loans(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS BankTransactions (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            description VARCHAR(255),
            amount      DECIMAL(12,2) NOT NULL,
            type        ENUM('credit','debit') NOT NULL,
            date        DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS Subscriptions (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            name        VARCHAR(150) NOT NULL,
            amount      DECIMAL(12,2) NOT NULL,
            renewal_day INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS SavingsGoals (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            name        VARCHAR(150) NOT NULL,
            target      DECIMAL(12,2) NOT NULL,
            saved       DECIMAL(12,2) DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    query("""
        CREATE TABLE IF NOT EXISTS UserPreferences (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            user_id  INT UNIQUE NOT NULL,
            currency VARCHAR(10) DEFAULT 'INR',
            theme    VARCHAR(20) DEFAULT 'light',
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        )
    """)

    # ✅ NEW: INVESTMENTS TABLE
    query("""
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
        )
    """)

    print("✅ All tables created successfully (including Investments).")