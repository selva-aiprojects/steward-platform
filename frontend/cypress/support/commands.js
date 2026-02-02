Cypress.Commands.add('login', (role) => {
    cy.visit('/login');

    const roleTestIdMap = {
        'admin': 'login-admin',
        'superadmin': 'login-admin',
        'trader': 'login-trader',
        'auditor': 'login-auditor',
        'business-owner': 'login-business-owner',
        'BUSINESS_OWNER': 'login-business-owner'
    };

    const testId = roleTestIdMap[role] || `login-${role.toLowerCase()}`;
    cy.get(`[data-testid="${testId}"]`).click();

    // Verify login was successful - using the heading on the dashboard
    cy.get('h1', { timeout: 10000 }).should('be.visible');
    cy.url().should('eq', Cypress.config().baseUrl + '/');
});
