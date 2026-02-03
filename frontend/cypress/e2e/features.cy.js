describe('Feature Availability and Workflow Tests', () => {
    describe('Feature Availability and Workflow Tests', () => {
        it('verifies trading mode visibility and algo liveness', () => {
            cy.login('trader');
            cy.visit('/trading');

            // Check for algo status and mode toggles
            cy.get('[data-testid="algo-status"]').should('be.visible');
            cy.get('[data-testid="mode-toggle-auto"]').scrollIntoView().should('be.visible');
            cy.get('[data-testid="mode-toggle-manual"]').scrollIntoView().should('be.visible');
        });

        it('verifies end-to-end workflow completes without errors', () => {
            cy.login('trader');
            cy.visit('/trading');

            // Toggle to Manual Mode if in Auto (or just click to ensure it's selected)
            cy.get('[data-testid="mode-toggle-manual"]').click();

            // Wait for manual mode to be active (check for active class/color)
            cy.get('[data-testid="mode-toggle-manual"]').should('have.class', 'bg-orange-600');

            // Handle alert
            const alertStub = cy.stub();
            cy.on('window:alert', alertStub);

            // Perform a trading action
            cy.get('[data-testid="manual-order-ticket"]').should('be.visible').within(() => {
                cy.get('input').first().clear().type('RELIANCE');
                cy.get('[data-testid="manual-buy-button"]').click();
            });

            // Assert workflow completes with a success message in the UI or alert
            cy.contains(/successful|success/i, { timeout: 10000 }).should('be.visible');
        });
    });
});
