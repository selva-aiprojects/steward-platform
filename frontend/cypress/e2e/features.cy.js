describe('Feature Availability and Workflow Tests', () => {
    it('verifies trading mode visibility and algo liveness', () => {
        cy.login('trader');
        cy.visit('/trading');

        // Wait for the page to fully load
        cy.get('[data-testid="trading-hub-container"]').should('be.visible');
        cy.get('h1', { timeout: 10000 }).should('contain.text', 'Trading Hub');

        // Wait for any potential loading indicators to disappear
        cy.get('body').should('not.contain', 'Synchronizing Execution Parameters');

        // Check for algo status and mode toggles
        cy.get('[data-testid="algo-status"]').should('be.visible');
        cy.get('[data-testid="mode-toggle-auto"]').scrollIntoView().should('be.visible');
        cy.get('[data-testid="mode-toggle-manual"]').scrollIntoView().should('be.visible');
    });

    it('verifies end-to-end workflow completes without errors', () => {
        cy.login('trader');
        cy.visit('/trading');

        // Wait for the app data to finish loading
        cy.waitForAppDataLoad();

        // Wait for the main content to be visible
        cy.get('h1', { timeout: 10000 }).should('contain.text', 'Trading Hub');

        // Wait for the trading hub container to be visible
        cy.get('[data-testid="trading-hub-container"]').should('be.visible');

        // Wait for the mode toggle buttons to appear (they might take time to render after data loads)
        cy.get('[data-testid="mode-toggle-manual"]', { timeout: 20000 }).should('be.visible');

        // Toggle to Manual Mode if in Auto (or just click to ensure it's selected)
        // Using .then() to handle potential DOM re-rendering
        cy.get('[data-testid="mode-toggle-manual"]').should('be.visible').then(($el) => {
            // Check if the element has the active class before clicking
            const isActive = $el.hasClass('bg-orange-600');
            if (!isActive) {
                cy.wrap($el).click({ force: true });
                // Wait for the class to update
                cy.get('[data-testid="mode-toggle-manual"]').should('have.class', 'bg-orange-600');
            } else {
                // If already active, just verify it
                cy.get('[data-testid="mode-toggle-manual"]').should('have.class', 'bg-orange-600');
            }
        });

        // Handle alert
        const alertStub = cy.stub();
        cy.on('window:alert', alertStub);

        // Perform a trading action
        cy.get('[data-testid="manual-order-ticket"]').should('be.visible').within(() => {
            cy.get('input').first().should('be.visible').clear().type('RELIANCE');
            // Find the buy button by its text content since the testid might not be correct
            cy.get('button').contains('Buy').click({ force: true });
        });

        // Assert workflow completes with a success message in the UI or alert
        cy.contains(/successful|success/i, { timeout: 10000 }).should('be.visible');
    });
});
