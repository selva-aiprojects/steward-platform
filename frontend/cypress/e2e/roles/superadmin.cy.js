describe('Superadmin Role Tests', () => {
    beforeEach(() => {
        cy.login('admin');
    });

    it('accesses platform executive control', () => {
        cy.visit('/');
        cy.get('[data-testid="dashboard-container"]').should('be.visible');
        cy.contains('Platform Executive Control').should('be.visible');
    });

    it('manages user configurations and isolation', () => {
        cy.visit('/users');
        cy.get('[data-testid="users-container"]', { timeout: 10000 }).should('be.visible');

        // Open management modal for a user
        cy.get('[data-testid="manage-config-button"]').first().should('be.visible').click();
        cy.get('[data-testid="policy-modal"]', { timeout: 10000 }).should('be.visible');

        // Handle alert
        cy.on('window:alert', (str) => {
            expect(str).to.contain('Policy updated successfully');
        });

        // Change policy
        cy.contains('button', 'Manual Override').should('be.visible').click();
        cy.get('textarea').should('be.visible').clear().type('Testing Cypress Policy Update');
        cy.get('[data-testid="confirm-policy-button"]').should('not.be.disabled').click();

        // Modal should close
        cy.get('[data-testid="policy-modal"]').should('not.exist');
    });

    it('verifies multi-tenant scope switching on dashboard', () => {
        cy.visit('/');
        cy.contains('button', 'Platform Summary').click();
        cy.contains('Platform Executive Control').should('be.visible');
        cy.contains('button', 'My Portfolio').click();
        cy.contains('Market Overview').should('be.visible');
    });
});
