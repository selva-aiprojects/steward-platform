describe('Feature Availability and Workflow Tests', () => {
    it('verifies trading mode visibility and algo liveness', () => {
        cy.visit('/trading');

        // Check for locked/active/manual modes
        cy.get('[data-mode="locked"]').should('be.visible');
        cy.get('[data-mode="active"]').should('be.visible');
        cy.get('[data-mode="manual"]').should('be.visible');

        // Verify algo liveness indicator pulses
        cy.get('[data-algo-liveness]').should('be.visible');
        cy.get('[data-algo-liveness]').should('have.css', 'animation');
    });

    it('verifies end-to-end workflow completes without errors', () => {
        cy.login('trader');
        cy.visit('/trading');

        // Perform a trading action
        cy.get('[data-user-table] tbody tr:nth-child(1)').click();
        cy.get('[data-eval]').should('exist');

        // Assert workflow completes
        cy.get('[data-workflow-status]').should('contain', 'Completed');
    });
});
