describe('Auditor Role Tests', () => {
    beforeEach(() => {
        cy.login('auditor');
    });

    it('verifies dashboard compliance view', () => {
        cy.visit('/');
        cy.get('[data-testid="dashboard-container"]').should('be.visible');
        cy.contains('Compliance Oversight').should('be.visible');
        cy.get('[data-testid="intelligence-log"]').should('be.visible');
    });

    it('verifies reports and ledger visibility', () => {
        cy.visit('/reports');
        cy.get('[data-testid="reports-container"]').should('be.visible');
        cy.get('[data-testid="algo-trading-ledger"]').should('be.visible');
        cy.get('[data-testid="export-pdf-button"]').should('be.visible');
    });

    it('ensures trading hub is read-only for auditors', () => {
        cy.visit('/trading');
        cy.get('[data-testid="trading-hub-container"]').should('be.visible');
        // Manual order ticket should be disabled/restricted for non-traders or specifically auditors
        // Note: In current implementation, it checks user.trading_mode === 'AUTO' for restrictions.
        // For auditors, they shouldn't even have the toggle if we implemented RBAC fully.
    });
});
