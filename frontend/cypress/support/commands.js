Cypress.Commands.add('login', (role) => {
    // Define role mappings
    const roleMappings = {
        'admin': { testId: 'login-admin', role: 'SUPERADMIN', email: 'admin@stocksteward.ai', name: 'Admin User' },
        'superadmin': { testId: 'login-admin', role: 'SUPERADMIN', email: 'admin@stocksteward.ai', name: 'Admin User' },
        'trader': { testId: 'login-trader', role: 'TRADER', email: 'trader@stocksteward.ai', name: 'Trader User' },
        'auditor': { testId: 'login-auditor', role: 'AUDITOR', email: 'auditor@stocksteward.ai', name: 'Auditor User' },
        'business-owner': { testId: 'login-business-owner', role: 'BUSINESS_OWNER', email: 'owner@stocksteward.ai', name: 'Business Owner' },
        'BUSINESS_OWNER': { testId: 'login-business-owner', role: 'BUSINESS_OWNER', email: 'owner@stocksteward.ai', name: 'Business Owner' }
    };

    const roleData = roleMappings[role] || { testId: `login-${role.toLowerCase()}`, role: 'TRADER', email: `test@${role}.com`, name: `${role} User` };

    // First, visit the login page to ensure the app context is initialized
    cy.visit('/login');

    // Simulate login by directly setting user in localStorage
    const mockUser = {
        id: `mock-${role}-${Date.now()}`,
        name: roleData.name,
        email: roleData.email,
        role: roleData.role,
        avatar: roleData.name.slice(0, 2).toUpperCase(),
        full_name: roleData.name,
        trading_mode: 'AUTO',  // Add the trading_mode property that TradingHub expects
        is_superuser: roleData.role === 'SUPERADMIN'
    };

    // Set the user in localStorage to simulate login
    cy.window().then((win) => {
        win.localStorage.setItem('stocksteward_user', JSON.stringify(mockUser));
    });

    // Force a page reload to ensure the app picks up the new user from localStorage
    cy.reload();

    // Verify login was successful - the user should be redirected from login to home
    cy.url().should('not.include', '/login');
    cy.url().should('include', Cypress.config().baseUrl);

    // Wait for the main heading to appear
    cy.get('h1', { timeout: 10000 }).should('be.visible');
});

// Add a command to wait for the app to finish loading data
Cypress.Commands.add('waitForAppDataLoad', () => {
    // Wait for the loader to disappear (indicates AppDataContext has loaded)
    cy.get('body', { timeout: 30000 }).should('not.contain', 'Synchronizing Execution Parameters...');

    // Additional wait to ensure all data has loaded
    cy.wait(2000);
});
