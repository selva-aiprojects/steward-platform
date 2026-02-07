describe('Deposit Workflow Test', () => {
    beforeEach(() => {
        // Mock all API responses to ensure consistent test environment
        cy.intercept('GET', '**/api/v1/users/**', {
            statusCode: 200,
            body: {
                id: 1,
                name: 'Test Trader',
                email: 'trader@stocksteward.ai',
                role: 'TRADER',
                trading_mode: 'AUTO',
                full_name: 'Test Trader'
            }
        }).as('getUser');

        cy.intercept('GET', '**/api/v1/portfolio/**', {
            statusCode: 200,
            body: {
                id: 1,
                user_id: 1,
                name: 'Test Portfolio',
                cash_balance: 100000,
                invested_amount: 50000,
                win_rate: 0.65,
                total_value: 150000
            }
        }).as('getPortfolio');

        cy.intercept('POST', '**/api/v1/portfolio/deposit', {
            statusCode: 200,
            body: {
                id: 1,
                user_id: 1,
                name: 'Test Portfolio',
                cash_balance: 105000, // Increased by deposit amount
                invested_amount: 50000,
                win_rate: 0.65,
                total_value: 155000
            }
        }).as('depositFunds');
    });

    it('should successfully complete the deposit workflow', () => {
        // Visit the portfolio page
        cy.visit('/portfolio');

        // Verify page loaded
        cy.get('h1').should('contain', 'Wealth Vault');

        // Click the deposit button
        cy.contains('Deposit').click();

        // Verify deposit modal appears
        cy.get('.fixed.inset-0').should('be.visible');

        // Enter deposit amount
        cy.get('input[type="number"]').clear().type('5000');

        // Click deposit button in modal
        cy.contains('button', 'Deposit').click();

        // Wait for deposit to complete
        cy.wait('@depositFunds');

        // Verify success message appears
        cy.contains('Successfully deposited INR 5000').should('be.visible');

        // Close modal after successful deposit
        cy.get('button').contains('Cancel').click();

        // Verify the cash balance has updated (would normally refresh)
        cy.contains('INR 105,000').should('exist');
    });

    it('should handle deposit errors gracefully', () => {
        // Intercept deposit to return an error
        cy.intercept('POST', '**/api/v1/portfolio/deposit', {
            statusCode: 500,
            body: { error: 'Deposit failed' }
        }).as('depositFundsError');

        // Visit the portfolio page
        cy.visit('/portfolio');

        // Verify page loaded
        cy.get('h1').should('contain', 'Wealth Vault');

        // Click the deposit button
        cy.contains('Deposit').click();

        // Verify deposit modal appears
        cy.get('.fixed.inset-0').should('be.visible');

        // Enter deposit amount
        cy.get('input[type="number"]').clear().type('5000');

        // Click deposit button in modal
        cy.contains('button', 'Deposit').click();

        // Wait for deposit error
        cy.wait('@depositFundsError');

        // Verify error message appears
        cy.contains('Deposit failed').should('be.visible');
    });
});