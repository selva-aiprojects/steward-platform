describe('Business Owner Role Tests', () => {
    beforeEach(() => {
        cy.login('business-owner');
    });

    it('accesses executive dashboard and metrics', () => {
        cy.visit('/');
        cy.get('[data-testid="dashboard-container"]').should('be.visible');
        cy.contains('Executive Dashboard').should('be.visible');
        cy.get('[data-testid="metrics-grid"]').should('be.visible');
    });

    it('verifies reports access and export', () => {
        cy.visit('/reports');
        cy.get('[data-testid="reports-container"]').should('be.visible');
        cy.get('[data-testid="export-pdf-button"]').should('be.visible');
    });

    it('verifies algo liveness on trading hub', () => {
        cy.visit('/trading');
        cy.get('[data-testid="trading-hub-container"]').should('be.visible');
        cy.get('[data-testid="algo-status"]').should('be.visible');
        cy.get('[data-testid="strategies-heading"]').should('be.visible');
    });
});
